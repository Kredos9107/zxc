# -*- coding: utf-8 -*-
"""
Лабораторная работа 3.3.5 «Эффект Холла в металлах» — полная обработка.

Запуск:  python processing_335.py
Результат: графики *.png, results.json и results.txt в этой же папке.

Нумерация функций и комментариев совпадает с пунктами 13–20 лабника
(раздел «Обработка результатов»). Все исходные числа — в data_335.json.
"""
from pathlib import Path
import json
import math

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = Path(__file__).resolve().parent
D = json.loads((HERE / "data_335.json").read_text(encoding="utf-8"))

E = 1.602176634e-19          # Кл, модуль заряда электрона
S = D["hall_range_uV"] / D["scale_divisions"]       # мкВ/дел для холловских серий
S34 = D["u34_range_uV"] / D["scale_divisions"]      # мкВ/дел для U34

plt.rcParams.update({
    "font.family": "DejaVu Sans", "font.size": 11, "axes.grid": True,
    "grid.color": "#e3e3e3", "axes.spines.top": False, "axes.spines.right": False,
    "savefig.dpi": 200, "savefig.bbox": "tight", "legend.frameon": False,
})
COLORS = ["#1f4e79", "#2e75b6", "#3c9d9b", "#5aa832", "#c9a227", "#e07b28", "#c0392b"]


def ols(x, y):
    """МНК y = k x + b, свободный член не фиксирован. Возвращает k, b, s_k, s_b, r2."""
    x, y = np.asarray(x, float), np.asarray(y, float)
    n = len(x)
    A = np.column_stack([x, np.ones(n)])
    (k, b), *_ = np.linalg.lstsq(A, y, rcond=None)
    res = y - (k * x + b)
    s2 = res @ res / (n - 2)
    cov = s2 * np.linalg.inv(A.T @ A)
    r2 = 1 - (res @ res) / np.sum((y - y.mean()) ** 2)
    return dict(k=float(k), b=float(b), sk=float(math.sqrt(cov[0, 0])),
                sb=float(math.sqrt(cov[1, 1])), r2=float(r2), n=n)


def ols0(x, y):
    """МНК через начало координат y = k x (проверочный вариант)."""
    x, y = np.asarray(x, float), np.asarray(y, float)
    k = (x @ y) / (x @ x)
    res = y - k * x
    sk = math.sqrt(res @ res / (len(x) - 1) / (x @ x))
    return dict(k=float(k), sk=float(sk))


def fmt(x, n=3):
    return f"{x:.{n}f}".replace(".", ",")


# ---------------------------------------------------------------------------
# П. 13. Калибровка электромагнита B(Iм)
# ---------------------------------------------------------------------------
fwd = np.array(D["calibration"]["forward"], float)   # прямой ход (рост тока)
rev = np.array(D["calibration"]["reverse"], float)   # обратный ход (спад тока)
fwd_abs = np.column_stack([fwd[:, 0], np.abs(fwd[:, 1])])
rev_abs = np.column_stack([rev[:, 0], np.abs(rev[:, 1])])

# Узлы интерполяции: Iм = 0 → B = 0 (поле при выключенном магните считаем нулевым),
# 0,12 А — единственное измерение (с обратного хода), далее весь прямой ход.
# Прямой ход выбран потому, что все холловские серии снимались при медленном
# УВЕЛИЧЕНИИ тока магнита (требование п. 6 лабника) — то есть на том же ходе.
nodes = np.vstack([[0.0, 0.0], rev_abs[rev_abs[:, 0] == 0.12], fwd_abs])
nodes = nodes[np.argsort(nodes[:, 0])]


def B_of_I(im):
    """Модуль индукции, Тл, по току магнита, А (линейная интерполяция)."""
    return np.interp(np.asarray(im, float), nodes[:, 0], nodes[:, 1]) / 1000.0


# расхождение ходов
rev_in = rev_abs[(rev_abs[:, 0] >= fwd[:, 0].min())]
hyst = [dict(Im=float(i), B_rev=float(b), B_fwd=float(np.interp(i, fwd_abs[:, 0], fwd_abs[:, 1])),
             diff=float(b - np.interp(i, fwd_abs[:, 0], fwd_abs[:, 1])),
             rel=float((b - np.interp(i, fwd_abs[:, 0], fwd_abs[:, 1])) /
                       np.interp(i, fwd_abs[:, 0], fwd_abs[:, 1]) * 100))
        for i, b in rev_in]

fig, ax = plt.subplots(figsize=(7.2, 4.6))
xs = np.linspace(0, 1.26, 400)
ax.plot(xs, B_of_I(xs) * 1000, color="#1f4e79", lw=1.4, label="интерполяция (прямой ход)")
ax.plot(fwd_abs[:, 0], fwd_abs[:, 1], "o", color="#1f4e79", ms=6, label="прямой ход (Iм растёт)")
m = rev[:, 1] < 0
ax.plot(rev_abs[m, 0], rev_abs[m, 1], "s", mfc="none", mec="#e07b28", mew=1.6, ms=7,
        label="обратный ход (Iм убывает)")
ax.plot(rev_abs[~m, 0], rev_abs[~m, 1], "D", mfc="none", mec="#c0392b", mew=1.6, ms=8,
        label="0,75 А: записано «+831» (знак — описка)")
ax.set_xlabel("Ток электромагнита Iм, А")
ax.set_ylabel("|B|, мТл")
ax.set_xlim(0, 1.32); ax.set_ylim(0, 1180)
ax.legend(loc="lower right")
ax.set_title("П. 13. Калибровочная кривая электромагнита")
fig.savefig(HERE / "fig1_calibration.png"); plt.close(fig)


# ---------------------------------------------------------------------------
# П. 14. ЭДС Холла U⊥ = U24 − U0 и наклоны k = dU⊥/dB
# ---------------------------------------------------------------------------
def prepare(series, zero_from_im0):
    """Возвращает словарь с B, U⊥ (мкВ) и фитом. series — запись из data_335.json."""
    im = np.array(series["Im"], float)
    u = np.array(series["U_div"], float)
    excl = np.zeros(len(im), bool)
    for j in series.get("exclude", []):
        excl[j] = True
    if zero_from_im0 and np.any(im == 0):
        u0 = float(u[im == 0][0])          # измеренный отсчёт при выключенном магните
        u0_src = "отсчёт при Iм = 0"
    else:
        u0 = float(series["U0_div"])       # записанный в шапке U0
        u0_src = "записанный U0"
    sign = series.get("polarity", 1)       # −1, если K2 стоял в положении 2
    B = B_of_I(im)
    Uperp = sign * (u - u0) * S            # мкВ
    f = ols(B[~excl], Uperp[~excl])
    f_all = ols(B, Uperp) if excl.any() else None
    return dict(I=series["I"], Im=im.tolist(), U_div=u.tolist(), U0=u0, U0_src=u0_src,
                polarity=sign, B=B.tolist(), Uperp=Uperp.tolist(), excl=excl.tolist(),
                fit=f, fit_all=f_all)


AG = [prepare(s, False) for s in D["Ag"]]
CU = [prepare(s, True) for s in D["Cu"]]
AG_REV = prepare(D["Ag_reverse"], False)
CU_REV = prepare(D["Cu_reverse"], True)
ZN = prepare(D["Zn"], True)

# предсказание прямой в исключённых точках меди
for c in CU:
    for j, e in enumerate(c["excl"]):
        if e:
            pred = (c["fit"]["k"] * c["B"][j] + c["fit"]["b"]) / S / c["polarity"] + c["U0"]
            c.setdefault("excl_info", []).append(
                dict(Im=c["Im"][j], recorded=c["U_div"][j], expected_div=float(pred)))


def family_plot(series, title, fname, metal):
    fig, ax = plt.subplots(figsize=(7.6, 5.0))
    for i, s in enumerate(series):
        col = COLORS[int(i * (len(COLORS) - 1) / max(1, len(series) - 1))]
        B = np.array(s["B"]); U = np.array(s["Uperp"]); ex = np.array(s["excl"])
        ax.plot(B[~ex], U[~ex], "o", color=col, ms=5.5,
                label=f"I = {fmt(s['I'], 2)} А:  k = {fmt(s['fit']['k'], 3)} мкВ/Тл")
        if ex.any():
            ax.plot(B[ex], U[ex], "D", mfc="none", mec="#c0392b", mew=1.6, ms=8)
        xx = np.linspace(0, B.max() * 1.02, 50)
        ax.plot(xx, s["fit"]["k"] * xx + s["fit"]["b"], color=col, lw=1.2)
    if any(np.any(s["excl"]) for s in series):
        ax.plot([], [], "D", mfc="none", mec="#c0392b", mew=1.6, ms=8,
                label="исключённые записи (описки, см. текст)")
    ax.axhline(0, color="#999", lw=0.8)
    ax.set_xlabel("|B|, Тл"); ax.set_ylabel("U⊥ = U₂₄ − U₀, мкВ")
    ax.set_xlim(0, 1.15)
    ax.legend(loc="upper left", fontsize=9.5)
    ax.set_title(title)
    fig.savefig(HERE / fname); plt.close(fig)


family_plot(AG, "П. 14. Серебро: семейство U⊥(B) при разных токах I", "fig2_Ag_family.png", "Ag")
family_plot(CU, "П. 14. Медь: семейство U⊥(B) (полярность приведена к K₂ = 1)", "fig3_Cu_family.png", "Cu")


# ---------------------------------------------------------------------------
# П. 8. Обратное направление поля — проверка
# ---------------------------------------------------------------------------
def reversal(fw, rv):
    common = [i for i in fw["Im"] if i in rv["Im"]]
    d = []
    for i in common:
        a = fw["Uperp"][fw["Im"].index(i)]; b = rv["Uperp"][rv["Im"].index(i)]
        if not fw["excl"][fw["Im"].index(i)]:
            d.append(dict(Im=i, fwd=a, rev=b, half_sum=(a + b) / 2, diff=a - b))
    kf, kr = fw["fit"]["k"], rv["fit"]["k"]
    return dict(k_fwd=kf, sk_fwd=fw["fit"]["sk"], k_rev=kr, sk_rev=rv["fit"]["sk"],
                k_mean=(kf + kr) / 2, rel_diff=(kr - kf) / kf * 100,
                n_sigma=(kr - kf) / math.hypot(fw["fit"]["sk"], rv["fit"]["sk"]),
                points=d, max_abs_diff=max(abs(p["diff"]) for p in d))


REV_AG = reversal(AG[-1], AG_REV)
REV_CU = reversal(CU[-1], CU_REV)

fig, axs = plt.subplots(1, 2, figsize=(11, 4.4))
for ax, fw, rv, r, name in [(axs[0], AG[-1], AG_REV, REV_AG, "Ag, I = 0,95 А"),
                            (axs[1], CU[-1], CU_REV, REV_CU, "Cu, I = 1,07 А")]:
    for s, col, mk, lab in [(fw, "#1f4e79", "o", "прямое поле"), (rv, "#e07b28", "s", "обратное поле")]:
        B = np.array(s["B"]); U = np.array(s["Uperp"]); ex = np.array(s["excl"])
        ax.errorbar(B[~ex], U[~ex], yerr=0.5 * S, fmt=mk, color=col, ms=5.5, capsize=2,
                    mfc=col if mk == "o" else "none", label=f"{lab}: k = {fmt(s['fit']['k'], 3)} мкВ/Тл")
        xx = np.linspace(0, B.max(), 50)
        ax.plot(xx, s["fit"]["k"] * xx + s["fit"]["b"], color=col, lw=1.1)
    ax.set_title(name); ax.set_xlabel("|B|, Тл"); ax.set_ylabel("|U⊥|, мкВ")
    ax.legend(loc="upper left", fontsize=9.5); ax.set_xlim(0, 1.15)
fig.suptitle("П. 8. Измерения при двух направлениях поля (планки — ±½ деления)", y=1.02)
fig.savefig(HERE / "fig4_reversal.png"); plt.close(fig)


# ---------------------------------------------------------------------------
# П. 15. Зависимость k(I), постоянная Холла Ag и Cu: R_H = h · dk/dI
# ---------------------------------------------------------------------------
GEOM = D["geometry_mm"]
KI = {}
for metal, ser in [("Ag", AG), ("Cu", CU)]:
    I = np.array([s["I"] for s in ser]); k = np.array([s["fit"]["k"] for s in ser])
    sk = np.array([s["fit"]["sk"] for s in ser])
    f = ols(I, k); f0 = ols0(I, k)
    h = GEOM[metal]["h"] * 1e-3
    KI[metal] = dict(I=I.tolist(), k=k.tolist(), sk=sk.tolist(), fit=f, fit0=f0,
                     RH=f["k"] * 1e-6 * h, sRH_stat=f["sk"] * 1e-6 * h,
                     RH0=f0["k"] * 1e-6 * h)

fig, ax = plt.subplots(figsize=(7.2, 4.6))
for metal, col, mk in [("Ag", "#1f4e79", "o"), ("Cu", "#e07b28", "s")]:
    r = KI[metal]; I = np.array(r["I"])
    ax.errorbar(I, r["k"], yerr=r["sk"], fmt=mk, color=col, ms=6, capsize=3,
                label=f"{metal}: α = {fmt(r['fit']['k'], 3)} ± {fmt(r['fit']['sk'], 3)} мкВ/(Тл·А)")
    xx = np.linspace(0, 1.12, 50)
    ax.plot(xx, r["fit"]["k"] * xx + r["fit"]["b"], color=col, lw=1.3)
    ax.plot(xx, r["fit0"]["k"] * xx, color=col, lw=1, ls="--", alpha=0.7)
ax.plot([], [], color="#777", ls="--", label="проверка: прямая через начало координат")
ax.set_xlabel("Ток через образец I, А"); ax.set_ylabel("k = dU⊥/dB, мкВ/Тл")
ax.set_xlim(0, 1.15); ax.set_ylim(0, 1.5)
ax.legend(loc="upper left"); ax.set_title("П. 15. Зависимость наклона k от тока через образец")
fig.savefig(HERE / "fig5_k_of_I.png"); plt.close(fig)


# ---------------------------------------------------------------------------
# П. 16. Цинк: R_H = k h / I
# ---------------------------------------------------------------------------
hZn = GEOM["Zn"]["h"] * 1e-3
IZn = D["Zn"]["I"]
RH_Zn = abs(ZN["fit"]["k"]) * 1e-6 * hZn / IZn
sRH_Zn = ZN["fit"]["sk"] * 1e-6 * hZn / IZn
# сравнение знака с медью при одинаковых K1 = 1, K2 = 1
sign_Cu_raw = np.sign(CU[-1]["fit"]["k"])   # после приведения к K2 = 1 (у этой серии K2 = 1)
sign_Zn_raw = np.sign(ZN["fit"]["k"])

fig, ax = plt.subplots(figsize=(7.2, 4.4))
B = np.array(ZN["B"]); U = np.array(ZN["Uperp"])
ax.errorbar(B, U, yerr=0.5 * S, fmt="o", color="#3c9d9b", ms=6, capsize=3, label="Zn, I = 1,00 А")
xx = np.linspace(0, 1.12, 50)
ax.plot(xx, ZN["fit"]["k"] * xx + ZN["fit"]["b"], color="#3c9d9b", lw=1.3,
        label=f"МНК: k = {fmt(ZN['fit']['k'], 3)} ± {fmt(ZN['fit']['sk'], 3)} мкВ/Тл")
cu = CU[-1]; ex = np.array(cu["excl"])
ax.plot(np.array(cu["B"])[~ex], np.array(cu["Uperp"])[~ex], "s", mfc="none", mec="#e07b28", ms=6,
        label="для сравнения: Cu, I = 1,07 А (те же K₁, K₂)")
ax.axhline(0, color="#999", lw=0.8)
ax.set_xlabel("|B|, Тл"); ax.set_ylabel("U⊥ = U₂₄ − U₀, мкВ (K₁ = 1, K₂ = 1)")
ax.legend(loc="upper left"); ax.set_xlim(0, 1.15); ax.set_ylim(-1.15, 1.7)
ax.set_title("П. 16. Цинк: U⊥(B) — знак противоположен меди")
fig.savefig(HERE / "fig6_Zn.png"); plt.close(fig)


# ---------------------------------------------------------------------------
# П. 10. Схема определения знака носителей (рисунок для тетради)
# ---------------------------------------------------------------------------
fig, axs = plt.subplots(1, 2, figsize=(10.5, 3.3))
for ax, title, top, bot, carrier, vdir in [
        (axs[0], "Электроны (Cu, Ag): $R_H < 0$", "−", "+", "e⁻", -1),
        (axs[1], "Дырки (Zn): $R_H > 0$", "+", "−", "h⁺", +1)]:
    ax.set_xlim(0, 10); ax.set_ylim(0, 5.2); ax.axis("off")
    ax.add_patch(plt.Rectangle((1, 1), 8, 2.6, fill=False, lw=1.6))
    ax.annotate("", xy=(8.6, 4.4), xytext=(1.4, 4.4), arrowprops=dict(arrowstyle="-|>", lw=1.6))
    ax.text(5, 4.6, "ток I", ha="center")
    ax.text(1.5, 2.3, "⊗ B", fontsize=13, va="center")
    for x in np.linspace(3.2, 8.2, 6):
        ax.text(x, 3.25, top, ha="center", va="center", fontsize=13,
                color="#c0392b" if top == "+" else "#1f4e79")
        ax.text(x, 1.3, bot, ha="center", va="center", fontsize=13,
                color="#c0392b" if bot == "+" else "#1f4e79")
    # носитель и его скорость
    ax.text(5.6, 2.3, carrier, ha="center", va="center", fontsize=12,
            bbox=dict(boxstyle="circle,pad=0.25", fc="white", ec="#555"))
    ax.annotate("", xy=(5.6 + 1.5 * vdir, 2.3), xytext=(5.6 + 0.45 * vdir, 2.3),
                arrowprops=dict(arrowstyle="-|>", color="#555"))
    ax.text(5.6 + 1.1 * vdir, 1.85, "v", ha="center", color="#555")
    ax.annotate("", xy=(5.6, 3.0), xytext=(5.6, 2.62), arrowprops=dict(arrowstyle="-|>", color="#2e7d32", lw=1.6))
    ax.text(5.85, 2.75, "$F_Л$", color="#2e7d32")
    ax.text(5, 0.35, "носители отклоняются вверх в обоих случаях;\nзнак заряда верхней грани разный",
            ha="center", fontsize=9)
    ax.set_title(title, fontsize=11)
fig.savefig(HERE / "fig0_sign_scheme.png"); plt.close(fig)


# ---------------------------------------------------------------------------
# П. 17–18. ρ0, σ0, n, μ
# ---------------------------------------------------------------------------
U34 = D["U34"]
MAT = {}
for metal in ["Ag", "Cu"]:
    g = GEOM[metal]; h, a, l = g["h"] * 1e-3, g["a"] * 1e-3, g["l"] * 1e-3
    u34 = U34[metal]["div"] * S34 * 1e-6; I34 = U34["I"]
    rho = u34 * a * h / (I34 * l); sigma = 1 / rho
    RH = KI[metal]["RH"]
    MAT[metal] = dict(U34_uV=u34 * 1e6, R34_uOhm=u34 / I34 * 1e6, rho=rho, sigma=sigma,
                      RH=RH, n=1 / (E * RH), mu_cm2=sigma * RH * 1e4)
MAT["Zn"] = dict(RH=RH_Zn, n=1 / (E * RH_Zn))


# ---------------------------------------------------------------------------
# П. 20. Погрешности (стандартные неопределённости, k = 1)
# ---------------------------------------------------------------------------
sq3 = math.sqrt(3)
ERR = {}
dI_rel_gain = 0.005 / sq3                       # масштаб индикатора тока, 0,5 %
dB_rel = D["errors"]["dB_rel_bound"] / sq3      # градуировка поля
for metal, ser in [("Ag", AG), ("Cu", CU)]:
    g = GEOM[metal]
    Umax = max(max(s["Uperp"][j] for j in range(len(s["Uperp"])) if not s["excl"][j]) for s in ser)
    parts = dict(
        stat=KI[metal]["fit"]["sk"] / KI[metal]["fit"]["k"],
        U=(0.025 * D["hall_range_uV"]) / sq3 / Umax,
        B=dB_rel, I=dI_rel_gain,
        h=D["errors"]["h_bound_mm"] / sq3 / g["h"])
    tot = math.sqrt(sum(v * v for v in parts.values()))
    # σ0: U34 (отсчёт ±½ дел. + класс 1,5 %), I34, a, l, h
    u34 = U34[metal]["div"] * S34
    p_sig = dict(U34=math.hypot(0.5 * S34 / sq3, 0.015 * D["u34_range_uV"] / sq3) / u34,
                 I34=(0.005 * U34["I"] + 0.02) / sq3 / U34["I"],
                 a=D["errors"]["al_bound_mm"] / sq3 / g["a"],
                 l=D["errors"]["al_bound_mm"] / sq3 / g["l"],
                 h=parts["h"])
    tot_sig = math.sqrt(sum(v * v for v in p_sig.values()))
    # μ = σ0 R_H = α I34 l / (U34 a): толщина сокращается
    p_mu = {k: v for k, v in parts.items() if k != "h"}
    p_mu.update({k: v for k, v in p_sig.items() if k != "h"})
    tot_mu = math.sqrt(sum(v * v for v in p_mu.values()))
    ERR[metal] = dict(RH_parts=parts, RH_rel=tot, sigma_parts=p_sig, sigma_rel=tot_sig,
                      mu_parts=p_mu, mu_rel=tot_mu, Umax=Umax)
UmaxZn = max(abs(np.array(ZN["Uperp"])))
pZn = dict(stat=sRH_Zn / RH_Zn, U=(0.025 * D["hall_range_uV"]) / sq3 / UmaxZn, B=dB_rel,
           I=(0.005 * IZn + 0.02) / sq3 / IZn, h=D["errors"]["h_bound_mm"] / sq3 / GEOM["Zn"]["h"])
ERR["Zn"] = dict(RH_parts=pZn, RH_rel=math.sqrt(sum(v * v for v in pZn.values())), Umax=float(UmaxZn))

REF = D["reference"]

# ---------------------------------------------------------------------------
# Сохранение
# ---------------------------------------------------------------------------
out = dict(s_uV_per_div=S, nodes=nodes.tolist(), hysteresis=hyst,
           Ag=AG, Cu=CU, Ag_reverse=AG_REV, Cu_reverse=CU_REV, Zn=ZN,
           reversal=dict(Ag=REV_AG, Cu=REV_CU), k_of_I=KI,
           Zn_RH=RH_Zn, Zn_sRH_stat=sRH_Zn, sign_Cu=int(sign_Cu_raw), sign_Zn=int(sign_Zn_raw),
           materials=MAT, errors=ERR)
(HERE / "results.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")

L = []
L.append(f"Цена деления холловских серий s = {fmt(S, 3)} мкВ/дел; для U34 — {fmt(S34, 1)} мкВ/дел\n")
L.append("П.13  расхождение обратного и прямого ходов:")
for x in hyst:
    L.append(f"   Iм={fmt(x['Im'],2)} А: обр {fmt(x['B_rev'],1)}, прям {fmt(x['B_fwd'],1)} мТл, {fmt(x['rel'],2)} %")
L.append("\nП.14  наклоны k, мкВ/Тл")
for m, ser in [("Ag", AG), ("Cu", CU)]:
    for s in ser:
        f = s["fit"]
        extra = f"   (по всем записям {fmt(s['fit_all']['k'],3)})" if s["fit_all"] else ""
        L.append(f"   {m} I={fmt(s['I'],2)}  U0={fmt(s['U0'],1)} дел ({s['U0_src']}), pol={s['polarity']:+d}:"
                 f"  k={fmt(f['k'],4)} ± {fmt(f['sk'],4)}, b={fmt(f['b'],4)} ± {fmt(f['sb'],4)}, r²={fmt(f['r2'],4)}{extra}")
        for e in s.get("excl_info", []):
            L.append(f"        исключено: Iм={e['Im']} записано {e['recorded']} дел, прямая даёт {fmt(e['expected_div'],1)} дел")
L.append("\nП.8   обращение поля")
for m, r in [("Ag", REV_AG), ("Cu", REV_CU)]:
    L.append(f"   {m}: k_пр={fmt(r['k_fwd'],4)}±{fmt(r['sk_fwd'],4)}, k_обр={fmt(r['k_rev'],4)}±{fmt(r['sk_rev'],4)},"
             f" среднее {fmt(r['k_mean'],4)}, разница {fmt(r['rel_diff'],1)} % ({fmt(r['n_sigma'],1)} σ),"
             f" max|ΔU| = {fmt(r['max_abs_diff'],3)} мкВ")
L.append("\nП.15  k(I) = αI + β")
for m in ["Ag", "Cu"]:
    r = KI[m]; f = r["fit"]
    L.append(f"   {m}: α={fmt(f['k'],4)}±{fmt(f['sk'],4)} мкВ/(Тл·А), β={fmt(f['b'],4)}±{fmt(f['sb'],4)} мкВ/Тл;"
             f"  R_H = {r['RH']:.4e} ± {r['sRH_stat']:.2e} (стат.);  через 0: α0={fmt(r['fit0']['k'],4)}, R_H0={r['RH0']:.4e}")
L.append(f"\nП.16  Zn: k={fmt(ZN['fit']['k'],4)}±{fmt(ZN['fit']['sk'],4)}, b={fmt(ZN['fit']['b'],4)}, R_H = {RH_Zn:.4e} ± {sRH_Zn:.2e} (стат.)"
         f"; знак k: Cu {int(sign_Cu_raw):+d}, Zn {int(sign_Zn_raw):+d}")
L.append("\nП.17–18")
for m in ["Ag", "Cu"]:
    x = MAT[m]
    L.append(f"   {m}: U34={fmt(x['U34_uV'],1)} мкВ, ρ0={x['rho']:.4e} Ом·м, σ0={x['sigma']:.4e} См/м, n={x['n']:.4e} м^-3, μ={fmt(x['mu_cm2'],2)} см²/(В·с)")
L.append(f"   Zn: n={MAT['Zn']['n']:.4e} м^-3")
L.append("\nП.20  относительные стандартные неопределённости")
for m in ["Ag", "Cu", "Zn"]:
    e = ERR[m]
    L.append(f"   {m} R_H: " + ", ".join(f"{k}={fmt(v*100,1)}%" for k, v in e["RH_parts"].items()) + f"  → {fmt(e['RH_rel']*100,1)} %")
    if "sigma_rel" in e:
        L.append(f"   {m} σ0: " + ", ".join(f"{k}={fmt(v*100,1)}%" for k, v in e["sigma_parts"].items()) + f"  → {fmt(e['sigma_rel']*100,1)} %")
        L.append(f"   {m} μ:  → {fmt(e['mu_rel']*100,1)} %")
(HERE / "results.txt").write_text("\n".join(L), encoding="utf-8")
print("\n".join(L))
