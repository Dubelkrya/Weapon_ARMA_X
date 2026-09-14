#ifdef WORKBENCH

// Raw source snapshot exporter for architecture analysis.
//
// This plugin deliberately does not interpret weapon architecture. It only
// materializes mounted base-game text resources into Weapon_ARMA_X so an
// external/local agent can parse them later. Raw snapshot files remain local
// and gitignored under Imported/VanillaSources.
//
// Supported source kinds are intentionally text/architecture oriented:
//   .et      entity/prefab source
//   .conf    reusable configuration source
//   .c       Enfusion script source when Workbench exposes a physical source
//   .layout  UI/layout source when Workbench exposes a physical source
//
// .et/.conf retain the existing container fallback from
// WAX_BaseGameSourceMaterializerPlugin when no physical source file exists.

[WorkbenchPluginAttribute(
	name: "WAX: Export Full Vanilla Source Snapshot",
	description: "Export mounted vanilla .et/.conf/.c/.layout sources into Imported/VanillaSources for offline architecture analysis. Raw snapshot stays local/gitignored.",
	wbModules: { "ResourceManager" },
	category: "Weapon ARMA X")]
class WAX_BaseGameFullSnapshotExporterPlugin : WAX_BaseGameSourceMaterializerPlugin
{
	protected bool IsSnapshotTextResource(string relativePath)
	{
		return relativePath.EndsWith(".et")
			|| relativePath.EndsWith(".ET")
			|| relativePath.EndsWith(".conf")
			|| relativePath.EndsWith(".CONF")
			|| relativePath.EndsWith(".c")
			|| relativePath.EndsWith(".C")
			|| relativePath.EndsWith(".layout")
			|| relativePath.EndsWith(".LAYOUT");
	}

	protected bool AddSnapshotResource(ResourceName resourceName)
	{
		if (resourceName == ResourceName.Empty)
			return false;

		string relativePath = resourceName.GetPath();
		if (relativePath == "" || !IsSnapshotTextResource(relativePath))
			return false;

		string sourcePath = BASE_GAME_ROOT + relativePath;
		if (m_SourcePaths.Find(sourcePath) >= 0)
			return false;

		m_SourcePaths.Insert(sourcePath);
		m_SourceResources.Insert(resourceName);
		return true;
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

		array<ResourceName> resources = SCR_WorkbenchHelper.SearchWorkbenchResources(
			{ "et", "conf", "c", "layout" },
			null,
			BASE_GAME_ROOT,
			true);

		if (resources)
		{
			foreach (ResourceName resourceName : resources)
				AddSnapshotResource(resourceName);
		}

		if (m_SourcePaths.IsEmpty())
		{
			SCR_WorkbenchHelper.PrintDialog(
				"No mounted vanilla .et/.conf/.c/.layout resources were discovered under $ArmaReforger:.",
				"Weapon ARMA X",
				LogLevel.WARNING);
			return;
		}

		PrintFormat(
			"[WAX][SNAPSHOT] discovered=%1 root=%2",
			m_SourcePaths.Count(),
			BASE_GAME_ROOT);

		MaterializeCollected(resourceManager, "full_source_snapshot");
	}
}

#endif
