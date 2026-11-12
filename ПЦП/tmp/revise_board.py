import pcbnew as p
import json, pathlib, shutil, re

ROOT=pathlib.Path(__file__).resolve().parents[1]
OUT=ROOT/'tmp'/'board-review'
OUT.mkdir(parents=True,exist_ok=True)
SRC=ROOT/'Vortex_v8_доработка'/'Vortex_final.kicad_pcb'
DEST=OUT/'Vortex_revised.kicad_pcb'
change={'/GND','/+3V3','/ENC2_CLK','/ENC2_DT','/ENC2_SW','/ESP_VIN','/+5V','/PUMP_PWM','/+12V','/PUMP_POS','/PUMP_NEG'}
def children(s):
    depth=0;quoted=False;escape=False;start=None
    for i,c in enumerate(s):
        if quoted:
            if escape:escape=False
            elif c=='\\':escape=True
            elif c=='"':quoted=False
            continue
        if c=='"':quoted=True
        elif c=='(':
            if depth==1:start=i
            depth+=1
        elif c==')':
            depth-=1
            if depth==1 and start is not None:yield s[start:i+1]
raw=[]
for chunk in children(SRC.read_text(encoding='utf-8')):
    if chunk.startswith('(segment') and any('(net "'+n+'")' in chunk for n in change):continue
    if chunk.startswith('(gr_text'):continue
    if chunk.startswith('(footprint'):
        if re.search(r'\(property "Reference" "W3"',chunk):continue
        if re.search(r'\(property "Reference" "(?:U2|U3|JP1)"',chunk):
            chunks=list(children(chunk));head=chunk[:chunk.find('(',1)]
            chunk=head+'\n'+'\n'.join(c for c in chunks if not c.startswith(('(fp_line','(fp_rect','(fp_poly','(fp_arc','(fp_circle')))+'\n)'
    raw.append(chunk)
filtered=OUT/'source-filtered.kicad_pcb'
filtered.write_text('(kicad_pcb\n'+'\n'.join(raw)+'\n)',encoding='utf-8')
b=p.LoadBoard(str(filtered))
drawings=list(b.GetDrawings())
alltracks=list(b.GetTracks())
fps={f.GetReference():f for f in b.GetFootprints()}
net={n.GetNetname():n for n in b.GetNetInfo().NetsByNetcode().values()}
def xy(x,y):return p.VECTOR2I(p.FromMM(x),p.FromMM(y))
def pad(ref,num):return next(z for z in fps[ref].Pads() if z.GetNumber()==str(num))
def at(ref,num,x,y):pad(ref,num).SetPosition(xy(x,y))
def label(t,x,y,size=1,layer=p.F_SilkS):
    q=p.PCB_TEXT(b);q.SetText(t);q.SetPosition(xy(x,y));q.SetTextSize(xy(size,size));q.SetTextThickness(p.FromMM(.15));q.SetLayer(layer);b.Add(q);return q
def line(owner,x1,y1,x2,y2,layer=p.F_SilkS):
    z=p.PCB_SHAPE(owner);z.SetShape(p.SHAPE_T_SEGMENT);z.SetStart(xy(x1,y1));z.SetEnd(xy(x2,y2));z.SetLayer(layer);z.SetWidth(p.FromMM(.15));owner.Add(z)
def outline(ref,x,y,w,h):
    f=fps[ref]
    for x1,y1,x2,y2 in [(x,y,x+w,y),(x+w,y,x+w,y+h),(x+w,y+h,x,y+h),(x,y+h,x,y)]:line(f,x1,y1,x2,y2,p.F_Fab)
    for x1,y1,x2,y2 in [(x-.5,y-.5,x+w+.5,y-.5),(x+w+.5,y-.5,x+w+.5,y+h+.5),(x+w+.5,y+h+.5,x-.5,y+h+.5),(x-.5,y+h+.5,x-.5,y-.5)]:line(f,x1,y1,x2,y2,p.F_CrtYd)
def route(n,width,points):
    for (x1,y1),(x2,y2) in zip(points,points[1:]):
        if (x1,y1)==(x2,y2):continue
        z=p.PCB_TRACK(b);z.SetStart(xy(x1,y1));z.SetEnd(xy(x2,y2));z.SetWidth(p.FromMM(width));z.SetLayer(p.B_Cu);z.SetNet(net[n]);b.Add(z)
def jumper(ref,n,a,c,size,drill):
    f=p.FOOTPRINT(b);f.SetReference(ref);f.SetValue('INSULATED WIRE');f.SetPosition(xy(*a));f.SetDuplicatePadNumbersAreJumpers(True)
    for pos in [a,c]:
        z=p.PAD(f);z.SetNumber('1');z.SetAttribute(p.PAD_ATTRIB_PTH);z.SetShape(p.PAD_SHAPE_CIRCLE);z.SetSize(xy(size,size));z.SetDrillSize(xy(drill,drill));z.SetLayerSet(p.LSET.AllCuMask());z.SetPosition(xy(*pos));z.SetNet(net[n]);f.Add(z)
    line(f,*a,*c,p.F_Fab)
    f.Reference().SetVisible(False);f.Value().SetVisible(False);b.Add(f);fps[ref]=f

at('U2',1,109.5,78.5);at('U2',2,109.5,58.5);at('U2',3,160,78.5);at('U2',4,160,58.5)
outline('U2',108,56.5,54,23.5)
fps['U2'].SetValue('XL4015 54x23.5 measured underside')
fps['U2'].SetFPID(p.LIB_ID('Vortex','XL4015_MEASURED_50_5x20'))
for k,x,y in [(1,139.5,96.5),(2,149.5,96.5),(3,139.5,101),(4,149.5,101),(5,148.5,122.5),(6,141,122.5)]:at('U3',k,x,y)
outline('U3',137,93,16.5,34)
fps['U3'].SetValue('HW517 16.5x34 PWM=S4 GND=S1')
fps['U3'].SetFPID(p.LIB_ID('Vortex','HW517_MEASURED_10x4_5_SIGNAL_7_5'))
for k,y in [(5,93.82),(4,96.36),(1,98.9),(2,101.44),(3,103.98)]:at('J6',k,61.5,y)
for ref in ['J5','J6']:
    fps[ref].SetValue('ENCODER SAME DIRECTION GND 3V3 CLK DT SW')
    fps[ref].SetFPID(p.LIB_ID('Vortex',ref+'_SAME_ORIENTATION'))
fps['JP1'].SetPosition(xy(107.54,84.5))
at('JP1',1,107.54,84.5);at('JP1',2,105,84.5)
outline('JP1',103.5,83,5.54,3)

route('/+3V3',.6,[(61.5,81.12),(66.38,81.12),(74,73.5),(74.5,73.5)])
route('/+3V3',.6,[(61.5,81.12),(59.5,81.12),(58.7,81.92),(58.7,90.5)])
route('/+3V3',.6,[(58.7,97),(60.86,97),(61.5,96.36)])
jumper('W2','/+3V3',(58.7,90.5),(58.7,97),1.8,1)
for n,y1,y2 in [('/ENC2_CLK',98.9,93.82),('/ENC2_DT',101.44,96.36),('/ENC2_SW',103.98,98.9)]:route(n,.6,[(61.5,y1),(69.42,y1),(74.5,y2)])

route('/GND',1,[(61.5,78.58),(68.83,71.25),(75.5,71.25),(76.75,72.5),(76.75,74.5),(75.21,76.04),(74.5,76.04)])
route('/GND',1,[(61.5,78.58),(59,78.58),(56.5,81.08),(56.5,93.82),(61.5,93.82)])
route('/GND',1,[(74.5,76.04),(99.9,76.04)])
route('/GND',1,[(99.9,76.04),(99.04,76.04),(97.75,74.75),(97.75,68.25),(107.5,58.5),(109.5,58.5),(160,58.5)])
route('/GND',1,[(160,58.5),(164.58,63.08),(164.58,90.5)])
route('/GND',2,[(164.58,90.5),(164.58,129),(160,133.58),(103.08,133.58),(101,131.5),(97.5,131.5)])
route('/GND',2,[(81.66,131.5),(86.5,131.5),(90.5,135.5),(96,135.5),(97.5,134),(97.5,131.5)])
route('/GND',2,[(149.5,101),(149.5,104),(155.5,110)])
route('/GND',1,[(148.5,122.5),(149.5,121.5),(149.5,104)])
route('/GND',2,[(164.5,110),(164.58,110)])
jumper('W1','/GND',(155.5,110),(164.5,110),3.2,1.3)

route('/ESP_VIN',1,[(99.9,73.5),(103.5,73.5),(103.5,83),(105,84.5)])
route('/+5V',1,[(109.5,78.5),(109.5,82.54),(107.54,84.5)])
route('/PUMP_PWM',.6,[(99.9,91.28),(108.25,91.28),(139.47,122.5),(141,122.5)])
route('/PUMP_POS',2,[(124.5,88.5),(124.5,92),(135,92),(139.5,96.5)])
route('/PUMP_POS',2,[(124.5,92),(124.5,96.5)])
route('/PUMP_NEG',2,[(129.58,96.5),(134.08,101),(139.5,101)])
route('/PUMP_NEG',2,[(134.66,88.5),(140.5,88.5),(144.5,92.5),(144.5,97),(140.5,101),(139.5,101)])
route('/+12V',2,[(160,78.5),(160,90),(159.5,90.5),(153.5,96.5),(149.5,96.5)])
route('/+12V',2,[(159.5,90.5),(159.5,126.5),(155.75,130.25),(138.25,130.25),(136.75,128.75),(95.25,128.75),(92.5,131.5)])
route('/+12V',2,[(92.5,131.5),(89,128),(80.08,128),(76.58,131.5)])

for f in b.GetFootprints():
    f.Reference().SetVisible(False);f.Value().SetVisible(False)
    item=f.GetFPID().GetLibItemName()
    if item:f.SetFPID(p.LIB_ID('',item))
for y,t in [(78.58,'GND'),(81.12,'3V3'),(83.66,'CLK'),(86.2,'DT'),(88.74,'SW'),(93.82,'GND'),(96.36,'3V3'),(98.9,'CLK'),(101.44,'DT'),(103.98,'SW')]:label(t,65.2,y,.9)
label('J5 PUMP',62,74.8);label('J6 LIGHT',63,108)
label('ESP32 / USB',87,62);label('XL4015 5.0V',135,83)
label('JP1: REMOVE FOR USB',112.5,88,.8)
for x,y,t in [(139.5,90,'HW517'),(139.5,94,'OUT+'),(150,94,'VIN+'),(134.7,101,'OUT-'),(154.1,101,'VIN-'),(141,125,'PWM'),(148.5,125,'GND'),(161.5,94,'12V INPUT'),(126,103.5,'PUMP'),(129.5,85.5,'D1 1N5819'),(76,124,'R1 330R'),(76,127,'LED'),(94,135.5,'C1 1000uF')]:label(t,x,y,.85)
label('W1',158.5,113,.85);label('W2',57.5,88,.85)
label('MEASURED UNDERSIDE -> TOP; ENCODERS ALIGNED',111,140,1,p.Cmts_User)
for f in b.GetFootprints():
    for q in f.Pads():q.SetLocalClearance(p.FromMM(.5))
b.GetDesignSettings().m_MinClearance=p.FromMM(.5)
b.GetDesignSettings().m_CopperEdgeClearance=p.FromMM(.5)
b.BuildConnectivity()
p.SaveBoard(str(DEST),b)
pro={'meta':{'filename':'Vortex_revised.kicad_pro','version':1},'board':{'design_settings':{'rules':{'min_clearance':0.5,'min_copper_edge_clearance':0.5,'min_track_width':0.6,'min_through_hole_diameter':1.0}}},'net_settings':{'classes':[{'name':'Default','clearance':0.5,'track_width':0.6,'via_diameter':1.6,'via_drill':1.0,'microvia_diameter':0.3,'microvia_drill':0.1,'diff_pair_width':0.6,'diff_pair_gap':0.5,'diff_pair_via_gap':0.5}],'version':4}}
DEST.with_suffix('.kicad_pro').write_text(json.dumps(pro,indent=2),encoding='utf-8')
DEST.with_suffix('.kicad_dru').write_text('(version 1)\n(rule "Clearance 0.5 mm" (constraint clearance (min 0.5mm)))\n(rule "Copper edge 0.5 mm" (constraint edge_clearance (min 0.5mm)))\n',encoding='utf-8')
print(DEST)
