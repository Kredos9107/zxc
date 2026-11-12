from pathlib import Path
import json,shutil,zipfile,hashlib
root=Path(__file__).resolve().parents[1]
main=root/'Vortex_v8_доработка'
build=root/'tmp/board-review'
package=build/'delivery'
report=json.loads((build/'manual-check/drc-moved.json').read_text())
assert not report['violations'] and not report['unconnected_items']
assert (main/'Vortex_final.kicad_pcb').read_bytes()==(build/'manual-check/Vortex_final.kicad_pcb').read_bytes()
names={'Vortex_final-B_Cu.gbl':'BottomLayer.gbr','Vortex_final-Edge_Cuts.gm1':'BoardOutline.gbr','Vortex_final-PTH.drl':'DrillPTH.drl','Vortex_final-NPTH.drl':'DrillNPTH.drl'}
for old,new in names.items():
    src=main/'Gerber'/old;dst=main/'Gerber'/new
    assert src.is_file() and not dst.exists(),(src,dst)
    src.rename(dst)
job=main/'Gerber/Vortex_final-job.gbrjob'
if job.exists():shutil.move(str(job),str(build/'last-GerberJob.gbrjob'))
outgerber=package/'Gerber'
assert outgerber.resolve().is_relative_to(root.resolve())
for q in outgerber.iterdir():
    if q.is_file():q.unlink()
for new in names.values():shutil.copy2(main/'Gerber'/new,outgerber/new)
shutil.copy2(main/'Vortex_final.kicad_pcb',package/'Vortex_final.kicad_pcb')
pro=json.loads((package/'Vortex_final.kicad_pro').read_text())
pro['board']['design_settings']['rules']['min_clearance']=.6
for cls in pro['net_settings']['classes']:cls['clearance']=.6;cls['via_diameter']=1.8
(package/'Vortex_final.kicad_pro').write_text(json.dumps(pro,indent=2),encoding='utf-8')
(package/'Vortex_final.kicad_dru').write_text('(version 1)\n(rule "Manual clearance 0.6 mm" (constraint clearance (min 0.6mm)))\n(rule "Copper edge 0.5 mm" (constraint edge_clearance (min 0.5mm)))\n',encoding='utf-8')
(package/'DRC.json').write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding='utf-8')
readme=(package/'READ-ME.txt').read_text(encoding='utf-8-sig')
readme=readme.replace('зазор 0,5 мм','зазор 0,6 мм').replace('Дополнительные требования методички не проверены: методичка пока не получена.','Методичка получена. Правила 0,6 мм проверены. Пять тесных мест исправлены, DRC: 0 нарушений.\nЛевый верхний угол контура платы находится в (0; 0) мм в KiCad.\nМедь, контур и сверловка сдвинуты согласованно.\nФайлы CAM: BottomLayer.gbr, BoardOutline.gbr, DrillPTH.drl, DrillNPTH.drl.\nISO ещё не подготовлены: подготовка CAM приостановлена пользователем.')
(package/'READ-ME.txt').write_text(readme,encoding='utf-8-sig')
out=root/'output/Vortex_corrected_2026-11-10.zip'
with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED) as z:
    for q in sorted(package.rglob('*')):
        if q.is_file():z.write(q,q.relative_to(package))
with zipfile.ZipFile(out) as z:assert z.testzip() is None
drill=(main/'Gerber/DrillPTH.drl').read_text()
assert 'X86.0Y-69.0' in drill and 'X93.5Y-69.0' in drill
assert all((main/'Gerber'/name).is_file() for name in names.values())
print('Origin and Gerber verified; archive updated:',out)
