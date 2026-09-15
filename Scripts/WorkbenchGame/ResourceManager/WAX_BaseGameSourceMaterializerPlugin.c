#ifdef WORKBENCH

// Exact/manual vanilla source materializer for offline resolver evidence.
//
// This utility intentionally does not scan the weapon tree or the whole game.
// It materializes only explicitly selected $ArmaReforger .et/.conf resources,
// preserves vanilla-relative paths, appends result rows to the authoritative
// manifest, and does not register generated copies back into Resource Manager.
// Registration is unnecessary for the Python resolver and can create sidecars
// or Workbench churn.

[WorkbenchPluginAttribute(
	name: "WAX: Materialize Selected Vanilla Sources",
	description: "Materialize only explicitly selected base-game .et/.conf resources into Imported/VanillaSources for offline resolver evidence.",
	wbModules: { "ResourceManager" },
	resourceTypes: { "et", "conf" },
	category: "Weapon ARMA X")]
class WAX_BaseGameSourceMaterializerPlugin : ResourceManagerPlugin
{
	protected static const string DESTINATION_ROOT = "$Weapon_ARMA_X:Imported/VanillaSources";
	protected static const string BASE_GAME_ROOT = "$ArmaReforger:";
	protected static const string MANIFEST_NAME = "_wax_materialization.tsv";

	protected ref array<string> m_SourcePaths;
	protected ref array<ResourceName> m_SourceResources;

	override void Run()
	{
		ResourceManager resourceManager = Workbench.GetModule(ResourceManager);
		if (!resourceManager)
		{
			Print("[WAX][MATERIALIZE] Resource Manager unavailable", LogLevel.ERROR);
			return;
		}

		ResetSources();
		resourceManager.GetResourceBrowserSelection(OnSelectionItem, true);

		if (m_SourcePaths.IsEmpty())
		{
			Print("[WAX][MATERIALIZE] Select one or more $ArmaReforger: .et/.conf resources first.", LogLevel.WARNING);
			return;
		}

		MaterializeCollected("selection");
	}

	protected void ResetSources()
	{
		m_SourcePaths = {};
		m_SourceResources = {};
	}

	protected bool AddBaseGameResource(ResourceName resourceName)
	{
		if (resourceName == ResourceName.Empty)
			return false;

		string relativePath = resourceName.GetPath();
		if (relativePath == "")
			return false;

		if (!relativePath.EndsWith(".et") && !relativePath.EndsWith(".ET") && !relativePath.EndsWith(".conf") && !relativePath.EndsWith(".CONF"))
			return false;

		string sourcePath = BASE_GAME_ROOT + relativePath;
		if (m_SourcePaths.Find(sourcePath) >= 0)
			return false;

		m_SourcePaths.Insert(sourcePath);
		m_SourceResources.Insert(resourceName);
		return true;
	}

	protected FileHandle OpenManifest(string manifestAbsolute)
	{
		FileHandle manifest;
		if (FileIO.FileExists(manifestAbsolute))
		{
			manifest = FileIO.OpenFile(manifestAbsolute, FileMode.APPEND);
		}
		else
		{
			manifest = FileIO.OpenFile(manifestAbsolute, FileMode.WRITE);
			if (manifest)
				manifest.WriteLine("source\tdestination_relative\tmethod\tcontainer_class\tstatus");
		}
		return manifest;
	}

	protected void MaterializeCollected(string mode)
	{
		string destinationRootAbsolute;
		if (!Workbench.GetAbsolutePath(DESTINATION_ROOT, destinationRootAbsolute, false))
		{
			PrintFormat("[WAX][MATERIALIZE] cannot_resolve_destination=%1", DESTINATION_ROOT, level: LogLevel.ERROR);
			return;
		}

		if (!FileIO.MakeDirectory(destinationRootAbsolute))
		{
			PrintFormat("[WAX][MATERIALIZE] cannot_create_destination=%1", destinationRootAbsolute, level: LogLevel.ERROR);
			return;
		}

		string manifestAbsolute = FilePath.Concat(destinationRootAbsolute, MANIFEST_NAME);
		FileHandle manifest = OpenManifest(manifestAbsolute);
		if (!manifest)
		{
			PrintFormat("[WAX][MATERIALIZE] cannot_open_manifest=%1", manifestAbsolute, level: LogLevel.ERROR);
			return;
		}

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
				PrintFormat("[WAX][MATERIALIZE] INVALID_SOURCE source=%1", sourcePath, level: LogLevel.WARNING);
				failed++;
				continue;
			}

			string destinationAbsolute = FilePath.Concat(destinationRootAbsolute, relativePath);
			string destinationDirectory = FilePath.StripFileName(destinationAbsolute);
			if (!FileIO.MakeDirectory(destinationDirectory))
			{
				PrintFormat("[WAX][MATERIALIZE] MKDIR_FAIL destination=%1", destinationDirectory, level: LogLevel.WARNING);
				manifest.WriteLine(string.Format("%1\t%2\t\t\tmkdir_failed", SafeField(sourcePath), SafeField(relativePath)));
				failed++;
				continue;
			}

			string method;
			string containerClass;
			if (!Materialize(sourcePath, sourceResource, destinationAbsolute, method, containerClass))
			{
				PrintFormat("[WAX][MATERIALIZE] FAIL source=%1 method=%2 class=%3", sourcePath, method, containerClass, level: LogLevel.WARNING);
				manifest.WriteLine(string.Format("%1\t%2\t%3\t%4\tfailed", SafeField(sourcePath), SafeField(relativePath), SafeField(method), SafeField(containerClass)));
				failed++;
				continue;
			}

			if (method == "physical")
				physical++;
			if (method == "container")
				container++;

			manifest.WriteLine(string.Format("%1\t%2\t%3\t%4\tok", SafeField(sourcePath), SafeField(relativePath), SafeField(method), SafeField(containerClass)));
			copied++;
		}

		manifest.Close();

		PrintFormat(
			"[WAX][MATERIALIZE] DONE mode=%1 inputs=%2 copied=%3 physical=%4 container=%5 failed=%6 root=%7",
			mode,
			m_SourcePaths.Count(),
			copied,
			physical,
			container,
			failed,
			DESTINATION_ROOT);
	}

	protected bool ToBaseGameRelativePath(string sourcePath, out string relativePath)
	{
		relativePath = sourcePath;
		if (sourcePath.IndexOf(BASE_GAME_ROOT) != 0)
			return false;

		relativePath.Replace(BASE_GAME_ROOT, "");
		relativePath.Replace("\\", "/");
		return relativePath != "";
	}

	protected bool Materialize(
		string sourcePath,
		ResourceName sourceResourceName,
		string destinationAbsolute,
		out string method,
		out string containerClass)
	{
		method = "physical_unavailable";
		containerClass = "";

		string sourceAbsolute;
		if (Workbench.GetAbsolutePath(sourcePath, sourceAbsolute, true))
		{
			if (!CopySourceFile(sourceAbsolute, destinationAbsolute))
			{
				method = "physical_copy_failed";
				return false;
			}
			method = "physical";
			return true;
		}

		method = "container_load_failed";
		Resource sourceResource = Resource.Load(sourceResourceName);
		if (!sourceResource || !sourceResource.IsValid())
			return false;

		method = "container_resource_object_missing";
		BaseResourceObject resourceObject = sourceResource.GetResource();
		if (!resourceObject)
			return false;

		method = "container_base_container_missing";
		BaseContainer sourceContainer = resourceObject.ToBaseContainer();
		if (!sourceContainer)
			return false;

		containerClass = sourceContainer.GetClassName();
		method = "container_save_failed";
		if (!BaseContainerTools.SaveContainer(sourceContainer, ResourceName.Empty, destinationAbsolute))
			return false;

		if (!FileIO.FileExists(destinationAbsolute))
		{
			method = "container_file_missing";
			return false;
		}

		method = "container";
		return true;
	}

	protected bool CopySourceFile(string sourceAbsolute, string destinationAbsolute)
	{
		FileHandle sourceFile = FileIO.OpenFile(sourceAbsolute, FileMode.READ);
		if (!sourceFile)
			return false;

		int sourceLength = sourceFile.GetLength();
		string sourceData;
		int readBytes = sourceFile.Read(sourceData, sourceLength);
		sourceFile.Close();
		if (readBytes != sourceLength)
			return false;

		FileHandle destinationFile = FileIO.OpenFile(destinationAbsolute, FileMode.WRITE);
		if (!destinationFile)
			return false;

		int writtenBytes = destinationFile.Write(sourceData, readBytes);
		destinationFile.Close();
		return writtenBytes == readBytes;
	}

	protected string SafeField(string value)
	{
		string safe = value;
		safe.Replace("\t", " ");
		safe.Replace("\r", " ");
		safe.Replace("\n", " ");
		return safe;
	}

	protected void OnSelectionItem(ResourceName resourceName, string filePath = "")
	{
		if (resourceName == ResourceName.Empty)
			return;

		string sourcePath = filePath;
		if (sourcePath == "" || sourcePath.IndexOf(BASE_GAME_ROOT) != 0)
		{
			if (sourcePath != "")
				PrintFormat("[WAX][MATERIALIZE] SKIP_NON_BASE_GAME source=%1", sourcePath);
			return;
		}

		if (!sourcePath.EndsWith(".et") && !sourcePath.EndsWith(".ET") && !sourcePath.EndsWith(".conf") && !sourcePath.EndsWith(".CONF"))
			return;

		if (m_SourcePaths.Find(sourcePath) >= 0)
			return;

		m_SourcePaths.Insert(sourcePath);
		m_SourceResources.Insert(resourceName);
	}
}

#endif
