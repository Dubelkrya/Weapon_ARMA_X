#ifdef WORKBENCH

// Weapon-scoped raw source snapshot exporter for offline architecture analysis.
//
// This plugin deliberately does NOT scan/export the whole game. It materializes
// only vanilla resources that are useful for weapon architecture:
//   - Prefabs/Weapons: .et + .conf
//   - Configs/Weapons: .conf
//   - weapon-related script sources under Scripts/Game: .c
//
// Raw files are written under Imported/VanillaSources, remain gitignored, and
// are NOT registered back into Resource Manager. Registration is unnecessary
// for the local Python agent and can cause Workbench churn/reload prompts.
// All status is written to Log Console/manifest; this plugin shows no popups.

[WorkbenchPluginAttribute(
	name: "WAX: Export Vanilla Weapon Source Snapshot",
	description: "Export vanilla weapon prefabs/configs plus weapon-related scripts into Imported/VanillaSources for offline architecture analysis. Does not scan/export the whole game.",
	wbModules: { "ResourceManager" },
	category: "Weapon ARMA X")]
class WAX_BaseGameFullSnapshotExporterPlugin : WAX_BaseGameSourceMaterializerPlugin
{
	protected static const string SCRIPT_GAME_ROOT = "$ArmaReforger:Scripts/Game";
	protected int m_ScriptSourceCount;

	protected bool IsWeaponScriptPath(string relativePath)
	{
		// Keep these as simple statements. Enfusion Workbench can reject one
		// large boolean expression here with "Formula too complex".
		if (relativePath.IndexOf("Weapon") >= 0) return true;
		if (relativePath.IndexOf("weapon") >= 0) return true;
		if (relativePath.IndexOf("Magazine") >= 0) return true;
		if (relativePath.IndexOf("magazine") >= 0) return true;
		if (relativePath.IndexOf("Ammo") >= 0) return true;
		if (relativePath.IndexOf("ammo") >= 0) return true;
		if (relativePath.IndexOf("Projectile") >= 0) return true;
		if (relativePath.IndexOf("projectile") >= 0) return true;
		if (relativePath.IndexOf("Muzzle") >= 0) return true;
		if (relativePath.IndexOf("muzzle") >= 0) return true;
		if (relativePath.IndexOf("Recoil") >= 0) return true;
		if (relativePath.IndexOf("recoil") >= 0) return true;
		if (relativePath.IndexOf("FireMode") >= 0) return true;
		if (relativePath.IndexOf("firemode") >= 0) return true;
		if (relativePath.IndexOf("Attachment") >= 0) return true;
		if (relativePath.IndexOf("attachment") >= 0) return true;
		if (relativePath.IndexOf("Optic") >= 0) return true;
		if (relativePath.IndexOf("optic") >= 0) return true;
		return false;
	}

	protected bool AddSnapshotResource(ResourceName resourceName)
	{
		if (resourceName == ResourceName.Empty)
			return false;

		string relativePath = resourceName.GetPath();
		if (relativePath == "")
			return false;

		string sourcePath = BASE_GAME_ROOT + relativePath;
		if (m_SourcePaths.Find(sourcePath) >= 0)
			return false;

		m_SourcePaths.Insert(sourcePath);
		m_SourceResources.Insert(resourceName);
		return true;
	}

	protected bool AddSnapshotScriptFile(string sourcePath)
	{
		if (sourcePath == "")
			return false;

		string normalizedPath = sourcePath;
		normalizedPath.Replace("\\", "/");
		if (normalizedPath.IndexOf(BASE_GAME_ROOT) != 0)
			return false;

		string relativePath = normalizedPath;
		relativePath.Replace(BASE_GAME_ROOT, "");
		if (!relativePath.EndsWith(".c") && !relativePath.EndsWith(".C"))
			return false;
		if (!IsWeaponScriptPath(relativePath))
			return false;
		if (m_SourcePaths.Find(normalizedPath) >= 0)
			return false;

		// Script files are not registered resources. Keep an empty ResourceName;
		// Materialize() will first try the physical Workbench path and copy it.
		m_SourcePaths.Insert(normalizedPath);
		m_SourceResources.Insert(ResourceName.Empty);
		m_ScriptSourceCount++;
		return true;
	}

	protected void CollectWeaponDataset()
	{
		array<ResourceName> prefabResources = SCR_WorkbenchHelper.SearchWorkbenchResources(
			{ "et", "conf" },
			null,
			PREFAB_ROOT,
			true);
		if (prefabResources)
		{
			foreach (ResourceName resourceName : prefabResources)
				AddSnapshotResource(resourceName);
		}

		array<ResourceName> weaponConfigs = SCR_WorkbenchHelper.SearchWorkbenchResources(
			{ "conf" },
			null,
			CONFIG_ROOT,
			true);
		if (weaponConfigs)
		{
			foreach (ResourceName resourceName : weaponConfigs)
				AddSnapshotResource(resourceName);
		}

		// Scripts are not ResourceDB resources. SearchWorkbenchFiles is the
		// supported API and returns Workbench file paths such as
		// $ArmaReforger:Scripts/Game/.../SomeWeaponScript.c.
		array<string> scriptFiles = SCR_WorkbenchHelper.SearchWorkbenchFiles(
			{ "c" },
			null,
			SCRIPT_GAME_ROOT,
			true);
		if (scriptFiles)
		{
			foreach (string scriptPath : scriptFiles)
				AddSnapshotScriptFile(scriptPath);
		}
	}

	protected void MaterializeSnapshotWithoutRegistration(string mode)
	{
		string destinationRootAbsolute;
		if (!Workbench.GetAbsolutePath(DESTINATION_ROOT, destinationRootAbsolute, false))
		{
			PrintFormat("[WAX][SNAPSHOT] cannot_resolve_destination=%1", DESTINATION_ROOT, level: LogLevel.ERROR);
			return;
		}

		if (!FileIO.MakeDirectory(destinationRootAbsolute))
		{
			PrintFormat("[WAX][SNAPSHOT] cannot_create_destination=%1", destinationRootAbsolute, level: LogLevel.ERROR);
			return;
		}

		string manifestAbsolute = FilePath.Concat(destinationRootAbsolute, MANIFEST_NAME);
		FileHandle manifest = FileIO.OpenFile(manifestAbsolute, FileMode.WRITE);
		if (manifest)
			manifest.WriteLine("source\tdestination_relative\tmethod\tcontainer_class\tstatus");

		int copied = 0;
		int physical = 0;
		int container = 0;
		int failed = 0;

		for (int i = 0; i < m_SourcePaths.Count(); i++)
		{
			string sourcePath = m_SourcePaths[i];
			ResourceName sourceResource = m_SourceResources[i];
			string relativePath;
			if (!ToBaseGameRelativePath(sourcePath, relativePath))
			{
				failed++;
				if (manifest)
					manifest.WriteLine(string.Format("%1\t\t\t\tinvalid_source", SafeField(sourcePath)));
				continue;
			}

			string destinationAbsolute = FilePath.Concat(destinationRootAbsolute, relativePath);
			string destinationDirectory = FilePath.StripFileName(destinationAbsolute);
			if (!FileIO.MakeDirectory(destinationDirectory))
			{
				failed++;
				if (manifest)
					manifest.WriteLine(string.Format("%1\t%2\t\t\tmkdir_failed", SafeField(sourcePath), SafeField(relativePath)));
				continue;
			}

			string method;
			string containerClass;
			if (!Materialize(sourcePath, sourceResource, destinationAbsolute, method, containerClass))
			{
				failed++;
				if (manifest)
					manifest.WriteLine(string.Format("%1\t%2\t%3\t%4\tfailed", SafeField(sourcePath), SafeField(relativePath), SafeField(method), SafeField(containerClass)));
				continue;
			}

			if (method == "physical")
				physical++;
			if (method == "container")
				container++;

			if (manifest)
				manifest.WriteLine(string.Format("%1\t%2\t%3\t%4\tok", SafeField(sourcePath), SafeField(relativePath), SafeField(method), SafeField(containerClass)));
			copied++;
		}

		if (manifest)
			manifest.Close();

		PrintFormat(
			"[WAX][SNAPSHOT] DONE mode=%1 inputs=%2 scripts=%3 copied=%4 physical=%5 container=%6 failed=%7 root=%8",
			mode,
			m_SourcePaths.Count(),
			m_ScriptSourceCount,
			copied,
			physical,
			container,
			failed,
			DESTINATION_ROOT);
	}

	override void Run()
	{
		ResourceManager resourceManager = Workbench.GetModule(ResourceManager);
		if (!resourceManager)
		{
			Print("[WAX][SNAPSHOT] Resource Manager unavailable", LogLevel.ERROR);
			return;
		}

		ResetSources();
		m_ScriptSourceCount = 0;
		CollectWeaponDataset();

		if (m_SourcePaths.IsEmpty())
		{
			Print("[WAX][SNAPSHOT] No mounted vanilla weapon prefab/config/script resources were discovered.", LogLevel.WARNING);
			return;
		}

		PrintFormat(
			"[WAX][SNAPSHOT] discovered=%1 scripts=%2 scope=weapon_only",
			m_SourcePaths.Count(),
			m_ScriptSourceCount);
		MaterializeSnapshotWithoutRegistration("weapon_source_snapshot");
	}
}

#endif
