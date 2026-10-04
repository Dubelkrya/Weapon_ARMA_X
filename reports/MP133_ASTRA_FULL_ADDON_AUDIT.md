# MP-133 Astra: аудит аддона и исправление новой копии

Статус: **WORKSPACE_REPAIRED_ANIMATION_GATE**, не ENGINE_SAFE_RELOAD_SOURCE_READY.
Задание: [Issue #34, 5984204617](https://github.com/Dubelkrya/Weapon_ARMA_X/issues/34#issuecomment-5984204617). База ветки t4b/installed-mag-probe: `8b472163202f738440d95aeef979d499faf34643`.

**Результат:** изменены реальные пять авторских файлов новой копии Workspace. Исправлен потерянный Group Select досылки, удалены назначения магазинных клипов и ложное подключение shell-цикла к CMD2–6. Пять фаз доступны как отдельный анимационный узел для проверки, но намеренно не подключены к игровому R. Доказанного безопасного соединения R → injected graph в разрешённой области нет; запись патронов не добавлена. Ограничение относится к исследованному интерфейсу и текущему scope, а не доказывает принципиальную невозможность в движке.

## 1. Источники и полный состав лаборатории

Live: `C:\Users\yshky\Documents\My Games\ArmaReforgerWorkbench\addons\ARMSTMP133T4B_InstalledMagProbe`.
Project ID ARMSTMP133T4BInstalledMag, GUID B1C2D3E4F5061728. Зависимости base 58D0FB3206B6F859 и Weapons 6A70E400C54051DC. Установленный Workbench executable: версия **1.8.0.13**. Игра/редактор не запускались; владелец подтвердил закрытие всех редакторов и отсутствие другого исполнителя.

Инвентаризированы 108 файлов live-аддона: все Prefabs/Test, пять скриптов Game, исходный и новый Workspace, импортированные анимации/метаданные и вспомогательные ресурсы. Текущие W3 и G3B2 отличаются от старых отчётов: W3 снова имеет полную структуру, G3B2 теперь повторяемый после завершения отложенных проверок. Старые утверждения про повреждённый W3/строго одноразовый G3B2 неприменимы к этой базе.

| Файл / узел | Фактическая роль и вывод |
|---|---|
| Scripts/Game/ARMST_T4B/ARMST_T4B_InstalledMagProbe.c | WeaponAnimationComponent вызывает super и пишет native event/command trace. Probe НЕ полностью пассивен: T4BTryBaseline вызывает SetAmmoCount(start). Отдельный AddRound action делает синтетический +1; новый fixture его не содержит. |
| ARMST_T4B_G3B1_DonorConsume.c | Отдельное историческое действие donor−1. Не является backend цикла Astra. |
| ARMST_T4B_G3B2_Transfer.c | Server-only action; два последовательных setter, identity/type/storage/capacity/chamber guards. Latch ставится до donor setter. Ошибка после записи → quarantine. Текущий код снимает latch только после подтверждённых 250ms/1000ms snapshots одного operation ID. Нет атомарной транзакции или автоматического rollback. |
| ARMST_T4B_AstraV2_WeaponAnimationComponent.c | Согласованный с owner compile logging bridge; lazy initialization вместо ранее отвергнутого конструктора. W marker создаёт только diagnostic_candidate_no_transfer. Нет авторитетного session/cycle token, inventory writer или input arbitration. |
| ARMST_T4B_AstraRequestProbe.c | Старый эксперимент BindVariableBool на player_main.agr. Провал привязки подтверждён логом. Новый fixture не содержит действия, повторно оно не подключается. |
| ARMST_T4B_AstraRebuild_TestWeapon.et | Прямой потомок production MP-133, один nested bridge, Tube3 и probe start2. Нет дополнительных действий. `.et.meta` по-прежнему отсутствует: регистрация владельцем обязательна. |
| Старые W3/G4A/G3B2/Bridge/TestWeapon/DonorDevice | Независимые fixtures, их действия не наследуются новым prefab. Исходники не изменены; наличие в аддоне не делает их активным маршрутом нового оружия. |

Цепь нового prefab: `armst_Shotgun_mp_133.et` GUID63FF6FDCA4E7E735 → `armst_shotgun_base.et` GUID6C5E2009CDCD0BD3 → vanilla Rifle_M21 GUIDB31929F65F0D0279. Production WeaponComponent CFBAA4B706BA66E8 содержит Muzzle CA6BE4D6B867541F и animator60B4EA76EB15F6E0; новый prefab переопределяет их на месте. Tube3 CD8091A2B3C4D5E6 имеет физический MaxAmmo3, а не только HUD-ограничение. Начальный probe2 — настройка лабораторного образца, не загрузка патрона из донора.

Core изучен только как потенциальный второй владелец ammo: `Scripts/Game/Items/ARMST_WEAPONS_HANDLER.c` содержит ARMST_SHOTGUN_COMPONENTS и TAO_DecrementAmmoOnRack; `Scripts/Game/Player/ARMST_PLAYER_CharacterController.c` регистрирует ARMST_LIGHT_RELOAD_ACTION. Core не подключать. Production prefab ссылается на custom component; наличие такой ссылки не разрешает включать Core ради устранения сообщения о классе. Применимость этой зависимости к instantiated prefab проверяется отдельно, вне анимационного preview.

## 2. Карта механизмов и доказательств

```text
Штатный ввод R / удержание / спуск
  → CharacterInputContext                       [декларации SDK]
  → CharacterCommandHandler.HandleWeaponReloading [скриптовый callback SDK]
  → HandleWeaponReloadingDefault / ReloadWeapon  [native, тела недоступны]
  → команда и native magazine lifecycle          [точный порядок не доказан]
  → character graph + injected W/P                [SyncWithCharacter contract]
  → пять фаз Astra                               [исправленный source, пока isolated preview]
  → W InsertCommit                               [имя в ANM; delivery/timing owner gate]
  → серверный coordinator(session, cycle)         [проектируется, не подключён]
  → donor−1 + тот же Tube3+1                      [существующий B2 bounded proof]
  → подтверждение операции → следующий цикл      [нужен новый adapter, не кнопка]
Патронник: отдельная native CMD1 / Weapon_Rack_Bolt ветка.
```

SDK evidence — в установленном `Workbench/docs/ArmaReforgerScriptAPIPublic/html/`:
- `interfaceCharacterCommandHandlerComponent.html:197,224`: HandleWeaponReloadingDefault — proto external, HandleWeaponReloading — bool callback. Это точка на ПЕРСОНАЖЕ, не WeaponAnimationComponent. Одной сигнатуры недостаточно для утверждения порядка native side effects и смысла return.
- `interfaceCharacterInputContext.html:155–157`: WeaponIsStartReloading, GetWeaponReloadType, SetReloadWeapon(int). Числа input reload type нельзя автоматически отождествлять с CMD_Weapon_Reload intValue.
- `interfaceCharacterControllerComponent.html:255–258`: ReloadWeapon/ReloadWeaponWith — native. Они не доказаны как безвредный animation trigger.
- `interfaceBaseItemAnimationComponent.html:131–149`: SyncWithCharacter подписывает item на изменения character variables/commands; OnCharacterCommand — void callback. Публичного bind/set API injected weapon graph в этом интерфейсе нет. Вызвать OnCharacterBoolVariable вручную — не доказанный setter.
- `interfaceCharacterAnimationComponent.html:166,177`: BindVariableBool и CallCommand существуют на character animation instance. Owner log [5983965875](https://github.com/Dubelkrya/Weapon_ARMA_X/issues/34#issuecomment-5983965875) прямо показывает lookup в player_main.agr, а не injected Astra. SetSharedVariableBool после отказа НЕ выполнялся; его распространение не проверено.
- BaseMagazineComponent.SetAmmoCount существует, но не делает два setter атомарными. G3B2 строки1195–1210 ставят latch и выполняют donor/target запись; строки1554–1570 освобождают её только после подтверждения.

Owner logs доказывают swaps предыдущего образца при CMD4/5 с native magazine events. Они не доказывают, что один только CMD при полностью очищенных клипах обязательно меняет магазин. Нельзя ни объявить engine cause установленной, ни считать новый граф безопасным. Повторять опасный игровой эксперимент запрещено.

Официальная [документация Nodes](https://community.bistudio.com/wiki/Arma_Reforger%3AAnimation_Editor%3A_Nodes) подтверждает Group.Animation при наличии Group Select и необходимость PostEval для условий времени дочерних нод. Полные страницы State Machine/Weapon Components вернули 403; version-specific выводы выше основаны на локальном SDK, не на предположении о текущей онлайн-версии.

## 3. Исправления, выполненные в live новой копии

Корень: `Assets/MP133_AstraShellGraph_test/`.

1. **AGF:** Idle→Reload теперь только CMD1 с float0; Shell(CMD2–6) удалён из ReloadRouteSTM. Это удаление неподтверждённого маршрута, НЕ отмена native reload до графа. **В игровом режиме обычный R пока использовать нельзя.**
2. **AGF:** Bolt→RackStanceSTM выбирает RackErcG для Stance0/1 и RackPneG для2. Оба задают Reload group/column перед RackBoltAnim. До исправления у bare `Reload.ReloadActionBolt` после удаления старой stance-ветки не было Group Select.
3. **AST+P/W ASI:** удалены все восемь назначений legacy Reload_InsertMag/Reload_RemoveMag (2 stance ×2 side ×2 phase) и их template slots. Оригинальные native файлы не удалялись. Пять фаз собраны в единственную группу AstraShell.Erc; GSelect/source/template/ASI согласованы. Shell Pne-анимаций нет: стоячую анимацию не выдаём за проверенную prone.
4. **AGR+AGF:** удалены пять ASTRA debug controls, не имевших рабочего writer. Свободное повторение по bool без подтверждённой транзакции удалено. Текущий animation kernel конечный: Start→Grab→Insert→Check→End. Это сознательно **один цикл до интеграции**, а не завершённая игровая перезарядка. Внешний MasterControl не входит в этот kernel.
5. **AGF:** Start/Grab могут закончиться на boundary по Firing/TriggerPulled/CMD_Weapon_Action_Interrupt; начавшийся Insert доигрывается, затем Check→End. Все шесть remaining-time переходов PostEval1. Это не latch: краткий input pulse может быть пропущен, настоящий coordinator обязан удерживать cancel до конца. В случае stop до commit будущая транзакция должна отклониться; pose completion не разрешает позднюю запись.

DefaultRunNode MasterControl, firing/safety/inspection узлы, native rack source и W/P bolt resources сохранены. Их runtime работоспособность не объявляется доказанной. Старые предупреждения других non-reload путей не скрываются: если компилятор сообщит Missing Group Select, вернуть конкретный путь; визуальное/скриптовое выполнение владельцем ещё не проверено.

Не менялись AW и шесть meta: AW A744E2E9E141725B, AGR7E087CCCBFB67045, AGF5106627621151975, AST6CFA1ACC8873A4B6, P B7A966A6741EAEE2, W4CF7F797EC1FCA0E. Fixture по-прежнему использует эти четыре W/P ссылки. Все десять оригинальных ANM/meta сохранены; чтение binary строк подтвердило наличие имён ASTRA phase/commit/stop, но НЕ подтвердило времена, порядок callback или корректность визуальных треков.

## 4. Единая архитектура для следующей реализации — минимальная граница разрешений

Нужен один владелец сессии перезарядки и ровно один маршрут штатного ввода. Дополнительные кнопки и global modded handler не нужны и не разрешены.

**Минимальное расширение scope для предложения, сейчас НЕ реализовано:** новый LAB-only персонаж, производный от штатного test character, с собственным подклассом CharacterCommandHandler и собственным authoring character graph/control schema. Production персонажей, vanilla player_main и Core не редактировать. Перехват HandleWeaponReloading применим только если активное оружие — новый Astra fixture; для остальных полное native делегирование. На лабораторном персонаже надо сначала доказать значение callback return/порядок default, различие short-R/hold-inspect, и отсутствие native CMD2–6. Пропуск default сам по себе пока не доказанная гарантия. Нужны отдельное разрешение на character prefab/graph и проверка всей цепи, а не модификация глобального класса.

Вторая половина — явный транспорт состояния между собственным root character graph и injected W/P. Добавление session/phase/cycle/cancel в собственную control schema решает конкретный lookup blocker player_main; факт синхронизации требуется подтвердить по обеим сторонам. Альтернатива — документированный прямой доступ к injected graph, если он будет найден в расширенном SDK; сейчас такой метод не найден. Само переименование переменных не решает проблему.

Предлагаемый протокол (псевдокод, НЕ готовые методы SDK):

```text
normal_reload_intent(new_fixture):
  если требуется только rack: native CMD1, без shell transaction
  иначе сервер проверяет actor/weapon/tube/capacity/donor → создаёт session
  начало Start/Grab; удержание R сохраняет штатную inspection-арбитрацию
on_W_insert_marker(session, cycle):
  принять только ожидаемый stage и первый маркер данного cycle
  повторно проверить actor, текущий weapon, тот же tube, donor ownership/type/count
  при cancel до записи: отклонить, перейти к End
  latch(session,cycle) → donor−1 → проверить → tube+1 → проверить conservation
  при любой неопределённости: quarantine, без слепого retry/refund
on_commit_ack(session,cycle):
  только после подтверждения, свободной ёмкости и донора разрешить следующий Grab
  full/no reserve/cancel/weapon loss → End → Idle
```

Это **одна** будущая перезарядка, не параллельная native-mag ветка. Контроллер должен владеть stop и не разрешать fire/pump одновременно с записью; патронник не правится вручную. Для empty chamber native cmd1 выполняется в согласованной отдельной фазе до/после shell session, когда оружие это допускает. Empty/full/partial/reserve=0 принимаются серверными проверками, не таймерами или fake ammo.

B2 нельзя вызвать как ScriptedUserAction из маркера: action привязан к owner/user, задержкам и in-flight latch. Нужен отдельный lab service с теми же проверками, без изменения защищённого G3B2; возврат COMMITTED/REJECTED/INDETERMINATE с token. Пока безопасный input/identity путь не доказан, ammo-writing service не поставляется согласно implementation gate задания.

Authority: клиент шлёт intent, не число патронов/готовый результат. Сервер выбирает/валидирует донор и единолично пишет; session+cycle+weapon identity защищают от повторной доставки W/P и сетевых повторов. P события визуальные, не второй commit. После donor-write ошибка не допускает автоматического возврата при изменившемся ownership/count; quarantine и журнал сверки. Никакой exactly-once/atomicity/MP PASS до отдельной проверки. Старый локальный stage latch — недостаточное доказательство exactly-once.

## 5. Минимальная безопасная проверка владельцем

1. Workbench только T4b, без standalone Astra/Core/старых диагностических проектов. В Resource Browser зарегистрировать `Prefabs/Test/ARMST_T4B_AstraRebuild_TestWeapon.et` через Register, сохранить настоящую meta; прислать GUID. Не путать entity ID с GUID. Отсутствие meta не мешает независимому открытию AW.
2. Открыть именно `Assets/MP133_AstraShellGraph_test/MP133_AstraShellGraph_test.aw`. Скомпилировать graph; вернуть полный error log, особенно пути Group Select. Ранее успешный Game compile не доказывает эту сборку.
3. Проверить template AstraShell.Erc с пятью строками в обоих ASI, 10 оригинальных ANM GUID и их ASTRA markers. Native insert/remove slots в новой копии должны отсутствовать; bolt Erc/Pne остаются.
4. В Animation Editor выбрать узел `AstraShellErcG` как preview run node средствами редактора, **не менять сохранённый DefaultRunNode**. Если установленная версия UI не позволяет выбор — прислать скрин; не добавлять runtime action. Firing=false, TriggerPulled=false; наблюдать один Start→Grab→Insert→Check→End. Повторная проба — перезапуск preview, не simulated ammo cycle.
5. Отдельно повторить с TriggerPulled=true во время Grab и Insert: в первом случае нет Insert; во втором движение Insert завершается, затем End. События здесь не разрешают никакой ammo mutation. В режиме MasterControl проверить только анимационный CMD1 и Erc/Pne source resolution, а не игровой R. Проверить firing/inspection графически без Game Mode.
6. STOP при unresolved ANM, ошибке сборки/двойном аниматоре, неправильной ASI или перескоке через фазу. Вернуть GUID fixture, screenshot нод+ASI и короткое видео. **Не запускать игровой R/CMD2–6: input suppression и physical tube survival пока не доказаны.**

Работающая обычная R-перезарядка, авторитетный repeat и conserved ammo остаются незавершёнными. Следующее решение владельца — разрешить минимальный lab-character scope выше либо предоставить документированный weapon-local способ перехвата до native reload/доступа к injected graph. Это конкретный архитектурный блокер, а не повод добавлять ещё один переключатель.

## 6. Проверки и сохранность

[Манифест before/after](astra-full-audit/repair_manifest.json): 712 baseline файлов; изменены ровно пять разрешённых ресурсов, остальные707 без изменений. Все 108 исходных файлов лаборатории инвентаризированы; production/Core/frozen/worlds покрыты ограниченным ранее определённым набором, не заявлен полный аудит всех установленных модов. Никаких запусков Workbench/игры и никаких изменений GUID/ANM/скриптов/старых fixtures.

Новые 8 source-contract tests проходят. Полный набор: **95 PASS / 1 FAIL из96**. Предсуществующий `test_astra_t4b_integration.test_paired_rows_match_authored_clips` проверяет старую неизменённую папку MP133_AstraShellGraph по устаревшим именам AstraShell.Erc; текущий owner-saved original использует Reload.Erc. Исправлять защищённый original ради теста нельзя; тест старого этапа не менялся и не отключался. Repository integrity: прежние3 broken Markdown links (два G3B1_TestWeapon и CURRENT_AI_SYNC→G4A). Они не вызваны новой копией. Это честные ограничения общего зелёного статуса, а не runtime ошибки новой перезарядки.
