from pathlib import Path
import hashlib
import json
import re
import uuid
from zipfile import ZipFile, ZipInfo, ZIP_DEFLATED

root = Path(__file__).resolve().parent.parent
stage = root / 'output' / 'ФАЙЛЫ_ПРОЕКТА'
archive = root / 'output' / 'ФАЙЛЫ_ПРОЕКТА.zip'
stage.mkdir(parents=True, exist_ok=True)
inputs = {}
package_paths = set()

def read(rel):
    p = root / rel
    data = p.read_bytes()
    inputs[rel] = hashlib.sha256(data).hexdigest()
    return data.decode('utf-8-sig')

def put(rel, text):
    p = stage / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding='utf-8', newline='\n')
    assert p.read_bytes().decode('utf-8') == text
    package_paths.add(p)

pcb = read('Vortex_v8_доработка/Vortex_final.kicad_pcb')
pattern = re.compile(r'\b[0-9a-fA-F]{8}(?:-[0-9a-fA-F]{4}){3}-[0-9a-fA-F]{12}\b')
old_ids = set(pattern.findall(pcb))
mapping = {old: str(uuid.uuid4()) for old in old_ids}
clean_pcb = pattern.sub(lambda m: mapping[m[0]], pcb)
inverse = {v: k for k, v in mapping.items()}
assert pattern.sub(lambda m: inverse[m[0]], clean_pcb) == pcb
assert not old_ids.intersection(pattern.findall(clean_pcb))
put('board/Vortex_final.kicad_pcb', clean_pcb)
for ext in ('kicad_pro', 'kicad_dru'):
    put(f'board/Vortex_final.{ext}', read(f'tmp/board-review/delivery/Vortex_final.{ext}'))

gerber_changes = 0
for name in ('BottomLayer.gbr', 'BoardOutline.gbr', 'DrillPTH.drl', 'DrillNPTH.drl'):
    original = read('Vortex_v8_доработка/Gerber/' + name)
    lines = original.splitlines(keepends=True)
    def metadata(line):
        return line.startswith(('%TF.CreationDate,', '%TF.ProjectId,', 'G04 Created by ')) or line.startswith('; DRILL file ') or line.startswith('; #@! TF.CreationDate,')
    retained = [line for line in lines if not metadata(line)]
    gerber_changes += len(lines) - len(retained)
    clean = ''.join(retained)
    assert clean == ''.join(line for line in lines if not metadata(line))
    put('board/Gerber/' + name, clean)

firmware = read('led_test.ino')
clean_firmware = firmware
settings = {'HOME_SSID': 'YOUR_WIFI_SSID', 'HOME_PASS': 'YOUR_WIFI_PASSWORD', 'WIFI_NAME': 'WaterVortex', 'WIFI_PASS': 'CHANGE_ME'}
for key, val in settings.items():
    clean_firmware, count = re.subn(r'(const char\*\s+' + key + r'\s*=\s*)"[^"\r\n]*"', lambda m: m[1] + json.dumps(val), clean_firmware)
    assert count == 1
mask = lambda s: re.sub(r'(const char\*\s+(?:HOME_SSID|HOME_PASS|WIFI_NAME|WIFI_PASS)\s*=\s*)"[^"\r\n]*"', r'\1"CONFIG"', s)
assert mask(firmware) == mask(clean_firmware)
put('firmware/led_test/led_test.ino', clean_firmware)
put('firmware/encoder_test/encoder_test.ino', read('encoder_test/encoder_test.ino'))
put('КОНТЕКСТ_ПРОЕКТА.txt', read('output/КОНТЕКСТ_ПРОЕКТА.txt'))

put('НАЧНИ_ЗДЕСЬ.txt', '''ПЦП — «Водяной вихрь»

КОНТЕКСТ_ПРОЕКТА.txt — описание проекта, распиновка, корпус, состояние и задачи.

board/ — актуальная плата, настройки и правила KiCad 10. Открывать Vortex_final.kicad_pro. Встроенные посадочные места находятся в файле платы. Отдельной электрической схемы нет.
board/Gerber/ — медь B.Cu, контур, монтажная и крепёжная сверловка. ISO/G-code ещё не подготовлены.
board/DRC.json — сохранённый отчёт исходной платы; его статус описан в ПРОВЕРКА.txt.

firmware/led_test/led_test.ino — исходник управления насосом и подсветкой. Параметры Wi-Fi заменены заглушками. Перед сборкой задать HOME_SSID, HOME_PASS, WIFI_NAME и WIFI_PASS; пароль собственной точки доступа должен содержать не менее 8 символов.
ВАЖНО: LED_PIN в этом скетче всё ещё равен 16, а на плате лента подключена к 23. Это исходник для адаптации. Два энкодера в него не добавлены. Не загружать на новую плату без проверки распиновки.

firmware/encoder_test/encoder_test.ino — отдельный тест энкодера CLK=18, DT=19, SW=21, Serial 115200. Он не содержит управления всей установкой.

Для подготовки копии обновлены внутренние идентификаторы объектов платы, удалены даты генерации и идентификаторы проекта из Gerber/сверловки. Геометрия, цепи и команды производства сохранены. В прошивке изменены только четыре строки настройки сети.

Бинарная копия памяти ESP32 не включена, поскольку может содержать настройки сети. История разработки, промежуточные архивы, локальные пути и служебные файлы рабочей среды не включены. Исходники корпуса и актуальная электрическая схема отсутствуют в имеющемся наборе; их описание находится в контексте.

ПРОВЕРКА.txt — проверка состава и сохранности. КОНТРОЛЬНЫЕ_СУММЫ.txt — SHA-256 файлов пакета.

Насос испытывать только в воде. Энкодеры только на 3V3. До установки ESP32 настроить XL4015 на 5,0 В. Перед USB от компьютера снять JP1.
''')

report = json.loads(read('tmp/board-review/delivery/DRC.json'))
assert not report.get('violations'), len(report.get('violations', []))
assert not report.get('unconnected_items'), len(report.get('unconnected_items', []))
report['source'] = 'Vortex_final.kicad_pcb'
report.pop('date', None)
report['report_note'] = 'Сохранённый результат проверки исходной платы. Повторный запуск для копии прерван по тайм-ауту. Геометрия и цепи сохранены; служебные UUID объектов обновлены.'
put('board/DRC.json', json.dumps(report, ensure_ascii=False, indent=2) + '\n')

put('ПРОВЕРКА.txt', f'''Проверка комплекта

KiCad {report.get('kicad_version', '10')}: сохранённая DRC-проверка исходной платы.
Нарушений: {len(report.get('violations', []))}.
Неподключённых элементов: {len(report.get('unconnected_items', []))}.
Полный отчёт: board/DRC.json; учитывать список отключённых вспомогательных проверок в нём.
ERC и сверка со схемой не выполнялись: схемы нет.
Повторный запуск DRC для копии не завершился за 120 секунд. Новый результат не получен. Вложенный отчёт не выдаётся за новую проверку.

Текст платы сверён с исходником после обратной подстановки служебных UUID: полное совпадение. Обновлено {len(mapping)} UUID объектов. Координаты, размеры и цепи не менялись.
Gerber и сверловка сверены после удаления только информационных строк с датой/ProjectId: полное совпадение команд.
Прошивка сверена после маскирования только четырёх сетевых строк: полное совпадение кода.
Исходные файлы проекта не изменены; проверены их SHA-256 до и после подготовки.

Проверка не заменяет физическую примерку модулей и испытание устройства. Компиляция и загрузка прошивки не выполнялись, адаптация под новую распиновку ещё нужна.
''')

for rel, sha in inputs.items():
    assert hashlib.sha256((root / rel).read_bytes()).hexdigest() == sha, rel

forbidden = re.compile(r'claude|anthropic|artifact|chatgpt|codex|kredos|teftelya|limbermidge|данил|01a0fc01|(?<![a-z0-9])[a-z]:[\\/]|[\w.+-]+@[\w.-]+\.[a-z]{2,}', re.I)
allowed_urls = {'https://schemas.kicad.org/drc.v1.json', 'http://vortex.local', 'http://'}
for p in package_paths:
    assert p.suffix.lower() not in {'.bin', '.zip', '.prl', '.pdf', '.png'}
    s = p.read_text(encoding='utf-8-sig')
    assert not forbidden.search(s), p.name
    assert '\ufffd' not in s, p.name
    for link in re.findall(r'https?://[^\s"<>]*', s):
        assert link in allowed_urls, (p.name, link)

manifest = []
for p in sorted(package_paths):
    if p.name != 'КОНТРОЛЬНЫЕ_СУММЫ.txt':
        manifest.append(hashlib.sha256(p.read_bytes()).hexdigest() + '  ' + p.relative_to(stage).as_posix())
put('КОНТРОЛЬНЫЕ_СУММЫ.txt', '\n'.join(manifest) + '\n')

with ZipFile(archive, 'w', ZIP_DEFLATED, compresslevel=9) as z:
    for p in sorted(package_paths):
        if p.is_file():
            info = ZipInfo(p.relative_to(stage).as_posix(), date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type = ZIP_DEFLATED
            info.create_system = 0
            info.extra = b''
            info.comment = b''
            z.writestr(info, p.read_bytes())
with ZipFile(archive) as z:
    assert z.testzip() is None
    for name in z.namelist():
        assert z.read(name) == (stage / name).read_bytes()
    for line in z.read('КОНТРОЛЬНЫЕ_СУММЫ.txt').decode().splitlines():
        sha, name = line.split('  ', 1)
        assert hashlib.sha256(z.read(name)).hexdigest() == sha
    count = len(z.namelist())

print(json.dumps({'files': count, 'bytes': archive.stat().st_size, 'drc_violations': len(report.get('violations', [])), 'unconnected_items': len(report.get('unconnected_items', [])), 'object_uuids_updated': len(mapping), 'production_metadata_lines_removed': gerber_changes, 'privacy_scan': 'passed', 'archive_integrity': 'passed', 'originals_unchanged': True}, ensure_ascii=False))
