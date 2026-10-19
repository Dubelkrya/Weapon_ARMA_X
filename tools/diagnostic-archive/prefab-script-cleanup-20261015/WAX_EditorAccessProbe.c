// Temporary read-only diagnostic: 12 samples, five seconds apart.
// No rights changes, RPC, editor mutations or ammo writes.
modded class SCR_PlayerController
{
	protected float m_WAXAccessElapsed;
	protected int m_WAXAccessSamples;
	override void OnUpdate(float timeSlice)
	{
		super.OnUpdate(timeSlice);
		if (m_WAXAccessSamples >= 12) return;
		bool authority = Replication.IsServer();
		bool owner = GetGame().GetPlayerController() == this;
		if (!authority && !owner) return;
		m_WAXAccessElapsed += timeSlice;
		if (m_WAXAccessElapsed < 5) return;
		m_WAXAccessElapsed = 0;
		m_WAXAccessSamples++;
		int playerId = GetPlayerId();
		PlayerManager players = GetGame().GetPlayerManager();
		if (!players) return;
		string environment = "CLIENT";
#ifdef WORKBENCH
		environment = "WORKBENCH";
#endif
		PrintFormat("[WAX-EDITOR-ACCESS] env=%1 server=%2 owner=%3 sample=%4 player=%5 roles=%6 admin=%7",
			environment, authority, owner, m_WAXAccessSamples, playerId,
			players.GetPlayerRoles(playerId), SCR_Global.IsAdmin(playerId));
		SCR_EditorManagerEntity manager;
		if (authority)
		{
			SCR_EditorManagerCore core = SCR_EditorManagerCore.Cast(SCR_EditorManagerCore.GetInstance(SCR_EditorManagerCore));
			if (core) manager = core.GetEditorManager(playerId);
		}
		else manager = SCR_EditorManagerEntity.GetInstance();
		if (manager)
			PrintFormat("[WAX-EDITOR-ACCESS] player=%1 manager=present canOpen=%2 limited=%3 opened=%4 allowedModes=%5 registeredModes=%6 currentMode=%7",
				playerId, manager.CanOpen(), manager.IsLimited(), manager.IsOpened(),
				manager.GetEditorModes(), manager.GetModes(), manager.GetCurrentMode());
		else PrintFormat("[WAX-EDITOR-ACCESS] player=%1 manager=absent", playerId);
		SCR_EditorSettingsEntity settings = SCR_EditorSettingsEntity.GetInstance();
		if (settings)
			PrintFormat("[WAX-EDITOR-ACCESS] settings=present disabled=%1 unlimitedLegal=%2 baseOverride=%3",
				settings.IsEditorDisabled(), settings.IsUnlimitedEditorLegal(), settings.IsBaseOverrideEnabled());
		else Print("[WAX-EDITOR-ACCESS] settings=absent");
	}
}
