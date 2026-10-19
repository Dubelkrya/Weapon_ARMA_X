// Intentional editor mutation, separate from the read-only API.
// Operates ONLY on the saved local parent in ARMSTPLATFORMWeapons.
class WAX_ConfigureLocalSpawnResponse : JsonApiStruct
{
	string status;
	bool saved;
	void WAX_ConfigureLocalSpawnResponse() { RegV("status"); RegV("saved"); }
}
class WAX_ConfigureLocalSpawn : NetApiHandler
{
	override JsonApiStruct GetRequest() { return new WAX_ReadOnlyNetRequest(); }
	override JsonApiStruct GetResponse(JsonApiStruct request)
	{
		WAX_ConfigureLocalSpawnResponse reply = new WAX_ConfigureLocalSpawnResponse();
		WAX_ReadOnlyNetRequest req = WAX_ReadOnlyNetRequest.Cast(request);
		if (!req || req.nonce != "configure-local-parent") { reply.status = "confirmation-required"; return reply; }
		WorldEditor editor = Workbench.GetModule(WorldEditor);
		if (!editor) { reply.status = "no-editor"; return reply; }
		WorldEditorAPI api = editor.GetApi();
		if (!api) { reply.status = "no-editor-api"; return reply; }
		string world;
		api.GetWorldPath(world);
		if (world != "$ARMSTPLATFORMWeapons:worlds/Tests/TestFramework/Autotest_GameMode_Plain.ent")
		{ reply.status = "open-local-parent-not-vanilla"; return reply; }
		int scene = api.GetCurrentSubScene();
		IEntitySource mode;
		int modeCount;
		for (int i = 0; i < api.GetEntityCount(scene); i++)
		{
			IEntitySource entity = api.GetEntity(scene, i);
			if (entity && entity.GetClassName() == "SCR_BaseGameMode")
			{ mode = entity; modeCount++; }
		}
		if (modeCount != 1 || !mode || mode.GetSubScene() != scene)
		{ reply.status = "expected-one-local-gamemode"; return reply; }
		int respawnIndex = -1;
		for (int c = 0; c < mode.GetComponentCount(); c++)
			if (mode.GetComponent(c).GetClassName() == "SCR_RespawnSystemComponent") respawnIndex = c;
		if (respawnIndex < 0) { reply.status = "no-respawn"; return reply; }
		ResourceName spawnPrefab = Workbench.GetResourceName("$ArmaReforger:Prefabs/MP/Spawning/SpawnPoint_FFA.et");
		Resource spawnResource = Resource.Load(spawnPrefab);
		if (spawnPrefab == ResourceName.Empty || !spawnResource || !spawnResource.IsValid())
		{ reply.status = "spawn-prefab-unresolved"; return reply; }
		array<ref ContainerIdPathEntry> respawnPath = {new ContainerIdPathEntry("components", respawnIndex)};
		array<ref ContainerIdPathEntry> logicPath = {new ContainerIdPathEntry("components", respawnIndex), new ContainerIdPathEntry("m_SpawnLogic")};
		if (!api.BeginEntityAction("Weapon test local auto spawn"))
		{ reply.status = "cannot-begin-edit"; return reply; }
		bool ok = api.ChangeObjectClass(mode, logicPath, "SCR_AutoSpawnLogic");
		if (ok) ok = api.SetVariableValue(mode, respawnPath, "m_bEnableRespawn", "1");
		if (ok) ok = api.SetVariableValue(mode, logicPath, "m_sForcedFaction", "FFA");
		if (ok) ok = api.SetVariableValue(mode, logicPath, "m_sForcedLoadout", "#AR-Role_Rifleman");
		// Authored placement: 3m in front of the first existing desk at 130.664/77.997.
		// Height is queried from terrain rather than guessed.
		IEntitySource point = api.FindEntityByName("WAX_WeaponTestSpawn");
		if (ok && !point)
		{
			vector position = Vector(130.664, api.GetTerrainSurfaceY(130.664, 74.997) + 0.1, 74.997);
			point = api.CreateEntity(spawnPrefab, "WAX_WeaponTestSpawn", mode.GetLayerID(), null, position, vector.Zero);
			ok = point != null;
		}
		api.EndEntityAction("Weapon test local auto spawn");
		if (!ok) { reply.status = "edit-failed-unsaved-use-undo"; return reply; }
		reply.saved = editor.Save();
		reply.status = "configured-check-runtime";
		return reply;
	}
}
