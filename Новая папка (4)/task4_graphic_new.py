import numpy as np
import matplotlib.pyplot as plt

data = {}
with open("task4_pi.csv") as file:
    for line in file:
        name, n, pi = line.split()
        if 'nan' in pi:
            pi = 'nan'
        if name not in data:
            data[name] = ([], [])
        data[name][0].append(int(n))
        data[name][1].append(float(pi))

for name in data:
    x = np.array(data[name][0])
    y = np.array(data[name][1])

    plt.figure(figsize=(15, 8))
    plt.plot(x, y, 'o-', color='blue')
    plt.axhline(np.pi, color='red')
    plt.text(-0.01, np.pi, 'pi', color='red', fontsize=14, ha='right', va='center',
             transform=plt.gca().get_yaxis_transform())

    if name == 'brother_Chudnovsky':
        plt.xlim(0.5, 10.5)
    else:
        plt.xscale('log')

    if name == 'double_sum':
        plt.ylim(3.1400, 3.1430)
        plt.ticklabel_format(axis='y', useOffset=False)
    if name == 'Euler':
        plt.ylim(3.1414, 3.1417)
        plt.ticklabel_format(axis='y', useOffset=False)

    plt.title(name)
    plt.grid(True, alpha=0.5)
    plt.show()