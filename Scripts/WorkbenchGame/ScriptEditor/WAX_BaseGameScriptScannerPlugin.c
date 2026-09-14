#ifdef WORKBENCH

class WAX_BaseGameScriptScanner
{
	static const string SOURCE_ROOT = "scripts/";
	static const string SOURCE_EXTENSION = ".c";
	static const string OUTPUT_ROOT = "$Weapon_ARMA_X:Generated/BaseGameScripts";

	protected int m_Discovered;
	protected int m_Read;
	protected int m_Unreadable;
	protected int m_TotalLines;

	bool Run()
	{
		m_Discovered = 0;
		m_Read = 0;
		m_Unreadable = 0;
		m_TotalLines = 0;

		array<string> scriptFiles = {};
		bool discoveryOk = FileIO.FindFiles(scriptFiles.Insert, SOURCE_ROOT, SOURCE_EXTENSION);
		m_Discovered = scriptFiles.Count();
		if (!discoveryOk || m_Discovered == 0)
		{
			Print("[WAX][SCRIPT_INTEL] no_scripts_discovered", LogLevel.ERROR);
			return false;
		}

		SortStrings(scriptFiles);
		FileIO.MakeDirectory(OUTPUT_ROOT);
		FileHandle filesOut = FileIO.OpenFile(OUTPUT_ROOT + "/files.tsv", FileMode.WRITE);
		if (!filesOut)
			return false;

		filesOut.WriteLine("path\tlines\tread_status");
		foreach (string scriptPath : scriptFiles)
			ScanFile(scriptPath, filesOut);
		filesOut.Close();

		WriteManifest();
		WriteReadme();

		PrintFormat(
			"[WAX][SCRIPT_INTEL] discovered=%1 read=%2 unreadable=%3 lines=%4 output=%5/",
			m_Discovered,
			m_Read,
			m_Unreadable,
			m_TotalLines,
			OUTPUT_ROOT);
		return m_Unreadable == 0;
	}

	protected void ScanFile(string scriptPath, FileHandle filesOut)
	{
		FileHandle file = FileIO.OpenFile(scriptPath, FileMode.READ);
		if (!file)
		{
			filesOut.WriteLine(string.Format("%1\t0\tunreadable", SafeField(scriptPath)));
			m_Unreadable++;
			return;
		}

		int lines = 0;
		string line;
		while (file.ReadLine(line) >= 0)
			lines++;
		file.Close();

		m_Read++;
		m_TotalLines += lines;
		filesOut.WriteLine(string.Format("%1\t%2\tread", SafeField(scriptPath), lines));
	}

	protected void WriteManifest()
	{
		FileHandle file = FileIO.OpenFile(OUTPUT_ROOT + "/manifest.tsv", FileMode.WRITE);
		if (!file)
			return;

		file.WriteLine("key\tvalue");
		file.WriteLine("format\tWAX_BASE_GAME_SCRIPTS_V1");
		file.WriteLine(string.Format("source_root\t%1", SOURCE_ROOT));
		file.WriteLine(string.Format("source_extension\t%1", SOURCE_EXTENSION));
		file.WriteLine(string.Format("discovered\t%1", m_Discovered));
		file.WriteLine(string.Format("read\t%1", m_Read));
		file.WriteLine(string.Format("unreadable\t%1", m_Unreadable));
		file.WriteLine(string.Format("total_lines\t%1", m_TotalLines));
		file.WriteLine("source_mirror\tno");
		file.Close();
	}

	protected void WriteReadme()
	{
		FileHandle file = FileIO.OpenFile(OUTPUT_ROOT + "/README.md", FileMode.WRITE);
		if (!file)
			return;

		file.WriteLine("# Weapon ARMA X — Base Game Script Visibility");
		file.WriteLine("");
		file.WriteLine("This scanner proves Workbench-visible `.c` access using the same `FileIO.FindFiles(\"scripts/\", \".c\")` architecture previously validated by RWTK Code Intelligence.");
		file.WriteLine("");
		file.WriteLine("V1 writes only derived file/line metadata; it does not copy vanilla source bodies into this repository.");
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

	protected void SortStrings(notnull array<string> values)
	{
		int count = values.Count();
		for (int i = 1; i < count; i++)
		{
			string current = values[i];
			int j = i - 1;
			while (j >= 0 && values[j].Compare(current) > 0)
			{
				values[j + 1] = values[j];
				j--;
			}
			values[j + 1] = current;
		}
	}
}

[WorkbenchPluginAttribute(
	name: "WAX: Scan Base Game Scripts",
	description: "Index Workbench-visible Arma Reforger .c scripts without copying source bodies.",
	wbModules: { "ScriptEditor" },
	category: "Weapon ARMA X")]
class WAX_BaseGameScriptScannerPlugin : ScriptEditorPlugin
{
	override void Run()
	{
		WAX_BaseGameScriptScanner scanner = new WAX_BaseGameScriptScanner();
		bool ok = scanner.Run();
		if (ok)
			SCR_WorkbenchHelper.PrintDialog("Base-game script scan completed. See Generated/BaseGameScripts.", "Weapon ARMA X", LogLevel.NORMAL);
		else
			SCR_WorkbenchHelper.PrintDialog("Base-game script scan failed or found unreadable files. See Output Console.", "Weapon ARMA X", LogLevel.WARNING);
	}
}

#endif
