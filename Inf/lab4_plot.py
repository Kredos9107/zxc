import csv
import math
import matplotlib.pyplot as plt

data = {}
with open("lab4.csv") as f:
    for row in csv.DictReader(f):
        data.setdefault(row["formula"], ([], []))
        data[row["formula"]][0].append(int(row["n"]))
        data[row["formula"]][1].append(float(row["pi"]))

titles = {
    "wallis": ("Формула Валлиса",
               r"$\dfrac{\pi}{2} = \prod_{n=1}^{\infty} \dfrac{4n^2}{4n^2-1}$"),
    "leibniz": ("Ряд Лейбница",
                r"$\dfrac{\pi}{4} = \sum_{n=0}^{\infty} \dfrac{(-1)^n}{2n+1}$"),
    "basel": ("Ряд Эйлера",
              r"$\dfrac{\pi^2}{6} = \sum_{n=1}^{\infty} \dfrac{1}{n^2}$"),
    "nilakantha": ("Ряд Нилаканты",
                   r"$\pi = 3 + \sum_{n=1}^{\infty} \dfrac{(-1)^{n+1} \cdot 4}{2n(2n+1)(2n+2)}$"),
}

fig, axes = plt.subplots(len(titles), 1, figsize=(10, 17))
for ax, (name, (title, formula)) in zip(axes, titles.items()):
    n, pi = data[name]
    ax.plot(n, pi, marker=".", label=title)
    ax.axhline(math.pi, color="red", linestyle="--", label="π")
    ax.set_xscale("log")
    ax.set_title(title + "\n" + formula, fontsize=13)
    ax.set_xlabel("число итераций")
    ax.set_ylabel("π")
    ax.legend()
    ax.grid(True)

axes[0].set_ylim(3.06, 3.15)
axes[1].set_ylim(3.10, 3.18)
axes[2].set_ylim(3.1405, 3.1420)
axes[3].set_ylim(3.1410, 3.1420)

plt.tight_layout()
plt.savefig("lab4.png")

plt.figure(figsize=(10, 6))
for name in titles:
    n, pi = data[name]
    plt.plot(n, [abs(p - math.pi) for p in pi], label=titles[name][0])
plt.xscale("log")
plt.yscale("log")
plt.title("Ошибка |π - результат|")
plt.xlabel("число итераций")
plt.ylabel("ошибка")
plt.legend()
plt.grid(True)
plt.savefig("lab4_error.png")

plt.show()
