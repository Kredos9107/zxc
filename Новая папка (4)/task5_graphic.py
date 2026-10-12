import numpy as np
import matplotlib.pyplot as plt

data = {}
with open("task5_time.csv") as file:
    for line in file:
        name, digits, iters, time = line.split()
        if name not in data:
            data[name] = ([], [], [])
        data[name][0].append(int(digits))
        data[name][1].append(int(iters))
        data[name][2].append(float(time))

plt.figure(figsize=(15, 8)) # время от точности
for name in data:
    plt.plot(data[name][0], data[name][2], 'o-', label=name)
plt.yscale('log')
plt.xticks(range(1, 11))
plt.title('Среднее время достижения точности 10^-k, нс')
plt.grid(True, which='both', alpha=0.5)
plt.legend()
plt.show()

plt.figure(figsize=(15, 8)) #число итераций от тчосности
for name in data:
    plt.plot(data[name][0], data[name][1], 'o-', label=name)
plt.yscale('log')
plt.xticks(range(1, 11))
plt.title('Число итераций алгоритма для точности 10^-k')
plt.grid(True, which='both', alpha=0.5)
plt.legend()
plt.show()