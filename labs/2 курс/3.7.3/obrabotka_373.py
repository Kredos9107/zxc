# Обработка 3.7.3 «Длинные линии». Формулы по описанию (номера в комментариях), переписаны в СИ.
# Данные: журналы (мой и напарника), курсоры и автоизмерения Vpp на сохранённых осциллограммах.
# Графики: экспериментальные данные только круглыми точками.
import numpy as np, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
import matplotlib.ticker as mt                 # десятичная запятая на осях
_fmt=mt.ScalarFormatter.__call__; mt.ScalarFormatter.__call__=lambda self,x,pos=None: _fmt(self,x,pos).replace('.',',')
plt.rcParams.update({'font.size':13,'axes.grid':True,'grid.alpha':0.3,'figure.dpi':150,'savefig.bbox':'tight'})
B,R,G,K='#1f5fa8','#d0542b','#2e8b57','#555555'
c=2.998e8; mu0=4e-7*np.pi
l=50.52; dl=0.2; Z0=50.0; d=1.37e-3; D=4.6e-3
out=[]
P=lambda *a: (print(*a), out.append(' '.join(str(x) for x in a)))
def lin(x,y):
    # x нормируется на max|x|, иначе при x ~ 1e16 матрица плохо обусловлена и свободный член теряется
    q=np.max(np.abs(x)); A=np.vstack([x/q,np.ones_like(x)]).T; s,_,_,_=np.linalg.lstsq(A,y,rcond=None)
    s=np.array([s[0]/q,s[1]])
    r=y-(s[0]*x+s[1]); n=len(x); sa=np.sqrt(np.sum(r**2)/(n-2)/np.sum((x-x.mean())**2)); sb=sa*np.sqrt(np.mean(x**2))
    return s[0],s[1],sa,sb

# ---------- I. Резонансные частоты (Δφ = 2πm) -> V = l·Δν ----------
m=np.arange(1,8)
sets={'синус, R = 50 Ом':np.array([3.940,7.910,11.91,15.88,19.87,23.87,27.85]),
      'синус, R = 1 МОм':np.array([4,8,12,16,20,24,28.]),
      'импульсы, 50 Ом и 1 МОм':np.array([4,8,12,16,20.])}
fig,ax=plt.subplots(figsize=(6.8,4.6)); cols=[B,R,G]; msz=[12,8.5,5]   # точки разного размера, чтобы совпадающие были видны
for (lab,fr),cl,ms_ in zip(sets.items(),cols,msz):
    mm=np.arange(1,len(fr)+1); a,b,sa,sb=lin(mm,fr)
    P(f'I {lab}: Δν={a:.4f}±{sa:.4f} МГц, b={b:.3f}±{sb:.3f} МГц, V=l·Δν={l*a*1e6:.4e}')
    ax.plot(mm,fr,'o',color=cl,ms=ms_,label=lab,zorder=3)
a1r,b1r,sa1r,sb1r=lin(m,sets['синус, R = 50 Ом'])
mx=np.linspace(0,7.5,10); ax.plot(mx,a1r*mx+b1r,'-',color=K,lw=1.5,label=f'МНК: Δν = {a1r:.3f} МГц'.replace('.',','),zorder=2)
ax.set_xlabel('номер резонанса m'); ax.set_ylabel('$\\nu_m$, МГц'); ax.set_xlim(0,7.5); ax.set_ylim(0,30); ax.legend(fontsize=10)
ax.set_title('Резонансные частоты кабеля')
fig.savefig('out/cable_res.png')
Vres=l*a1r*1e6; dVres=Vres*np.hypot(sa1r/a1r,dl/l); P(f'I V_ф по резонансам = {Vres:.4e} ± {dVres:.1e}; τ=1/Δν={1e3/a1r:.1f} нс')

# ---------- II. ФЧХ и АЧХ ----------
f7=np.array([1,5,10,15,20,25,30.]); dx=np.array([748,149.6,48.0,15.2,48.8,28.5,15.3])
T=1e3/f7; dxp=(-dx)%T; n=np.round((251-dxp)/T); tau=dxp+n*T
P('II Δx\' (нс):',dxp.round(1),' n:',n,' τ (нс):',tau.round(1),' τ ср=',tau.mean().round(1),'±',(tau.std(ddof=1)/np.sqrt(7)).round(1))
k7=2*np.pi*f7*1e6*tau*1e-9/l
fr=np.array([3.94,7.91,11.91,27.85]); kr=2*np.pi*np.array([1,2,3,7])/l
fA=np.array([1,3.94,5,7.91,10,11.91,15,20,25,27.85,30.]); wA=2*np.pi*fA*1e6
V1=np.array([2.800,2.664,2.729,2.664,2.729,2.642,2.763,2.762,2.800,2.651,2.738]); V2=np.array([24.80,23.87,23.64,22.87,22.84,21.80,21.25,20.90,19.67,19.11,18.99])/10
alpha=np.log(V1/V2)/l                                   # (28)
kd=dict(zip(list(f7)+list(fr),list(k7)+list(kr))); kA=np.array([kd[x] for x in fA])   # (29)
P('II k (1/м):',kA.round(4)); P('II α (1e-3 1/м):',(alpha*1e3).round(2)); P('II α (дБ/100м):',(20*np.log10(V1/V2)/l*100).round(1))
# ФЧХ по второму журналу
fJ=np.array([1,15,21,27,33,39.]); dxJ=np.array([378,59.0,17.8,32.2,11.0,22.1])
q=-fJ*dxJ*1e-3; nJ=np.round(0.25*fJ-q); cyc=q+nJ
a4,b4,sa4,sb4=lin(fJ,cyc); P(f'II ФЧХ журнал: τ={a4*1e3:.1f}±{sa4*1e3:.1f} нс, пост. сдвиг {b4*360:.0f}±{sb4*360:.0f}°')
fig,ax=plt.subplots(figsize=(6.8,4.6))
ax.plot(fA,kA*l/(2*np.pi),'o',color=B,ms=8,label='курсоры и резонансы')
ff=np.linspace(0,40,10); ax.plot(ff,ff*1e6*l/Vres,'-',color=R,lw=1.5,label='$\\Delta\\varphi/2\\pi=\\nu l/V_ф$')
ax.set_xlabel('ν, МГц'); ax.set_ylabel('Δφ / 2π'); ax.legend(fontsize=10); ax.set_title('ФЧХ кабеля')
fig.savefig('out/cable_phase.png')

# ---------- Обработка, часть I: y1 = k² − α² от x1 = ω²  (30)–(32) ----------
y1=kA**2-alpha**2; x1=wA**2
a1,b1,sa1,sb1=lin(x1,y1)
Vf=1/np.sqrt(a1); dVf=Vf*np.hypot(0.5*sa1/a1,dl/l)
Lx=Z0/Vf; Cx=1/(Z0*Vf)
em=(c/Vf)**2; me=(Z0/(60*np.log(D/d)))**2
P(f'Ч.I: наклон L_xC_x={a1:.4e}±{sa1:.1e} с²/м², своб.член {b1:.1e}±{sb1:.1e} 1/м² -> V_ф={Vf:.4e}±{dVf:.1e}')
P(f'Ч.I: L_x={Lx*1e9:.1f} нГн/м, C_x={Cx*1e12:.1f} пФ/м, εμ={em:.3f}, ε={np.sqrt(em/me):.2f}, μ={np.sqrt(em*me):.3f}')
fig,ax=plt.subplots(figsize=(6.8,4.6))
ax.plot(x1/1e16,y1,'o',color=B,ms=8,label='эксперимент')
xx=np.linspace(0,x1.max()*1.05,10); ax.plot(xx/1e16,a1*xx+b1,'-',color=R,lw=1.5,label=f'МНК: наклон $L_xC_x$ = {a1*1e17:.3f}'.replace('.',',')+f'·10$^{{-17}}$ с²/м²')
ax.set_xlabel('$x_1=\\omega^2$, $10^{16}$ с$^{-2}$'); ax.set_ylabel('$y_1=k^2-\\alpha^2$, м$^{-2}$'); ax.legend(fontsize=10)
ax.set_title('Определение $L_xC_x$ (30)–(32)')
fig.savefig('out/cable_y1.png')

# ---------- Обработка, часть II ----------
x2=np.sqrt(wA); a3,b3,sa3,sb3=lin(x2,alpha)          # (40)–(42), в СИ x2=√ω
sigA=mu0/(2*(np.pi*d*Z0*a3)**2); dsigA=2*sigA*sa3/a3
P(f'Ч.II А: наклон {a3:.3e}±{sa3:.1e} с^1/2/м, b={b3:.1e}±{sb3:.1e} -> σ={sigA:.2e}±{dsigA:.1e} (по (37)); со станд. R_s=1/(σδ): {sigA/4:.2e}')
fig,ax=plt.subplots(figsize=(6.8,4.6))
ax.plot(x2/1e3,alpha*1e3,'o',color=B,ms=8,label='эксперимент')
xx=np.linspace(0,x2.max()*1.05,10); ax.plot(xx/1e3,(a3*xx+b3)*1e3,'-',color=R,lw=1.5,label=f'МНК: наклон {a3*1e7:.2f}'.replace('.',',')+f'·10$^{{-7}}$ с$^{{1/2}}$/м')
ax.set_xlabel('$x_2=\\sqrt{\\omega}$, $10^3$ с$^{-1/2}$'); ax.set_ylabel('$y_2=\\alpha$, $10^{-3}$ м$^{-1}$'); ax.legend(fontsize=10)
ax.set_title('Метод А (40)–(43)')
fig.savefig('out/cable_alpha.png')
y3=alpha*kA; x3=wA**1.5; a5,b5,sa5,sb5=lin(x3,y3)   # (45)–(47)
sigB=mu0*Cx**2/(2*(np.pi*d*a5)**2); dsigB=sigB*np.hypot(2*sa5/a5,0.02)
P(f'Ч.II Б: наклон {a5:.3e}±{sa5:.1e}, b={b5:.1e}±{sb5:.1e} -> σ={sigB:.2e}±{dsigB:.1e}; станд.: {sigB/4:.2e}')
fig,ax=plt.subplots(figsize=(6.8,4.6))
ax.plot(x3/1e12,y3*1e3,'o',color=B,ms=8,label='эксперимент')
xx=np.linspace(0,x3.max()*1.05,10); ax.plot(xx/1e12,(a5*xx+b5)*1e3,'-',color=R,lw=1.5,label=f'МНК: наклон {a5*1e15:.2f}'.replace('.',',')+f'·10$^{{-15}}$ с$^{{3/2}}$/м$^2$')
ax.set_xlabel('$x_3=\\omega^{3/2}$, $10^{12}$ с$^{-3/2}$'); ax.set_ylabel('$y_3=\\alpha k$, $10^{-3}$ м$^{-2}$'); ax.legend(fontsize=10)
ax.set_title('Метод Б (45)–(48)')
fig.savefig('out/cable_methodB.png')

# ---------- Линия без нагрузки: отношение амплитуд вход/конец ----------
fo=np.array([1,5,10,15,20,25,30.])
U1o=np.array([0.268,0.572,1.823,1.025,1.741,1.067,1.691]); U2o=np.array([3.720,3.209,1.852,2.134,1.725,2.289,1.648])
r_exp=U1o/U2o; tt=1e3/a1r*1e-9
kl=2*np.pi*fo*1e6*tt; aL=(a3*np.sqrt(2*np.pi*fo*1e6)+b3)*l
r_th=np.sqrt(np.cos(kl)**2+np.sinh(aL)**2)
P('Откр. линия ντ:',(fo*1e6*tt).round(3)); P('  U1/U2 эксп:',r_exp.round(2)); P('  теория с затуханием:',r_th.round(2)); P('  без затухания |cos kl|:',np.abs(np.cos(kl)).round(2))
fig,ax=plt.subplots(figsize=(6.8,4.6))
fx=np.linspace(0.3,31,800); klx=2*np.pi*fx*1e6*tt; aLx=(a3*np.sqrt(2*np.pi*fx*1e6)+b3)*l
ax.plot(fx,np.sqrt(np.cos(klx)**2+np.sinh(aLx)**2),'-',color=R,lw=1.5,label='теория: $\\sqrt{\\cos^2 kl+\\mathrm{sh}^2\\alpha l}$')
ax.plot(fo,r_exp,'o',color=B,ms=8,label='эксперимент $U_{вх}/U_{кон}$')
ax.set_xlabel('ν, МГц'); ax.set_ylabel('$U_{вх}/U_{кон}$'); ax.legend(fontsize=10,loc='lower right'); ax.set_title('Линия без нагрузки (1 МОм)')
fig.savefig('out/cable_open.png')

# ---------- Модель ----------
L=1.5e-3; C=47e-9; nu0=1/(np.pi*np.sqrt(L*C)); R0=np.sqrt(L/C)      # (*), (**)
P(f'M nu0={nu0:.0f} Гц, R0={R0:.1f} Ом (подобрано 178,2)')
fm=np.array([2,7,12,15,18,21,26,32,38.])*1e3
d5=np.array([80.0,32.4,56.4,41.2,45.8,3.0,12.2,24.6,4.1])*1e-6
d9=np.array([95.0,92.8,14.8,7.2,26.2,38.0,14.9,6.6,2.1])*1e-6
dp=((d9-d5)*fm)%1
dpu=dp.copy()                                 # развёртка по монотонности: θ растёт с ν
for i in range(1,len(dpu)):
    while dpu[i]<dpu[i-1]-0.05: dpu[i]+=1      # допуск 0,05 периода на погрешность отсчёта
assert np.all(2*np.pi*dpu/4<=np.pi+0.05)       # и θ не больше π
th_e=2*np.pi*dpu/4
th_lin=2*np.pi*fm*np.sqrt(L*C)                 # как (27), (29) для кабеля: θ = ω√(LC)
P('M theta_эксп (рад):',th_e.round(3)); P('M theta=ω√(LC) (рад):',th_lin.round(3))
fig,ax=plt.subplots(figsize=(6.5,4.6))
fx=np.linspace(0,40e3,10); ax.plot(fx/1e3,2*np.pi*fx*np.sqrt(L*C),'--',color=K,lw=1.5,label='без дисперсии: $\\theta=\\omega\\sqrt{LC}$',zorder=2)
ax.axvline(nu0/1e3,color=R,lw=1.2,ls=':',label='$\\nu_0=1/(\\pi\\sqrt{LC})$'); ax.axhline(np.pi,color='gray',lw=1,ls=':')
ax.text(0.8,np.pi+0.07,'θ = π',color='gray',fontsize=11)
ax.plot(fm/1e3,th_e,'o',color=B,ms=8,label='эксперимент (выход 9 − выход 5)/4',zorder=3)
ax.set_xlim(0,40); ax.set_ylim(0,3.6); ax.set_xlabel('ν, кГц'); ax.set_ylabel('θ, рад'); ax.legend(fontsize=10,loc='lower right'); ax.set_title('Сдвиг фазы на звено цепочки LC')
fig.savefig('out/model_dispersion.png')
# распределение амплитуды вдоль цепочки, R = 0: 2A = A|sin θ(11-n)|, узел на закороченном конце (n = 11).
# По точкам находим θ и масштаб A (единицы 2A относительные). θ и π-θ дают одинаковые значения в целых n,
# берём то, что ближе к θ, измеренному по сдвигу фаз (рост θ с частотой).
from scipy.optimize import curve_fit
g=lambda m_,A,t: A*np.abs(np.sin(t*m_))
sw={2.89:([10,9,8,7,6,5,4,3],[8.50,21.4,34.8,47.6,59.0,67.4,74.4,78.2]),
    12.83:([3,4,5,6,7,8],[34.6,70.4,72.6,36.4,30.2,68.8]),
    27.89:([8,7,6,5,4,3],[20.6,61.8,24.2,66.0,41.2,73.2])}
fig,ax=plt.subplots(1,3,figsize=(15,4.3),sharey=True)
for a_,(fr,(nn,U)) in zip(ax,sw.items()):
    nn=np.array(nn);U=np.array(U,float); mm=11-nn
    best=None
    for t0 in np.linspace(0.05,np.pi-0.05,300):
        try:
            p,cv=curve_fit(g,mm,U,p0=[U.max(),t0]); r=np.sum((g(mm,*p)-U)**2)
            if 0<p[1]<np.pi and (best is None or r<best[0]-1e-9): best=(r,p,cv)
        except Exception: pass
    r,p,cv=best; th,dth=p[1],np.sqrt(cv[1,1]); th9=np.interp(fr*1e3,fm,th_e)
    if abs(np.pi-th-th9)<abs(th-th9): th=np.pi-th
    lin=2*np.pi*fr*1e3*np.sqrt(L*C)
    P(f'M стоячая {fr} кГц: theta по точкам={th:.3f}±{dth:.3f}, по сдвигу фаз≈{th9:.2f}, ω√(LC)={lin:.3f}, rms={np.sqrt(r/len(U)):.1f}')
    xs=np.linspace(1,11,300)
    a_.plot(xs,p[0]*np.abs(np.sin(th*(11-xs))),'-',color=R,lw=2,label='$|\\sin\\theta(11-n)|$, θ по точкам',zorder=2)
    a_.plot(nn,U,'o',color=B,ms=8,label='эксперимент',zorder=3)
    a_.set_title(f'ν = {fr} кГц,  θ = {th:.2f}'.replace('.',',')); a_.set_xlabel('номер выхода n'); a_.set_xticks(range(1,12))
ax[0].set_ylabel('2A, отн. ед.'); ax[0].legend(fontsize=10,loc='lower left')
fig.savefig('out/model_standing.png')

# п.6*: амплитуда на 5-й клемме от частоты, R=0
f6=np.array([2.89,3.03,4.09,4.27,4.49,6,8,10,12,14,16,18.]); U6=np.array([21.6,23.4,60.4,88.4,103.6,62.0,54.0,91.6,65.6,93.6,73.6,70.4])
fig,ax=plt.subplots(figsize=(6.5,4.3))
ax.plot(f6,U6,'o-',color=B,ms=7,lw=1.2)
ax.set_xlabel('ν, кГц'); ax.set_ylabel('2A, отн. ед.'); ax.set_title('Амплитуда на 5-й клемме, R = 0')
fig.savefig('out/model_klemma5.png')
open('out/results.txt','w').write('\n'.join(out))
