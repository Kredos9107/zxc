from pathlib import Path
import pcbnew as p
import json,shutil,hashlib
root=Path(__file__).resolve().parents[1]
main=root/'Vortex_v8_доработка/Vortex_final.kicad_pcb'
build=root/'tmp/board-review'
before=build/'before-origin-20261110.kicad_pcb'
if not before.exists():shutil.copy2(main,before)
snapshot=main.read_bytes()
(build/'latest-input-before-origin.kicad_pcb').write_bytes(snapshot)
(build/'move-input.sha256').write_text(hashlib.sha256(snapshot).hexdigest())
b=p.LoadBoard(str(main))
def v(x,y):return p.VECTOR2I(p.FromMM(x),p.FromMM(y))
adjust={
 ((68.83,71.25),(75.5,71.25)):((68.83,71.25),(76,71.25)),
 ((75.5,71.25),(76.75,72.5)):((76,71.25),(77.2,72.45)),
 ((76.75,72.5),(76.75,74.5)):((77.2,72.45),(77.2,74.8)),
 ((76.75,74.5),(75.21,76.04)):((77.2,74.8),(75.96,76.04)),
 ((75.21,76.04),(74.5,76.04)):((75.96,76.04),(74.5,76.04)),
}
coords=lambda q:(round(p.ToMM(q.x),3),round(p.ToMM(q.y),3))
for t in list(b.GetTracks()):
    a,c=coords(t.GetStart()),coords(t.GetEnd())
    if t.GetNetname()=='/GND' and (a,c) in adjust:
        u,w=adjust[(a,c)];t.SetStart(v(*u));t.SetEnd(v(*w))
    if t.GetNetname() in ['/ENC2_CLK','/ENC2_DT','/ENC2_SW']:
        if a[0]==61.5 and c[0]==69.42:t.SetEnd(v(68.42,c[1]))
        elif a[0]==69.42 and c[0]==74.5:
            t.SetStart(v(68.42,a[1]));t.SetEnd(v(73.5,c[1]))
            z=p.PCB_TRACK(b);z.SetStart(v(73.5,c[1]));z.SetEnd(v(*c));z.SetWidth(t.GetWidth());z.SetLayer(p.B_Cu);z.SetNet(t.GetNet());b.Add(z)
edges=[z for z in b.GetDrawings() if z.GetLayer()==p.Edge_Cuts]
left=min(min(z.GetStart().x,z.GetEnd().x) for z in edges)
top=min(min(z.GetStart().y,z.GetEnd().y) for z in edges)
delta=p.VECTOR2I(-left,-top)
for f in b.GetFootprints():f.Move(delta)
for t in b.GetTracks():t.Move(delta)
for d in b.GetDrawings():d.Move(delta)
for z in b.Zones():z.Move(delta)
for f in b.GetFootprints():
    for q in f.Pads():q.SetLocalClearance(p.FromMM(.6))
b.GetDesignSettings().SetAuxOrigin(p.VECTOR2I(0,0))
b.GetDesignSettings().SetGridOrigin(p.VECTOR2I(0,0))
dest=build/'manual-check/Vortex_final.kicad_pcb'
p.SaveBoard(str(dest),b)
print('Translation:',p.ToMM(delta.x),p.ToMM(delta.y),'mm; staged:',dest)
