from pathlib import Path
import shutil,json,zipfile,hashlib,re
root=Path(__file__).resolve().parents[1]
build=root/'tmp/board-review'
package=build/'delivery'
main=root/'Vortex_v8_доработка'
shutil.copytree(main/'Gerber',package/'Gerber',dirs_exist_ok=True)
readme='''Плата Vortex, исправление от 10.11.2026

Открывать Vortex_final.kicad_pro в KiCad 10. Плата: Vortex_final.kicad_pcb.
Ключевые правила сохранены в .kicad_pro и .kicad_dru: зазор 0,5 мм, медь до края 0,5 мм.
Контур 113,5 × 85 мм. Дорожки только на B.Cu. Gerber выпущен без дополнительного зеркалирования.

HW-517: размеры 16,5 × 34 мм. Силовые отверстия: 10 × 4,5 мм.
Управляющие штыри ставить в крайние малые отверстия S4 (PWM) и S1 (GND), расстояние 7,5 мм.
Крупные отверстия J1 модуля не используются. Замеры отражены с учётом измерения с обратной стороны.
XL4015: размеры 54 × 23,5 мм, между центрами штырей 50,5 × 20 мм.
JP1 вынесен ниже преобразователя. Перед подключением USB от ПК снять JP1.
Сначала настроить XL4015 на 5,0 В без ESP32.

J5 и J6, вид сверху, порядок сверху вниз одинаковый:
GND, 3V3, CLK, DT, SW. Энкодеры подключать проводами.
Сохранены прежние функции GPIO: насос D25, лента D23 через 330 Ом.
Энкодер насоса CLK D4 / DT D16 / SW D17; света CLK D18 / DT D19 / SW D21.
Питание энкодеров только 3V3.

Проволочные перемычки со стороны компонентов:
W1: 9 мм между центрами, GND, справа от HW-517. Изолированный медный провод 0,5 мм².
W2: 6,5 мм между центрами, 3V3, слева от разъёмов энкодеров. Изолированный медный провод.
Перемычки в меди верхнего слоя отсутствуют. Их требуется установить физически.
Для корректного учёта их соединений в DRC используется функция KiCad 10.

DRC: 0 нарушений, 0 неподключённых элементов. Назначение цепей исходных выводов сохранено.
Файла электрической схемы нет, ERC/сверка со схемой не выполнялись.
Дополнительные требования методички не проверены: методичка пока не получена.
Перед изготовлением выполнить примерку модулей по распечатке 1:1.
Старую прошивку требуется отдельно адаптировать к распиновке v8, сейчас она не изменена.
Насос тестировать только в воде.
'''
(package/'READ-ME.txt').write_text(readme,encoding='utf-8-sig')
report=json.loads((build/'drc.json').read_text(encoding='utf-8'))
assert not report['violations'] and not report['unconnected_items']
report['source']='Vortex_final.kicad_pcb'
(package/'DRC.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
assert hashlib.sha256((main/'Vortex_final.kicad_pcb').read_bytes()).digest()==hashlib.sha256((package/'Vortex_final.kicad_pcb').read_bytes()).digest()
pth=(main/'Gerber/Vortex_final-PTH.drl').read_text()
for coordinate in ['X141.0Y-122.5','X148.5Y-122.5','X160.0Y-78.5','X105.0Y-84.5','X107.54Y-84.5','X155.5Y-110.0','X164.5Y-110.0','X58.7Y-90.5','X58.7Y-97.0']:assert coordinate in pth,coordinate
out=root/'output/Vortex_corrected_2026-11-10.zip'
with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED) as z:
    for q in sorted(package.rglob('*')):
        if q.is_file():z.write(q,q.relative_to(package))
with zipfile.ZipFile(out) as z:assert z.testzip() is None;print('Archive:',out,'files:',len(z.namelist()))
