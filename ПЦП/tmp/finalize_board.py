from pathlib import Path
import shutil,zipfile,json,hashlib
root=Path(__file__).resolve().parents[1]
src=root/'Vortex_v8_доработка'
build=root/'tmp'/'board-review'
package=build/'delivery'
package.mkdir(exist_ok=True)
original=build/'original-20261110.zip'
if not original.exists():
    with zipfile.ZipFile(original,'w',zipfile.ZIP_DEFLATED) as z:
        for q in src.rglob('*'):
            if q.is_file():z.write(q,q.relative_to(src))
report=json.loads((build/'drc.json').read_text(encoding='utf-8'))
assert not report['violations'] and not report['unconnected_items']
shutil.copy2(build/'Vortex_revised.kicad_pcb',src/'Vortex_final.kicad_pcb')
shutil.copy2(src/'Vortex_final.kicad_pcb',package/'Vortex_final.kicad_pcb')
pro=json.loads((build/'Vortex_revised.kicad_pro').read_text(encoding='utf-8'))
pro['meta']['filename']='Vortex_final.kicad_pro'
(package/'Vortex_final.kicad_pro').write_text(json.dumps(pro,indent=2),encoding='utf-8')
shutil.copy2(build/'Vortex_revised.kicad_dru',package/'Vortex_final.kicad_dru')
print('Board installed; original archived:',original)
