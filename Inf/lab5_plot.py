import csv
import matplotlib.pyplot as plt

data = {}
with open("lab5.csv") as f:
    for row in csv.DictReader(f):
        d = data.setdefault(row["formula"], ([], [], []))
        d[0].append(int(row["digits"]))
        d[1].append(int(row["iterations"]))
        d[2].append(float(row["time_us"]))

names = {
    "wallis": "Формула Валлиса",
    "leibniz": "Ряд Лейбница",
    "basel": "Ряд Эйлера",
    "nilakantha": "Ряд Нилаканты",
}

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 10))

for name, title in names.items():
    digits, iters, time_us = data[name]
    ax1.plot(digits, time_us, marker="o", label=title)
    ax2.plot(digits, iters, marker="o", label=title)

ax1.set_title("Среднее время достижения точности")
ax1.set_ylabel("время, мкс")
ax2.set_title("Число итераций до достижения точности")
ax2.set_ylabel("итерации")

for ax in (ax1, ax2):
    ax.set_yscale("log")
    ax.set_xlabel("число верных знаков (точность 10^-k)")
    ax.set_xticks(range(1, 11))
    ax.legend()
    ax.grid(True)

plt.tight_layout()
plt.savefig("lab5.png")
plt.show()
