# Read-only Workbench NET API

## v5

После пользовательской компиляции: `python probe.py --snapshot`.
Снимки сохраняются в Weapon X/artifacts/workbench-net-api, без перезаписи.
Клиент требует v5, проверяет Ok и nonce, прекращает запросы после ошибки.
Обработчик возвращает до 8 выделенных объектов (truncated при превышении).
fields содержит path, field, valueType, status, value и directlySet.
Значение передаётся строкой с явным типом; absent/read-failed не являются нулём.
directlySet относится к текущему контейнеру, не определяет полный путь источника.
Старые configurationRows сохранены для совместимости. Gameplay не читается.
Тест клиента: `python -m unittest test_probe.py`.

`probe.py` подключается только к 127.0.0.1:5775. Два встроенных запроса возвращают
состояние Workbench / World Editor и ScriptsCompiled. Они не запускают компиляцию,
не открывают ресурсы и не изменяют проект. Порт не нужно открывать в интернет.

Запуск из этой папки: `python probe.py`.

Дополнительная проверка: `python probe.py --custom`.
Для неё Workbench должен загрузить и скомпилировать WAX_ReadOnlyNetApi.c из
`Scripts/WorkbenchGame`. Weapon X не имеет собственного .gproj: простого хранения
файла здесь недостаточно. Подключение к реальному Workbench-проекту выполняется
отдельно; этот этап пока не сделан. Не копировать в Scripts/Game.

Обработчик возвращает только маркер, scope и переданный nonce. Он намеренно не
заявляет название текущего проекта и не читает игровое состояние.
Проверка nonce подтверждает ответ нашего обработчика, не работу мультиплеера.

error_code сохраняется без интерпретации: при проверке нужно смотреть и этот код,
и payload. Ответ встроенного API не доказывает успешную компиляцию нового файла.

Документация протокола:
https://community.bistudio.com/wikidata/external-data/arma-reforger/EnfusionScriptAPIPublic/Page_NetApi.html
