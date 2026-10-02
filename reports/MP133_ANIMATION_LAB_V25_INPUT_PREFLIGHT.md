# MP-133 Lab — V2.5 input preflight (issue #27 review before re-enabling the gate)

Gate `m_bLabInsertEnabled` остаётся **OFF** на обоих префабах.
Работа — только в лабораторных скриптах; движок/Workbench/игра не запускались.

## 1. Где вызывается `HandleWeaponReloading` и что такое «свежий» R

- `HandleWeaponReloading(CharacterInputContext, float, int)` — виртуальный метод
  `SCR_CharacterCommandHandlerComponent` (подтверждено локальной
  `interfaceCharacterCommandHandlerComponent.html`). Движок вызывает его
  **пока активна команда перезагрузки**, т.е. это **покадровый callback**, а не
  событие нового нажатия. Это прямо подтверждает прошлый лог владельца: 61 вызов
  обработчика за один удержанный ввод.
- Поэтому «новый запрос» нельзя получить из самого обработчика. Используется
  **эпизод-защёлка**: запрос считается активным, если
  `inputCtx.WeaponIsStartReloading()` **или** `GetWeaponReloadType() != 0`.
  Эпизод «съедает» ровно одну попытку (`m_bLabInputLatched = true`), повторные
  покадровые вызовы игнорируются до **настоящего отпускания**.

## 2. Как помпа (LSHIFT+R) отличается от наблюдённого `type=1`

- **Не по значению типа.** Прошлый лог показал `reloadType=1` непосредственно
  перед лабораторным обработчиком, и невозможно утверждать, что это всегда
  LSHIFT+R. Поэтому входной гейт **не отклоняет `type==1`** (такое отклонение
  могло бы полностью заблокировать обычный R).
- Помпа определяется по **существующему проектному действию** Core
  `ARMST_LIGHT_RELOAD_ACTION` (это ARMST-действие из `Core/Configs/System/
  chimeraInputCommon.conf`, на которое сам Core вешает `AddActionListener` и
  вызывает `inputCtx.SetReloadWeapon(1)`). Лаборатория добавляет свой listener
  на то же действие (в `OnControlledByPlayer`, local-only) и ставит
  `m_bLabPumpLatch` при срабатывании. Это не выдуманное «нативное» имя — это
  фактическое Core-действие, подтверждённое исходником Core.
- Итог: `pump` (LSHIFT+R) → `m_bLabPumpLatch` → не вставка; обычный R (любой тип,
  включая транзитный 1) при отсутствии pump-latch → попытка вставки.

## 3. Точный предикат отпускания и момент re-arm

`LabInputReleased` (используется watcher'ом каждые 100 мс):

```
if (m_bLabClientInsertActive) return false;   // действие ещё идёт
if (IsReloading())            return false;   // команда перезагрузки активна
if (m_bLabPumpLatch)          return false;   // активна помпа
if (!inputCtx)                return true;
return (!inputCtx.WeaponIsStartReloading() && inputCtx.GetWeaponReloadType() == LAB_NO_RELOAD);
```

- re-arm (`m_bLabInputLatched=false`) — только по этому предикату
  (`input re-armed (released)`), плюс **страховочный таймаут 2 с**
  (`input re-armed (safety timeout)`, если latch залип, но ничего не активно и не
  перезаряжается) — чтобы игрок не оказался навсегда заблокирован.
- `abort`, серверный `cease`, отпущенное/сброшенное оружие, полная труба и
  удержанный R **не** ре-армят latch: abort/cease — это `LabClientStopInsert`
  (не трогает latch); отпущенное/полная труба — `begin blocked` (latch уже
  потреблён); новый вход возможен только после `released`/таймаута.

## 4. Offline-тесты состояния (модель, НЕ runtime)

`agent/scripts/mp133_lab_r_gate_model.py` — документированная модель принятия
решений (зеркалит EnforceScript), `agent/tests/test_mp133_lab_r_gate_model.py` —
**15/15 OK**, включая:
press→begin→held→abort→held→release→fresh press; no-repeated-begin; ordinary R
with type 1 не блокируется; pump не становится вставкой; lowered; full tube; no
reserve; foreign weapon/gate-disabled passthrough; release требует
`!insertActive && !IsReloading && !pump && !start && type==0`; safety-timeout.

Явно: это **model-only**, не доказательство рантайма.

## 5. Вердикт и остаточные неизвестности

**Вердикт: кандидат тестируем** (не `INPUT_GATE_BLOCKED`): различение помпы
опирается на существующее проектное Core-действие, а отпускание имеет
страховочный таймаут. Гейт остаётся OFF до твоего review.

Остаточные неизвестности (явно, без выдуманных методов):
- Не доказано (до игры), что `IsReloading()` надёжно сбрасывается после
  завершения вставки; если нет — re-arm произойдёт по таймауту.
- Не доказано, что `WeaponIsStartReloading()/GetWeaponReloadType()` надёжно
  возвращаются в idle; таймаут закрывает залипание.
- Не доказано рантаймом, что `HandleWeaponReloading`, возвращающий `true`,
  подавляет нативную перезагрузку (прошлый нулевой mag-swap недоказателен —
  коммита не было).

## 6. Изоляция

Клипы: W `{1F9884C8701DAE1B}`, P `{FE510A1EC49563F1}` — не перегенерировались.
Граф (lab-only, с hardening), магазин 3, RIS gate OFF, production не тронут.
Runtime — `OWNER TEST REQUIRED`.
