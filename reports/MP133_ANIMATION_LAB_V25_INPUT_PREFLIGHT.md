# MP-133 Lab — V2.5b input preflight (issue #27 review before re-enabling the gate)

Gate `m_bLabInsertEnabled` остаётся **OFF** на обоих префабах. Работа — только в
лабораторных скриптах; движок/Workbench/игра не запускались.

## 1. Где вызывается `HandleWeaponReloading` и что такое «свежий» R

- `HandleWeaponReloading(CharacterInputContext, float, int)` — виртуальный метод
  `SCR_CharacterCommandHandlerComponent` (локальная API-дока). Движок вызывает
  его **пока активна команда перезагрузки** — это **покадровый callback**, а не
  событие нового нажатия (подтверждается прошлым логом: 61 вызов за удержание).
- «Новый запрос» определяется как **эпизод**: запрос активен, если
  `WeaponIsStartReloading() == true` **или** `GetWeaponReloadType() != 0`.
  Эпизод потребляет ровно одну попытку (`m_bLabInputLatched=true`), повторные
  покадровые вызовы игнорируются до **положительного отпускания**.

## 2. Помпа (LSHIFT+R) vs `type=1`

- Отклонение по `type==1` **убрано** (могло блокировать обычный R).
- Помпа распознаётся по **существующему Core-действию** `ARMST_LIGHT_RELOAD_ACTION`
  (LSHIFT+R; Core сам на него подписан и вызывает `SetReloadWeapon(1)`).
  Лаборатория добавляет свой listener и ставит `m_bLabPumpLatch`. Обычный R с
  любым типом (включая транзитный 1) при отсутствии pump-latch → попытка вставки.
- **Порядок обработчиков:** чтобы LSHIFT+R не запустил оба действия независимо от
  порядка, старт вставки **отложен** на `LAB_BEGIN_DEFER_MS = 30` мс
  (`LabDeferredBegin`). К моменту исполнения pump-latch (если это помпа) уже
  установлен, и отложенный старт отменяется (`deferred begin cancelled (pump latch set)`).
  Проверены оба порядка: pump-до-обработчика → `pump`; обработчик-до-pump →
  `begin_deferred` → `pump_abort`.

## 3. Отпускание: только положительные признаки, без таймера

`LabInputReleased` (watcher каждые 100 мс):

```
if (m_bLabClientInsertActive) return false;   // действие идёт
if (IsReloading())            return false;   // команда перезагрузки активна
if (m_bLabPumpLatch)          return false;   // активна помпа
if (!inputCtx)                return false;   // нет контекста -> НЕ доказательство отпускания
return (!inputCtx.WeaponIsStartReloading() && inputCtx.GetWeaponReloadType() == LAB_NO_RELOAD);
```

- **Таймер-ре-арм удалён полностью** (`LAB_LATCH_SAFETY_MS` и `input re-armed
  (safety timeout)` отсутствуют). Удержание R > 2 с **не** ре-армит latch и не
  запускает новую попытку.
- `abort`/серверный `cease`/низкое оружие/полная труба/удержание — latch не
  ре-армят. Новый вход — только после `input re-armed (released)` (положительный
  idle) **или** потери управления персонажем (`OnControlledByPlayer(false)`
  сбрасывает latch/pump — это новая сессия управления, а не имитация отпускания).

## 4. Offline-модель и тесты (НЕ runtime)

`agent/scripts/mp133_lab_r_gate_model.py` (зеркалит EnforceScript) +
`agent/tests/test_mp133_lab_r_gate_model.py` — **17/17 OK**, включая:
press→begin_deferred→resolve→begin→hold→abort→release→fresh press;
**hold > 2 с не ре-армит**; no-repeat-while-held; ordinary R с type 1 не
блокируется; **оба порядка** pump/handler (order A/order B); lowered; full;
no reserve; foreign/gate-off passthrough; release требует
`!insertActive && !IsReloading && !pump && !start && type==0`; отсутствие
input-контекста **не** считается отпусканием. Явно **model-only**.

## 5. Вердикт и остаточные неизвестности

**Вердикт: кандидат тестируем** (не `INPUT_GATE_BLOCKED`):
различение помпы — существующее Core-действие; порядок обработчиков снят
отложенным стартом; таймер-имитация отпускания удалена.

Остаточные неизвестности (без выдуманных методов):
- Не доказано (до игры), что `WeaponIsStartReloading()/GetWeaponReloadType()`
  надёжно возвращаются в idle после отпускания. Если нет — latch останется
  взведённым (R не запустит новую досылку), это **безопасное** поведение; таймером
  отпускание не подменяем. Конкретный признак для проверки в логе: строка
  `input re-armed (released)` после отпускания R.
- Не доказано рантаймом, что `HandleWeaponReloading`, возвращающий `true`,
  подавляет нативную перезагрузку (прошлый нулевой mag-swap недоказателен).

## 6. Изоляция

Клипы W `{1F9884C8701DAE1B}`, P `{FE510A1EC49563F1}` — не перегенерировались.
Граф lab-only, магазин 3, RIS gate OFF, production не тронут. Runtime —
`OWNER TEST REQUIRED`.
