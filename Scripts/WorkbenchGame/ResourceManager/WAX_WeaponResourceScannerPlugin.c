#ifdef WORKBENCH

class WAX_WeaponResourceScanner
{
	static const string OUTPUT_ROOT = "$Weapon_ARMA_X:Generated/VanillaWeaponIntelligence";
	static const string PREFAB_ROOT = "$ArmaReforger:Prefabs/Weapons";
	static const string CONFIG_ROOT = "$ArmaReforger:Configs/Weapons";

	protected int m_PrefabDiscovered;
	protected int m_PrefabLoaded;
	protected int m_ConfigDiscovered;
	protected int m_ConfigLoaded;
	protected int m_Failed;

	bool Run()
	{
		m_PrefabDiscovered = 0;
		m_PrefabLoaded = 0;
		m_ConfigDiscovered = 0;
		m_ConfigLoaded = 0;
		m_Failed = 0;

		FileIO.MakeDirectory(OUTPUT_ROOT);

		FileHandle resourcesFile = FileIO.OpenFile(OUTPUT_ROOT + "/resources.tsv", FileMode.WRITE);
		FileHandle componentsFile = FileIO.OpenFile(OUTPUT_ROOT + "/components.tsv", FileMode.WRITE);
		if (!resourcesFile || !componentsFile)
		{
			if (resourcesFile) resourcesFile.Close();
			if (componentsFile) componentsFile.Close();
			Print("[WAX][WEAPON_INTEL] output_open_failed", LogLevel.ERROR);
			return false;
		}

		resourcesFile.WriteLine("kind\tresource_name\tpath\troot_class\tcomponent_count\tload_status");
		componentsFile.WriteLine("resource_name\tpath\tindex\tcomponent_class");

		ScanPrefabs(resourcesFile, componentsFile);
		ScanConfigs(resourcesFile);

		resourcesFile.Close();
		componentsFile.Close();

		WriteManifest();
		WriteReadme();

		PrintFormat(
			"[WAX][WEAPON_INTEL] prefabs=%1 loaded=%2 configs=%3 loaded=%4 failed=%5 output=%6/",
			m_PrefabDiscovered,
			m_PrefabLoaded,
			m_ConfigDiscovered,
			m_ConfigLoaded,
			m_Failed,
			OUTPUT_ROOT);

		return m_Failed == 0;
	}

	protected void ScanPrefabs(FileHandle resourcesFile, FileHandle componentsFile)
	{
		array<ResourceName> resources = SCR_WorkbenchHelper.SearchWorkbenchResources({ "et" }, null, PREFAB_ROOT, true);
		if (!resources)
			return;

		m_PrefabDiscovered = resources.Count();
		foreach (ResourceName resourceName : resources)
		{
			if (resourceName == ResourceName.Empty)
				continue;

			string path = resourceName.GetPath();
			string resourceText = SafeField(string.Format("%1", resourceName));
			Resource resource = Resource.Load(resourceName);
			if (!resource || !resource.IsValid())
			{
				resourcesFile.WriteLine(string.Format("prefab\t%1\t%2\t\t0\tload_failed", resourceText, SafeField(path)));
				m_Failed++;
				continue;
			}

			BaseResourceObject resourceObject = resource.GetResource();
			if (!resourceObject)
			{
				resourcesFile.WriteLine(string.Format("prefab\t%1\t%2\t\t0\tresource_object_missing", resourceText, SafeField(path)));
				m_Failed++;
				continue;
			}

			IEntitySource entitySource = resourceObject.ToEntitySource();
			if (!entitySource)
			{
				resourcesFile.WriteLine(string.Format("prefab\t%1\t%2\t\t0\tnot_entity_source", resourceText, SafeField(path)));
				m_Failed++;
				continue;
			}

			string rootClass = entitySource.GetClassName();
			int componentCount = entitySource.GetComponentCount();
			resourcesFile.WriteLine(string.Format(
				"prefab\t%1\t%2\t%3\t%4\tloaded",
				resourceText,
				SafeField(path),
				SafeField(rootClass),
				componentCount));

			for (int i = 0; i < componentCount; i++)
			{
				IEntityComponentSource componentSource = entitySource.GetComponent(i);
				string componentClass;
				if (componentSource)
					componentClass = componentSource.GetClassName();
				componentsFile.WriteLine(string.Format(
					"%1\t%2\t%3\t%4",
					resourceText,
					SafeField(path),
					i,
					SafeField(componentClass)));
			}

			m_PrefabLoaded++;
		}
	}

	protected void ScanConfigs(FileHandle resourcesFile)
	{
		array<ResourceName> resources = SCR_WorkbenchHelper.SearchWorkbenchResources({ "conf" }, null, CONFIG_ROOT, true);
		if (!resources)
			return;

		m_ConfigDiscovered = resources.Count();
		foreach (ResourceName resourceName : resources)
		{
			if (resourceName == ResourceName.Empty)
				continue;

			string path = resourceName.GetPath();
			string resourceText = SafeField(string.Format("%1", resourceName));
			Resource resource = Resource.Load(resourceName);
			if (!resource || !resource.IsValid())
			{
				resourcesFile.WriteLine(string.Format("config\t%1\t%2\t\t0\tload_failed", resourceText, SafeField(path)));
				m_Failed++;
				continue;
			}

			BaseResourceObject resourceObject = resource.GetResource();
			if (!resourceObject)
			{
				resourcesFile.WriteLine(string.Format("config\t%1\t%2\t\t0\tresource_object_missing", resourceText, SafeField(path)));
				m_Failed++;
				continue;
			}

			BaseContainer container = resourceObject.ToBaseContainer();
			if (!container)
			{
				resourcesFile.WriteLine(string.Format("config\t%1\t%2\t\t0\tbase_container_unavailable", resourceText, SafeField(path)));
				m_Failed++;
				continue;
			}

			resourcesFile.WriteLine(string.Format(
				"config\t%1\t%2\t%3\t0\tloaded",
				resourceText,
				SafeField(path),
				SafeField(container.GetClassName())));
			m_ConfigLoaded++;
		}
	}

	protected void WriteManifest()
	{
		FileHandle file = FileIO.OpenFile(OUTPUT_ROOT + "/manifest.tsv", FileMode.WRITE);
		if (!file)
			return;

		file.WriteLine("key\tvalue");
		file.WriteLine("format\tWAX_VANILLA_WEAPON_INTELLIGENCE_V1");
		file.WriteLine("authority\tArmaReforger base-game mounted resources");
		file.WriteLine(string.Format("prefab_root\t%1", PREFAB_ROOT));
		file.WriteLine(string.Format("config_root\t%1", CONFIG_ROOT));
		file.WriteLine(string.Format("prefabs_discovered\t%1", m_PrefabDiscovered));
		file.WriteLine(string.Format("prefabs_loaded\t%1", m_PrefabLoaded));
		file.WriteLine(string.Format("configs_discovered\t%1", m_ConfigDiscovered));
		file.WriteLine(string.Format("configs_loaded\t%1", m_ConfigLoaded));
		file.WriteLine(string.Format("failed\t%1", m_Failed));
		file.WriteLine("source_mutation\tnone");
		file.Close();
	}

	protected void WriteReadme()
	{
		FileHandle file = FileIO.OpenFile(OUTPUT_ROOT + "/README.md", FileMode.WRITE);
		if (!file)
			return;

		file.WriteLine("# Weapon ARMA X — Vanilla Weapon Intelligence V1");
		file.WriteLine("");
		file.WriteLine("Generated inside Arma Reforger Workbench from mounted base-game resources.");
		file.WriteLine("");
		file.WriteLine("This first pass records registered resource identity, root classes and top-level prefab components. It does not modify base-game resources and does not claim full property/inheritance resolution yet.");
		file.WriteLine("");
		file.WriteLine("Files:");
		file.WriteLine("- resources.tsv — registered vanilla weapon prefab/config inventory");
		file.WriteLine("- components.tsv — top-level IEntitySource component classes for .et prefabs");
		file.WriteLine("- manifest.tsv — scan roots and counts");
		file.Close();
	}

	protected string SafeField(string value)
	{
		string safe = value;
		safe.Replace("\t", " ");
		safe.Replace("\r", " ");
		safe.Replace("\n", " ");
		return safe;
	}
}

[WorkbenchPluginAttribute(
	name: "WAX: Scan Vanilla Weapon Resources",
	description: "Scan mounted Arma Reforger base-game weapon prefabs and configs into local derived metadata.",
	wbModules: { "ResourceManager" },
	category: "Weapon ARMA X")]
class WAX_WeaponResourceScannerPlugin : ResourceManagerPlugin
{
	override void Run()
	{
		WAX_WeaponResourceScanner scanner = new WAX_WeaponResourceScanner();
		bool ok = scanner.Run();
		if (ok)
			SCR_WorkbenchHelper.PrintDialog("Vanilla weapon resource scan completed. See Generated/VanillaWeaponIntelligence.", "Weapon ARMA X", LogLevel.NORMAL);
		else
			SCR_WorkbenchHelper.PrintDialog("Vanilla weapon resource scan completed with failures. See Output Console and Generated/VanillaWeaponIntelligence.", "Weapon ARMA X", LogLevel.WARNING);
	}
}

#endif
