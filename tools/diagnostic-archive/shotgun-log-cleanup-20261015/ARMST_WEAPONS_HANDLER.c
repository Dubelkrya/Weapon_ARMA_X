class ARMST_12g_SpreadEffect : BaseProjectileEffect
{
	[Attribute("", UIWidgets.ResourceNamePicker, "Pellet prefab", "et")]
	ResourceName m_sPelletPrefab;

	[Attribute("12")]
	int m_iPelletCount;

	[Attribute("1.0")]
	float m_fSpreadAngle;

	// Must match InitSpeed in the pellet prefab; converts carrier velocity to Launch coefficient.
	[Attribute("404")]
	float m_fPelletReferenceSpeed;

	// Experimental horizon from observed launch-to-self-hit timing; not an engine timestep.
	[Attribute("0.03")]
	float m_fMotionCompensationSeconds;

	override void OnEffect(IEntity pHitEntity, inout vector outMat[3], IEntity damageSource, notnull Instigator instigator, string colliderName, float speed)
	{
		if (m_sPelletPrefab == "" || m_iPelletCount <= 0 || m_fPelletReferenceSpeed <= 0) return;

		Resource res = Resource.Load(m_sPelletPrefab);
		if (!res) return;
		
		IEntity gunner = instigator.GetInstigatorEntity();
		float speedCoef = 1.0;
		if (speed > 0)
			speedCoef = speed / m_fPelletReferenceSpeed;
		vector gunnerVelocity = vector.Zero;
		if (gunner)
		{
			Physics gunnerPhysics = gunner.GetPhysics();
			if (gunnerPhysics)
				gunnerVelocity = gunnerPhysics.GetVelocity();
		}
		IEntity diagnosticWeapon;
		if (gunner)
		{
			BaseWeaponManagerComponent diagnosticManager = BaseWeaponManagerComponent.Cast(gunner.FindComponent(BaseWeaponManagerComponent));
			if (diagnosticManager)
			{
				BaseWeaponComponent diagnosticCurrent = diagnosticManager.GetCurrentWeapon();
				if (diagnosticCurrent)
					diagnosticWeapon = diagnosticCurrent.GetOwner();
			}
		}
		vector pelletSpawnPosition = outMat[0];
		if (diagnosticWeapon && m_fMotionCompensationSeconds > 0 && vector.Dot(gunnerVelocity, outMat[1]) > 0)
		{
			vector proposedPosition = pelletSpawnPosition + gunnerVelocity * m_fMotionCompensationSeconds;
			ref array<IEntity> excluded = new array<IEntity>();
			if (gunner)
				excluded.Insert(gunner);
			excluded.Insert(diagnosticWeapon);
			if (damageSource)
				excluded.Insert(damageSource);
			TraceSphere clearance = new TraceSphere();
			clearance.Start = pelletSpawnPosition;
			clearance.End = proposedPosition;
			clearance.Radius = 0.00415; // Half the authored 8.3 mm pellet diameter.
			clearance.Flags = TraceFlags.WORLD | TraceFlags.ENTS;
			clearance.LayerMask = EPhysicsLayerPresets.Projectile;
			clearance.ExcludeArray = excluded;
			float clearanceFraction = GetGame().GetWorld().TraceMove(clearance, null);
			// Never move a pellet past a detected obstacle. Fall back to the original launch.
			if (clearanceFraction >= 1 && !clearance.TraceEnt)
				pelletSpawnPosition = proposedPosition;
		}
		for (int i = 0; i < m_iPelletCount; i++)
		{
			vector dir = GetRandomSpread(outMat[1], m_fSpreadAngle);
			vector tm[4];
			Math3D.DirectionAndUpMatrix(dir, vector.Up, tm);
			tm[3] = pelletSpawnPosition;

			EntitySpawnParams params = EntitySpawnParams();
			params.TransformMode = ETransformMode.WORLD;
			params.Transform = tm;

			IEntity pellet = GetGame().SpawnEntityPrefab(res, GetGame().GetWorld(), params);
			if (!pellet) continue;

			ProjectileMoveComponent move = ProjectileMoveComponent.Cast(pellet.FindComponent(ProjectileMoveComponent));
			if (!move)
			{
				SCR_EntityHelper.DeleteEntityAndChildren(pellet);
				continue;
			}

			move.Launch(dir, vector.Zero, speedCoef, pellet, gunner, gunner, null, null);
			move.SetInstigator(instigator);
		}
	}

	vector GetRandomSpread(vector forward, float angleDeg)
	{
		vector ang = forward.VectorToAngles();

		float degToRad = 0.017453292519943295;
		float angleDir = Math.RandomFloat(0, 360);
		float radius = Math.Sqrt(Math.RandomFloat(0, 1)) * angleDeg;
		float offsetYaw = Math.Cos(angleDir * degToRad) * radius;
		float offsetPitch = Math.Sin(angleDir * degToRad) * radius;
		float yaw = ang[0] + offsetYaw;
		float pitch = ang[1] + offsetPitch;
	
		return Vector(yaw, pitch, 0).AnglesToVector().Normalized();
	}
}

// Compatibility stub for saved test-world instances; no diagnostic work.
class ARMST_BuckshotHitDiagnostic : BaseProjectileEffect
{
}

class ARMST_SHOTGUN_COMPONENTSClass : ScriptComponentClass
{
};
[BaseContainerProps()]
class ARMST_SHOTGUN_COMPONENTS : ScriptComponent
{
	[Attribute("2", UIWidgets.Slider, "Макс. патронов в магазине", "1 20 1")]
	int m_MaxMagazineAmmo;
}
modded class SCR_MuzzleEffectComponent : MuzzleEffectComponent
{
	
	
	
}

modded class SCR_WeaponInfo : SCR_InfoDisplayExtended
{
	
	
	override void OnAmmoCountChanged(BaseWeaponComponent weapon, BaseMuzzleComponent muzzle, BaseMagazineComponent magazine, int ammoCount, bool isBarrelChambered)
	{
        super.OnAmmoCountChanged(weapon,muzzle,magazine,ammoCount,isBarrelChambered);

        IEntity Wepon = weapon.GetOwner();
        if(Wepon)
		{
			
		   IEntity controlledEnt = SCR_PlayerController.GetLocalControlledEntity();
			if(!controlledEnt)
				return;
	        ChimeraCharacter character = ChimeraCharacter.Cast(controlledEnt);
	        PlayerController player = GetGame().GetPlayerController();
	        SCR_CharacterControllerComponent controller2 = SCR_CharacterControllerComponent.Cast(character.GetCharacterController());
	        controller2.RequestWeaponHandler(player.GetPlayerId());
			
	        ARMST_ITEMS_STATS_COMPONENTS m_ArmstStat_vest = ARMST_ITEMS_STATS_COMPONENTS.Cast(Wepon.FindComponent(ARMST_ITEMS_STATS_COMPONENTS));
	        if (m_ArmstStat_vest)
	        {
	            int conditionLevel = m_ArmstStat_vest.GetConditionLevel();
	            
	            if (conditionLevel < 70)
	            {
	                // Вычисляем шанс срабатывания: чем ниже состояние, тем выше шанс
	                // Например, при conditionLevel = 70 шанс = 0%, при conditionLevel = 0 шанс = 70%
	                float jamChance = (60 - conditionLevel) * 1.0; // Шанс увеличивается на 1% за каждую единицу состояния ниже 70
	                float randomRoll = Math.RandomFloat(0, 150);
	                
	                if (randomRoll <= jamChance)
	                {
	                    controller2.OnRackBoltMDown();
        				SCR_PlayerController controller3 = SCR_PlayerController.Cast(GetGame().GetPlayerController());
						controller3.RpcDo_AmmoCount("#armst_weapon_rack");
	                   // Print(string.Format("[SCR_WeaponInfo] Weapon jam triggered! Condition: %1, Chance: %2, Roll: %3", conditionLevel, jamChance, randomRoll), LogLevel.NORMAL);
	                }
	            }
	        }
		}
	}	
}

modded class SCR_CharacterControllerComponent
{
	protected CharacterAnimationComponent m_animComp;
	protected int m_WAXRackTraceLines;

	protected void WAXRackTrace(string phase)
	{
		if (m_WAXRackTraceLines >= 64)
			return;
		m_WAXRackTraceLines++;
		int ammo = -1;
		int chambered = -1;
		BaseWeaponManagerComponent manager = GetWeaponManagerComponent();
		if (manager && manager.GetCurrentWeapon())
		{
			BaseWeaponComponent weapon = manager.GetCurrentWeapon();
			BaseMagazineComponent magazine = weapon.GetCurrentMagazine();
			BaseMuzzleComponent muzzle = weapon.GetCurrentMuzzle();
			if (magazine)
				ammo = magazine.GetAmmoCount();
			if (muzzle)
			{
				chambered = 0;
				if (muzzle.IsCurrentBarrelChambered())
					chambered = 1;
			}
		}
		PrintFormat("[WAX-CORE-RACK] server=%1 phase=%2 ammo=%3 chambered=%4", Replication.IsServer(), phase, ammo, chambered);
	}

	// --- AnimEvent hook ---
	protected ref ScriptInvoker<AnimationEventID, AnimationEventID, int, float, float, SCR_CharacterControllerComponent> m_OnAnimEvt_LocalHook;
	protected AnimationEventID m_EvtRackBolt_Underscore; // "Weapon_Rack_Bolt"

	// --- Flags (serveur) ---
	protected bool m_ServerManualRackPending;   // SERVER: en attente de l'AnimEvent pour traiter
	protected bool m_ServerFallbackRunning;     // SERVER: CallLater en cours ?
	protected bool m_ServerRackCooldownActive;  // SERVER: petit cooldown anti-spam

	// --- Filet anti-spam côté client ---
	protected bool m_ClientRackCooldownActive;
	protected const float TAO_CLIENT_COOLDOWN_MS = 220.0; // ~ durée mini d’un cycle bolt

	// Fallback si l’AnimEvent serveur n’arrive pas
	protected int  m_ServerProcessRetryCount;
	protected const int   TAO_SERVER_RETRY_MAX   = 6;      // ~6 frames
	protected const float TAO_SERVER_RETRY_DELAY = 0.03;   // 30 ms

	// Cooldown serveur (empêche plusieurs racks pendant spam)
	protected const float TAO_SERVER_COOLDOWN_MS = 220.0;

	// ----------------------------------------------------------
	override void OnInit(IEntity owner)
	{
		super.OnInit(owner);

		m_animComp = GetAnimationComponent();

		// ID de l'AnimEvent
		m_EvtRackBolt_Underscore = GameAnimationUtils.RegisterAnimationEvent("Weapon_Rack_Bolt");

		// Abonnement à l’AnimEvent (client + serveur)
		ScriptInvoker onAnim = GetOnAnimationEvent();
		if (onAnim)
		{
			m_OnAnimEvt_LocalHook = onAnim;
			onAnim.Insert(OnAnimEvent_RackBoltCaseEject);
		}
	}

	// ----------------------------------------------------------
	override protected void OnReloaded(IEntity owner, BaseWeaponComponent weapon)
	{
		super.OnReloaded(owner, weapon);
		// Print("[TAO] OnReloaded: done (auto-rack vanilla si rack sans input)", LogLevel.NORMAL);
	}

	// ----------------------------------------------------------
	// AnimEvent callback (CLIENT + SERVER)
	// ----------------------------------------------------------
	protected void OnAnimEvent_RackBoltCaseEject(
		AnimationEventID animEventType,
		AnimationEventID animUserString,
		int intParam,
		float timeFromStart,
		float timeToEnd,
		SCR_CharacterControllerComponent controller)
	{
		if (animEventType != m_EvtRackBolt_Underscore)
			return;
		WAXRackTrace("rack-animation-event");

		ChimeraCharacter ch = GetCharacter();
		if (!ch) return;

		RplComponent rpl = ch.GetRplComponent();
		bool isMaster = (rpl && rpl.IsMaster());

		if (isMaster)
		{
			// ====== SERVEUR ======
			// Print(string.Format("[TAO][SV] RackBolt AnimEvent: pending=%1 cooldown=%2 reloading=%3",
			// 	m_ServerManualRackPending, m_ServerRackCooldownActive, IsReloading()), LogLevel.NORMAL);

			if (m_ServerManualRackPending && !m_ServerRackCooldownActive)
			{
				// Traitement autoritaire au moment exact du rack
				TAO_DecrementAmmoOnRack();
				TAO_ClearChamberIfNoMagOrEmpty();

				// Consommer la demande + poser un cooldown
				m_ServerManualRackPending   = false;
				m_ServerProcessRetryCount   = 0;
				m_ServerRackCooldownActive  = true;
				// Print("[TAO][SV] RackBolt: MANUAL processed at AnimEvent -> cooldown start", LogLevel.NORMAL);
				GetGame().GetCallqueue().CallLater(TAO_ServerCooldownOff, TAO_SERVER_COOLDOWN_MS, false);

				// Stopper le fallback si en cours
				if (m_ServerFallbackRunning)
				{
					m_ServerFallbackRunning = false;
					GetGame().GetCallqueue().Remove(TAO_ServerProcessManualRack_Fallback);
				}
			}
			else
			{
				// Print("[TAO][SV] RackBolt: skipped (auto/cooldown/no pending)", LogLevel.NORMAL);
			}
		}
		else
		{
			// ====== CLIENT ======
			// Print(string.Format("[TAO][CL] RackBolt AnimEvent -> clear local cooldown (was=%1)", m_ClientRackCooldownActive), LogLevel.NORMAL);
			// Déverrouille le cooldown client dès que l'event local passe
			if (m_ClientRackCooldownActive)
			{
				m_ClientRackCooldownActive = false;
			}
		}
	}

	// ----------------------------------------------------------
	// RPC Client->Serveur : demande de rack manuel (debounce serveur)
	// ----------------------------------------------------------
	[RplRpc(RplChannel.Reliable, RplRcver.Server)]
	protected void RpcAsk_TAO_ManualRack()
	{
		WAXRackTrace("manual-rack-rpc-received");
		// Refuse si déjà en attente, en cooldown, ou si une anim de reload est en cours côté serveur
		if (m_ServerManualRackPending || m_ServerRackCooldownActive || IsReloading())
		{
			WAXRackTrace("manual-rack-rpc-rejected");
			// Print(string.Format("[TAO][RPC->SV] Manual rack IGNORED (pending=%1 cooldown=%2 reloading=%3)",
			// 	m_ServerManualRackPending, m_ServerRackCooldownActive, IsReloading()), LogLevel.WARNING);
			return;
		}

		m_ServerManualRackPending  = true;
		WAXRackTrace("manual-rack-rpc-accepted");
		m_ServerProcessRetryCount  = 0;
		// Print("[TAO][RPC->SV] Manual rack accepted: pending=true", LogLevel.NORMAL);

		// Lancer le fallback si pas déjà en cours
		if (!m_ServerFallbackRunning)
		{
			m_ServerFallbackRunning = true;
			GetGame().GetCallqueue().CallLater(TAO_ServerProcessManualRack_Fallback, TAO_SERVER_RETRY_DELAY, true);
		}
	}

	// Fallback serveur: retente quelques frames si l’AnimEvent ne s’est pas produit
	protected void TAO_ServerProcessManualRack_Fallback()
	{
		// Arrêt si déjà traité, cooldown actif, ou si on est en plein reload serveur
		if (!m_ServerManualRackPending || m_ServerRackCooldownActive || IsReloading())
		{
			m_ServerFallbackRunning = false;
			GetGame().GetCallqueue().Remove(TAO_ServerProcessManualRack_Fallback);
			return;
		}

		m_ServerProcessRetryCount++;
		// Print(string.Format("[TAO][SV][FB] Try %1/%2", m_ServerProcessRetryCount, TAO_SERVER_RETRY_MAX), LogLevel.NORMAL);

		if (m_ServerProcessRetryCount >= TAO_SERVER_RETRY_MAX)
		{
			WAXRackTrace("fallback-processing");
			// Print("[TAO][SV][FB] No AnimEvent -> force manual processing now", LogLevel.WARNING);
			TAO_DecrementAmmoOnRack();
			TAO_ClearChamberIfNoMagOrEmpty();

			m_ServerManualRackPending  = false;
			m_ServerProcessRetryCount  = 0;
			m_ServerFallbackRunning    = false;

			// Cooldown après traitement forcé
			m_ServerRackCooldownActive = true;
			GetGame().GetCallqueue().Remove(TAO_ServerProcessManualRack_Fallback);
			GetGame().GetCallqueue().CallLater(TAO_ServerCooldownOff, TAO_SERVER_COOLDOWN_MS, false);
		}
	}

	protected void TAO_ServerCooldownOff()
	{
		m_ServerRackCooldownActive = false;
		// Print("[TAO][SV] Cooldown off", LogLevel.NORMAL);
	}

	// ----------------------------------------------------------
	// Décrémentation (SERVEUR uniquement)
	// ----------------------------------------------------------
	protected void TAO_DecrementAmmoOnRack()
	{
		WAXRackTrace("decrement-enter");
		BaseWeaponManagerComponent wm = GetWeaponManagerComponent();
		if (!wm) {  return; }

		BaseWeaponComponent wpn = wm.GetCurrentWeapon();
		if (!wpn) { return; }

		BaseMuzzleComponent muzzle = wpn.GetCurrentMuzzle();
		if (!muzzle) { return; }

		BaseMagazineComponent mag = wpn.GetCurrentMagazine();
		if (!mag) { return; }

		int count = mag.GetAmmoCount();
		if (count <= 0) {  return; }

		mag.SetAmmoCount(Math.Max(count - 1, 0));
		WAXRackTrace("decrement-after");
		// Print(string.Format("[TAO][SV] Decr: ammo %1 -> %2", count, Math.Max(count - 1, 0)), LogLevel.NORMAL);
	}

	// ----------------------------------------------------------
	// Clear chamber si pas de mag / mag vide (SERVEUR uniquement)
	// ----------------------------------------------------------
	void TAO_ClearChamberIfNoMagOrEmpty()
	{
		BaseWeaponManagerComponent wm = GetWeaponManagerComponent();
		if (!wm) {  return; }

		BaseWeaponComponent wpn = wm.GetCurrentWeapon();
		if (!wpn) {  return; }

		BaseMuzzleComponent muzzle = wpn.GetCurrentMuzzle();
		if (!muzzle) {  return; }

		BaseMagazineComponent mag = wpn.GetCurrentMagazine();
		bool noMagOrEmpty = true;
		if (mag && mag.GetAmmoCount() > 0) noMagOrEmpty = false;

		if (!noMagOrEmpty)
		{
			
			return;
		}

		if (!muzzle.IsCurrentBarrelChambered())
		{
			
			return;
		}

		int curIdx = muzzle.GetCurrentBarrelIndex();
		bool ok = muzzle.ClearChamber(curIdx);
		// Print(string.Format("[TAO][SV] Clear: ClearChamber(%1) -> %2", curIdx, ok), LogLevel.NORMAL);
	}

	// ----------------------------------------------------------
	// INPUT (CLIENT)
	// ----------------------------------------------------------
	void OnRackBoltMDown(float value = 0.0, EActionTrigger reason = 0)
	{
		WAXRackTrace("manual-input-enter");
		if (!m_animComp) return;

		CharacterCommandHandlerComponent cmdHandler = m_animComp.GetCommandHandler();
		if (!cmdHandler) return;

		CharacterControllerComponent controller = cmdHandler.GetControllerComponent();
		if (!controller) return;

		CharacterInputContext inputCtx = controller.GetInputContext();
		if (!inputCtx) return;

		// Anti-spam côté client : ne pas relancer si reload/rack en cours
		if (IsReloading())
		{
			// Print("[TAO][CL] Input ignored: character IsReloading()", LogLevel.WARNING);
			return;
		}
		// Petit cooldown client (filet de sécurité)
		if (m_ClientRackCooldownActive)
		{
			// Print("[TAO][CL] Input ignored: local cooldown active", LogLevel.WARNING);
			return;
		}
		m_ClientRackCooldownActive = true;
		GetGame().GetCallqueue().CallLater(TAO_ClientCooldownOff, TAO_CLIENT_COOLDOWN_MS, false);

		// CLIENT : envoyer la demande ; le serveur dédupliquera
		// Print("[TAO][CL] Input: manual rack -> RPC ask", LogLevel.NORMAL);
		Rpc(RpcAsk_TAO_ManualRack);

		// Déclenche l’anim qui émettra l’AnimEvent (solo & multi)
		inputCtx.SetReloadWeapon(1); // ReloadType = 83
	}

	protected void TAO_ClientCooldownOff()
	{
		m_ClientRackCooldownActive = false;
		// Print("[TAO][CL] Local cooldown off", LogLevel.NORMAL);
	}
	
	// Клиент → сервер
	void RequestWeaponHandler(int playerId)
	{
	    if (Replication.IsServer())
	    {
	        WeaponHandler(playerId);
	    }
	    else
	    {
	        Rpc(RpcAsk_WeaponHandler, playerId);
	    }
	}
	
	[RplRpc(RplChannel.Reliable, RplRcver.Server)]
	protected void RpcAsk_WeaponHandler(int playerId)
	{
	    SCR_PlayerController scrPlayerController = SCR_PlayerController.Cast(GetGame().GetPlayerManager().GetPlayerController(playerId));
	    if (!scrPlayerController) return;
	
	    IEntity player = scrPlayerController.GetMainEntity();
	    if (!player) return;
	
	    WeaponHandler(playerId);
	}
	
    protected vector m_aOriginalTransform[4];
	float conditionDamageModifier = 0;
	int max_mag = 0;
	void WeaponHandler(int playerId)
	{
	    if (!Replication.IsServer()) return;
	
	    SCR_PlayerController scrPlayerController = SCR_PlayerController.Cast(GetGame().GetPlayerManager().GetPlayerController(playerId));
		if(!scrPlayerController)
			return;
	    IEntity user = scrPlayerController.GetMainEntity();
		
	    BaseGameMode gameMode = BaseGameMode.Cast(GetGame().GetGameMode());
	    if (gameMode)
	        {
		        // Получаем компонент глобальных настроек ARMST_EDITOR_GLOBAL_SETTINGS
		        ARMST_EDITOR_GLOBAL_SETTINGS Settings = ARMST_EDITOR_GLOBAL_SETTINGS.Cast(gameMode.FindComponent(ARMST_EDITOR_GLOBAL_SETTINGS));
		        if (Settings)
		        {
					conditionDamageModifier = Settings.m_WeaponDamageConditionLevel;
				}
			}
			else 
			{
				return;	
			}

		
		BaseWeaponManagerComponent weaponManager = GetWeaponManagerComponent();
		if (!weaponManager) {  return; }

		BaseWeaponComponent weaponManager2 = weaponManager.GetCurrentWeapon();
		if (!weaponManager2) {  return; }
		
		IEntity wpn =  weaponManager2.GetOwner();
			if(wpn)
			{
			            ARMST_ITEMS_STATS_COMPONENTS m_ArmstStat_wpn = ARMST_ITEMS_STATS_COMPONENTS.Cast(wpn.FindComponent(ARMST_ITEMS_STATS_COMPONENTS));
			            if (m_ArmstStat_wpn)
							{
			        		 		m_ArmstStat_wpn.DecreaseCondition(conditionDamageModifier);
							}
						ARMST_SHOTGUN_COMPONENTS m_shotgun = ARMST_SHOTGUN_COMPONENTS.Cast(wpn.FindComponent(ARMST_SHOTGUN_COMPONENTS));
						if(m_shotgun)
							{
				                BaseMagazineComponent currentMagazine = weaponManager2.GetCurrentMagazine();
				                 if (currentMagazine)
				                     {
				                                IEntity magazineEntity = currentMagazine.GetOwner();
				                                ResourceName resourceName = magazineEntity.GetPrefabData().GetPrefabName();
												int Capacity = m_shotgun.m_MaxMagazineAmmo;
										        int maxCapacity = Capacity;
										        if (maxCapacity <= 0)
										            return;
													
										        // Текущее количество патронов в магазине
										        int currentAmmo = currentMagazine.GetAmmoCount();
										        if (currentAmmo < maxCapacity)
										            return; // Всё в порядке
									
										        // === ОБРЕЗАЕМ МАГАЗИН ===
										        int excessAmmo = currentAmmo - maxCapacity;
										
										        // Устанавливаем максимум в текущий магазин
										        currentMagazine.SetAmmoCount(maxCapacity);
										        		Resource resource = Resource.Load(resourceName);
										        if (!resource)
										            return;
										
							                    vector transform[4];
							                    SCR_TerrainHelper.GetTerrainBasis(user.GetOrigin(), transform, GetGame().GetWorld(), false, new TraceParam());
							
							                    m_aOriginalTransform = transform;
							
							                    EntitySpawnParams params = new EntitySpawnParams();
							                    params.Transform = m_aOriginalTransform;
							                    params.TransformMode = ETransformMode.WORLD;
										
					
										        IEntity newMagazine = GetGame().SpawnEntityPrefab(resource, GetGame().GetWorld(), params);
										        if (!newMagazine)
										            return;
					
										        MagazineComponent newMag = MagazineComponent.Cast(newMagazine.FindComponent(MagazineComponent));
										        if (newMag)
										        {
										            newMag.SetAmmoCount(excessAmmo);
										        }
										
										        SCR_InventoryStorageManagerComponent inventory = SCR_InventoryStorageManagerComponent.Cast(user.FindComponent(SCR_InventoryStorageManagerComponent));
										        if (!inventory)
										            return;
												float ammo_last =  newMag.GetAmmoCount();
												if(ammo_last < 1)
													{
														SCR_EntityHelper.DeleteEntityAndChildren(newMagazine);
														return;
													}
					
				                                	inventory.TryInsertItem(newMagazine);
										        // Кладём в инвентарь
										        if (!inventory.TryInsertItem(newMagazine))
										        {
										            // Если не влез — падает рядом с игроком
										            vector pos = user.GetOrigin();
										            SCR_EntityHelper.SnapToGround(newMagazine);
										        }
													
									}
							}
			}
		
	}
	
}
