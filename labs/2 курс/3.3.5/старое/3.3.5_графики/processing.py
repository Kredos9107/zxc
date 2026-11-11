from pathlib import Path
import json,math,numpy as np
from PIL import Image,ImageDraw,ImageFont

P=Path(__file__).parent
r=json.loads((P/'analysis.json').read_text(encoding='utf-8'))
def fit(x,y):
    x,y=np.array(x,dtype=float),np.array(y,dtype=float)
    A=np.column_stack([x,np.ones(len(x))]);a,b=np.linalg.lstsq(A,y,rcond=None)[0]
    residual=y-a*x-b;cov=(residual@residual/(len(x)-2))*np.linalg.inv(A.T@A)
    return dict(k=float(a),b=float(b),sk=float(np.sqrt(cov[0,0])),sb=float(np.sqrt(cov[1,1])))
cu_fit=fit([s['I'] for s in r['Cu_omit']],[abs(s['fit']['k']) for s in r['Cu_omit']])
ag_fit=r['Ag_kI']
FONT=r'C:\Windows\Fonts\arial.ttf';BOLD=r'C:\Windows\Fonts\arialbd.ttf'
fonts={n:ImageFont.truetype(FONT,n+8) for n in [26,28,30,32,36]}
bold=ImageFont.truetype(BOLD,44)
BLUE='#205f9a';ORANGE='#d06a29';RED='#bc2525';GRAY='#777777';GREEN='#267755'
def num(x,n=2):return f'{x:.{n}f}'.replace('.',',')
class Panel:
    def __init__(self,draw,box,xlim,ylim,xticks,yticks,title,ylabel,xlabel='Модуль индукции, Тл'):
        self.d=draw;self.box=box;self.xlim=xlim;self.ylim=ylim
        l,t,rr,b=box
        draw.text((l,t-105),title,font=bold,fill='black')
        draw.text((l,t-55),ylabel,font=fonts[30],fill='black')
        for x in xticks:
            xx,_=self.xy(x,ylim[0]);draw.line((xx,t,xx,b),fill='#dddddd',width=2)
            txt=num(x,2);bb=draw.textbbox((0,0),txt,font=fonts[28]);draw.text((xx-(bb[2]-bb[0])/2,b+12),txt,font=fonts[28],fill='black')
        for y in yticks:
            _,yy=self.xy(xlim[0],y);draw.line((l,yy,rr,yy),fill='#dddddd',width=2)
            txt=num(y,2) if abs(ylim[1]-ylim[0])<4 else num(y,0)
            bb=draw.textbbox((0,0),txt,font=fonts[28]);draw.text((l-16-(bb[2]-bb[0]),yy-16),txt,font=fonts[28],fill='black')
        draw.rectangle(box,outline='black',width=3)
        draw.text((l,b+62),xlabel,font=fonts[30],fill='black')
    def xy(self,x,y):
        l,t,rr,b=self.box
        return (l+(x-self.xlim[0])/(self.xlim[1]-self.xlim[0])*(rr-l),b-(y-self.ylim[0])/(self.ylim[1]-self.ylim[0])*(b-t))
    def points(self,x,y,color=BLUE,kind='circle',radius=8,err=None):
        for i,(xx,yy) in enumerate(zip(x,y)):
            px,py=self.xy(xx,yy)
            if err is not None:
                val=err if np.isscalar(err) else err[i]
                _,top=self.xy(xx,min(self.ylim[1],yy+val));_,bottom=self.xy(xx,max(self.ylim[0],yy-val))
                self.d.line((px,top,px,bottom),fill=color,width=2)
                self.d.line((px-6,top,px+6,top),fill=color,width=2);self.d.line((px-6,bottom,px+6,bottom),fill=color,width=2)
            if kind=='diamond':
                self.d.polygon([(px,py-radius-3),(px+radius+3,py),(px,py+radius+3),(px-radius-3,py)],outline=color,width=4)
            elif kind=='cross':
                self.d.line((px-radius,py-radius,px+radius,py+radius),fill=color,width=4)
                self.d.line((px-radius,py+radius,px+radius,py-radius),fill=color,width=4)
            else:self.d.ellipse((px-radius,py-radius,px+radius,py+radius),fill=color,outline='white',width=1)
    def line(self,x,y,color=BLUE,width=4,dashed=False):
        pts=[self.xy(a,b) for a,b in zip(x,y)]
        if dashed:
            if len(pts)<10:pts=[tuple(v) for v in np.linspace(pts[0],pts[-1],200)]
            for i in range(0,len(pts)-4,9):self.d.line(pts[i:i+5],fill=color,width=width)
        else:self.d.line(pts,fill=color,width=width)
    def arrow(self,x,y,text,at,color=RED):
        px,py=self.xy(x,y);tx,ty=self.xy(*at)
        self.d.text((tx,ty),text,font=fonts[28],fill=color,spacing=7)
        ox,oy=tx+20,ty+90
        self.d.line((ox,oy,px,py),fill=color,width=3)
        v=np.array([ox-px,oy-py]);v=v/np.linalg.norm(v);n=np.array([-v[1],v[0]])
        self.d.polygon([(px,py),tuple(np.array([px,py])+19*v+7*n),tuple(np.array([px,py])+19*v-7*n)],fill=color)

im=Image.new('RGB',(2500,1250),'white');dr=ImageDraw.Draw(im)
dr.text((105,25),'Медь: две записи, которые нужно проверить по исходной таблице',font=bold,fill='black')
candidate_results=[]
for j,idx in enumerate([1,3]):
    raw=r['Cu'][idx];clean=r['Cu_omit'][idx];x=np.array(raw['B']);u=np.array(raw['u']);flag=4
    box=(125+j*1240,205,1200+j*1240,935)
    panel=Panel(dr,box,(0,1.14),(-12,6) if j==0 else (0,46),np.arange(0,1.11,.2),[-12,-9,-6,-3,0,3,6] if j==0 else [0,10,20,30,40],f"Ток образца {num(raw['I'],2)} А",'Показание U, деления')
    keep=np.arange(len(x))!=flag
    panel.points(x[keep],u[keep],BLUE)
    panel.points([x[flag]],[u[flag]],RED,'diamond',11)
    xp=np.linspace(min(x),max(x),300)
    panel.line(xp,(clean['fit']['k']*xp+clean['fit']['b'])/.04,BLUE)
    panel.line(xp,(raw['fit']['k']*xp+raw['fit']['b'])/.04,GRAY,dashed=True)
    expected=(clean['fit']['k']*x[flag]+clean['fit']['b'])/.04
    candidate_results.append(dict(I=raw['I'],Im=raw['im'][flag],recorded=int(u[flag]),expected=float(expected),residual_div=float(u[flag]-expected)))
    panel.arrow(x[flag],u[flag],f"Iм = {num(raw['im'][flag],2)} А; U = {val if (val:=int(u[flag])) else 0} дел.\nПрямая ожидает {num(expected,1)} дел.",(.38,4.6) if j==0 else (.10,30))
    lx=box[0]
    for yy,col,txt in [(1040,BLUE,'МНК без красной записи; свободный член'),(1085,GRAY,'МНК по всем записям; свободный член')]:
        dr.line((lx,yy+15,lx+65,yy+15),fill=col,width=4);dr.text((lx+80,yy),txt,font=fonts[26],fill=col)
dr.text((125,1150),'Красный ромб — число из текущей расшифровки. Если ячейка с «0» пустая, это пропуск, а не измерение.',font=fonts[28],fill=RED)
im.save(P/'copper_checks.png')

fwd=r['Ag'][-1];rev=r['Ag_reverse'];kf=fwd['fit'];kr=rev['fit']
im=Image.new('RGB',(2500,1300),'white');dr=ImageDraw.Draw(im)
dr.text((125,25),'Серебро: прямое и обратное поле при одном токе образца 0,95 А',font=bold,fill='black')
left=Panel(dr,(125,205,1200,950),(.10,1.13),(0,1.32),[.2,.4,.6,.8,1.0],[0,.2,.4,.6,.8,1.0,1.2],'Показания и две свободные прямые','Показание U, мкВ')
for s,col,kind in [(fwd,BLUE,'circle'),(rev,ORANGE,'cross')]:
    x=np.array(s['B']);y=np.array(s['u'])*.04
    left.points(x,y,col,kind,err=.075)
    xp=np.linspace(min(x),max(x),200);left.line(xp,s['fit']['k']*xp+s['fit']['b'],col)
right=Panel(dr,(1380,205,2440,950),(.10,1.13),(-.18,.18),[.2,.4,.6,.8,1.0],[-.15,-.10,-.05,0,.05,.10,.15],'Разность показаний в общих точках','U прямое − U обратное, мкВ')
xp=np.linspace(.1574,1.079,200)
right.line(xp,(kf['k']-kr['k'])*xp+kf['b']-kr['b'],GREEN)
right.line([.10,1.13],[0,0],GRAY,width=2)
right.line([.10,1.13],[.15,.15],GRAY,dashed=True);right.line([.10,1.13],[-.15,-.15],GRAY,dashed=True)
common=[i for i in fwd['im'] if i in rev['im']]
cx=[fwd['B'][fwd['im'].index(i)] for i in common]
cy=[(fwd['u'][fwd['im'].index(i)]-rev['u'][rev['im'].index(i)])*.04 for i in common]
right.points(cx,cy,GREEN)
dr.text((125,1055),f"Прямое поле: k = {num(kf['k'],4)} ± {num(kf['sk'],4)} мкВ/Тл",font=fonts[30],fill=BLUE)
dr.text((125,1105),f"Обратное поле: k = {num(kr['k'],4)} ± {num(kr['sk'],4)} мкВ/Тл",font=fonts[30],fill=ORANGE)
dr.text((1380,1055),'Серый пунктир: ±0,150 мкВ — сумма двух',font=fonts[30],fill=GRAY)
dr.text((1380,1105),'предельных приборных ошибок, а не ошибка МНК.',font=fonts[30],fill=GRAY)
dk=kr['k']-kf['k'];sdk=np.hypot(kf['sk'],kr['sk'])
dr.text((125,1190),f"Различие наклонов: {num(dk,4)} ± {num(sdk,4)} мкВ/Тл = {num(dk/sdk,2)} ошибки МНК.",font=fonts[30],fill='black')
dr.text((125,1240),'Это сравнение по случайному разбросу, а не по полной погрешности.',font=fonts[30],fill='black')
im.save(P/'silver_field_reversal.png')

cal=np.array(r['calibration']);asc=cal[:8];desc=cal[8:]
im=Image.new('RGB',(2500,1290),'white');dr=ImageDraw.Draw(im)
dr.text((125,25),'Градуировка: общий масштаб и увеличенное расхождение ходов',font=bold,fill='black')
left=Panel(dr,(125,205,1200,950),(0,1.30),(0,1150),[0,.2,.4,.6,.8,1,1.2],[0,200,400,600,800,1000],'Полная кривая','Модуль индукции, мТл','Ток электромагнита Iм, А')
left.points(asc[:,0],abs(asc[:,1]),BLUE);left.line(asc[:,0],abs(asc[:,1]),BLUE)
negative=desc[:,1]<0;left.points(desc[negative,0],abs(desc[negative,1]),ORANGE,'cross')
left.points([.75],[831],RED,'diamond',10)
valid=desc[:,0]>=asc[:,0].min();xx=desc[valid,0];yy=abs(desc[valid,1]);pred=np.interp(xx,asc[:,0],abs(asc[:,1]));delta=yy-pred
right=Panel(dr,(1380,205,2440,950),(.18,1.05),(-35,20),[.2,.4,.6,.8,1.0],[-30,-20,-10,0,10,20],'Обратный ход минус прямой','Разность модулей индукции, мТл','Ток электромагнита Iм, А')
right.line([.18,1.05],[0,0],GRAY,width=2)
right.points(xx[desc[valid,1]<0],delta[desc[valid,1]<0],ORANGE,'cross')
right.points([.75],[831-np.interp(.75,asc[:,0],abs(asc[:,1]))],RED,'diamond',10)
res=[]
for i in [.92,.97]:
    j=list(xx).index(i);rel=delta[j]/pred[j]*100;res.append(dict(Im=i,forward_interpolated=float(pred[j]),reverse=float(yy[j]),difference_mT=float(delta[j]),difference_percent=float(rel)))
    right.arrow(i,delta[j],f"{num(i,2)} А: {num(delta[j],2)} мТл\n({num(rel,2)} %)",(.30,-8) if i==.92 else (.48,-25),ORANGE)
dr.text((125,1055),'Синий — прямой; оранжевый — обратный ход.',font=fonts[30],fill='black')
dr.text((125,1105),'Красный ромб: модуль записи +831 мТл.',font=fonts[30],fill=RED)
dr.text((1380,1055),'Вычтен прямой ход (интерполяция).',font=fonts[30],fill='black')
dr.text((1380,1105),'Точка 0,12 А вне диапазона сравнения ходов.',font=fonts[30],fill='black')
dr.text((125,1190),'0,75 А: ожидается 830,12 мТл; модуль 831 мТл отличается на 0,11 %. Спорный знак.',font=fonts[30],fill='black')
im.save(P/'calibration_checks.png')

# Both k(I) regressions now have independently fitted intercepts.
im=Image.new('RGB',(1600,1020),'white');dr=ImageDraw.Draw(im)
pan=Panel(dr,(145,155,1510,760),(0,1.15),(0,1.5),[0,.2,.4,.6,.8,1.0],[0,.25,.5,.75,1,1.25,1.5],'Наклоны полевых зависимостей','Модуль наклона, мкВ/Тл','Ток образца I, А')
for ss,ff,col,lab in [(r['Ag'],ag_fit,BLUE,'Ag'),(r['Cu_omit'],cu_fit,ORANGE,'Cu')]:
    x=np.array([s['I'] for s in ss]);y=np.array([abs(s['fit']['k']) for s in ss]);err=np.array([s['fit']['sk'] for s in ss])
    pan.points(x,y,col,err=err)
    xp=np.linspace(x.min(),x.max(),200);pan.line(xp,ff['k']*xp+ff['b'],col)
dr.text((145,875),'Ag: k = α I + β; α и β найдены независимо',font=fonts[30],fill=BLUE)
dr.text((145,925),'Cu: k = α I + β; α и β найдены независимо',font=fonts[30],fill=ORANGE)
im.save(P/'slopes_free.png')

e=1.602176634e-19;results={}
for metal,ff,h,a,l,U in [('Ag',ag_fit,9e-5,.011,.015,360e-6),('Cu',cu_fit,5e-5,.008,.006,295e-6)]:
    RH=ff['k']*h*1e-6;sRH=ff['sk']*h*1e-6;n=1/(e*RH);sig=l/(U*a*h)
    results[metal]=dict(h=h,a=a,l=l,U34=U,fit=ff,RH=RH,sRH_stat=sRH,n=n,sn_stat=n*sRH/RH,sigma=sig,dsigma_instrument=sig*(.025+11.25e-6/U),rho=1/sig,mu=sig*RH*1e4)
results['Zn']=dict(RH=r['RH_Zn'],sRH_stat=r['Zn']['fit']['sk']*8e-5*1e-6,n=r['nH_Zn'],sn_stat=r['nH_Zn']*r['Zn']['fit']['sk']/abs(r['Zn']['fit']['k']))
results['calibration_residuals']=res;results['candidate_records']=candidate_results
results['Ag_reversal']=dict(dk=dk,sdk=float(sdk),stat_sigmas=float(dk/sdk),relative_percent=dk/kf['k']*100,common_Im=common,dU_microvolts=cy)
(P/'revision_results.json').write_text(json.dumps(results,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(results,ensure_ascii=False,indent=2))
