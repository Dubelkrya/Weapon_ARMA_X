# Изоляция ошибки запуска, 14 октября 2026

Start-ShotgunTest.ps1 теперь выбирает Core по GUID 69E4C3542B6CDC19.
Его зависимости (включая Weapons и Sounds) разрешает движок.
Полный список имён из Workbench больше не используется.
Это исключает явный выбор локальной MOVehicles с GUID 6922BD7593B11A0A
в дополнение к опубликованной с GUID 6A8EECAC154A0BBD. Каталоги не удаляются.
Успешное разрешение всей цепочки пока не подтверждено запуском.

Первым выполнить загрузочную проверку SoundsOnly:

`powershell -NoProfile -File .\Start-ShotgunTest.ps1 -Role Client -Test SoundsOnly`

Она исключает Workbench/addons из addonsDir и выбирает только Sounds по GUID.
Это проверка инициализации, не мультиплеерный тест и не запуск сервера.
Ошибка подключения к отсутствующему серверу после инициализации допустима.
Если снова Can't add filesystem directory для Sounds — дальше проверять его
пакет/совместимость; не удалять аддон и не менять оружие наугад.

Проверка готовой команды без запуска:

`powershell -NoProfile -File .\Start-ShotgunTest.ps1 -Role Client -Test SoundsOnly -DryRun`

После успешной загрузки Sounds:

`powershell -NoProfile -File .\Start-ShotgunTest.ps1 -Role Client -Test ARMST`

Режим Server по-прежнему требует явно переданного установленного серверного exe.
Скрипт не добавляет обработчик Net API в игровой процесс.
