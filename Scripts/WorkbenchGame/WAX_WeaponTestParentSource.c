// Fixed-path read-only source export for the isolated Weapon_test parent.
// No writes, registration, world loading or editor mutation.
class WAX_WeaponTestParentSourceResponse : JsonApiStruct
{
	string worldStatus;
	string worldText;
	string layerStatus;
	string layerText;
	string autoSpawnStatus;
	string autoSpawnText;
	ref array<string> spawnResources = new array<string>();
	void WAX_WeaponTestParentSourceResponse()
	{
		RegV("worldStatus"); RegV("worldText"); RegV("layerStatus"); RegV("layerText");
		RegV("autoSpawnStatus"); RegV("autoSpawnText"); RegV("spawnResources");
	}
}
class WAX_WeaponTestParentSource : NetApiHandler
{
	protected ref array<string> m_Resources;
	protected string ReadSource(string path, out string status)
	{
		FileHandle handle = FileIO.OpenFile(path, FileMode.READ);
		if (!handle) { status = "not-readable"; return ""; }
		int length = handle.GetLength();
		if (length < 1 || length > 262144)
		{
			handle.Close(); status = "size-rejected"; return "";
		}
		string data;
		int count = handle.Read(data, length);
		handle.Close();
		if (count != length) { status = "short-read"; return ""; }
		status = "read";
		return data;
	}
	protected void OnSpawnResource(string fileName, FileAttribute attributes = 0, string filesystem = "")
	{
		if (m_Resources.Count() < 64)
			m_Resources.Insert(fileName);
	}
	override JsonApiStruct GetRequest() { return new WAX_ReadOnlyNetRequest(); }
	override JsonApiStruct GetResponse(JsonApiStruct request)
	{
		WAX_WeaponTestParentSourceResponse response = new WAX_WeaponTestParentSourceResponse();
		response.worldText = ReadSource("$ArmaReforger:worlds/Tests/TestFramework/Autotest_GameMode_Plain.ent", response.worldStatus);
		response.layerText = ReadSource("$ArmaReforger:worlds/Tests/TestFramework/Autotest_GameMode_Plain_Layers/default.layer", response.layerStatus);
		response.autoSpawnText = ReadSource("$ArmaReforger:Scripts/Game/Respawn/Logic/SCR_AutoSpawnLogic.c", response.autoSpawnStatus);
		m_Resources = response.spawnResources;
		FileIO.FindFiles(OnSpawnResource, "$ArmaReforger:Prefabs/MP/Spawning", ".et");
		return response;
	}
}
