#ifdef WORKBENCH

[WorkbenchPluginAttribute(
	name: "WAX: Materialize Selected Vanilla Sources",
	description: "Materialize selected base-game .et/.conf resources into this addon for local inspection. Uses physical copy first, then BaseContainer serialization when supported.",
	wbModules: { "ResourceManager" },
	resourceTypes: { "et", "conf" },
	category: "Weapon ARMA X")]
class WAX_BaseGameSourceMaterializerPlugin : ResourceManagerPlugin
{
	protected static const string DESTINATION_ROOT = "$Weapon_ARMA_X:Imported/VanillaSources";
	protected static const string BASE_GAME_ROOT = "$ArmaReforger:";

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

		m_SourcePaths = {};
		m_SourceResources = {};
		resourceManager.GetResourceBrowserSelection(OnSelectionItem, true);

		if (m_SourcePaths.IsEmpty())
		{
			SCR_WorkbenchHelper.PrintDialog(
				"Select one or more $ArmaReforger: .et/.conf resources in Resource Manager first.",
				"Weapon ARMA X",
				LogLevel.WARNING);
			return;
		}

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

		int copied = 0;
		int physical = 0;
		int container = 0;
		int failed = 0;

		for (int i = 0; i < m_SourcePaths.Count(); i++)
		{
			string sourcePath = m_SourcePaths[i];
			ResourceName sourceResource = m_SourceResources[i];
			string sourceFileName = FilePath.StripPath(sourcePath);
			string outputFileName = (i + 1).ToString(4) + "_" + sourceFileName;
			string destinationAbsolute = FilePath.Concat(destinationRootAbsolute, outputFileName);

			string method;
			string containerClass;
			if (!Materialize(sourcePath, sourceResource, destinationAbsolute, method, containerClass))
			{
				PrintFormat(
					"[WAX][MATERIALIZE] FAIL source=%1 method=%2 class=%3",
					sourcePath,
					method,
					containerClass,
					level: LogLevel.WARNING);
				failed++;
				continue;
			}

			if (method == "physical") physical++;
			if (method == "container") container++;

			if (!resourceManager.RegisterResourceFile(destinationAbsolute, false))
			{
				PrintFormat("[WAX][MATERIALIZE] REGISTER_FAIL file=%1", destinationAbsolute, level: LogLevel.WARNING);
				failed++;
				continue;
			}

			PrintFormat(
				"[WAX][MATERIALIZE] COPIED source=%1 method=%2 class=%3 destination=%4",
				sourcePath,
				method,
				containerClass,
				destinationAbsolute);
			copied++;
		}

		PrintFormat(
			"[WAX][MATERIALIZE] summary selected=%1 copied=%2 physical=%3 container=%4 failed=%5",
			m_SourcePaths.Count(),
			copied,
			physical,
			container,
			failed);

		LogLevel dialogLevel = LogLevel.NORMAL;
		if (failed > 0)
			dialogLevel = LogLevel.WARNING;

		SCR_WorkbenchHelper.PrintFormatDialog(
			"Materialization finished. Selected: %1, copied: %2, failed: %3. Packed resources that cannot serialize should be staged with Workbench 'Duplicate to addon'.",
			m_SourcePaths.Count().ToString(),
			copied.ToString(),
			failed.ToString(),
			"Weapon ARMA X",
			dialogLevel);
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

	protected void OnSelectionItem(ResourceName resourceName, string filePath = "")
	{
		if (resourceName == ResourceName.Empty)
			return;

		// Resource Manager callback filePath is expected in $Addon:Path/To/File.ext format.
		// V1 deliberately rejects every mount except the vanilla ArmaReforger mount.
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
