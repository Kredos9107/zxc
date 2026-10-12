import numpy as np
import matplotlib.pyplot as plt

data = {}
with open("task4_pi.csv") as file:                     
    for line in file:
        name, n, res_pi = line.split()
        if 'nan' in res_pi:              
            res_pi = 'nan'
        if name not in data:
            data[name] = ([], [])
        data[name][0].append(int(n))
        data[name][1].append(float(res_pi))

for name in data:
    x = np.array(data[name][0])
    y = np.array(data[name][1])

    plt.figure(figsize=(15, 8))
    plt.plot(x, y, 'o-', color='blue')
    plt.axhline(np.pi, color='red') 
    plt.text(-0.01, np.pi, 'pi', color='red', fontsize=14, ha='right', va='center', transform=plt.gca().get_yaxis_transform()) 
    plt.title(name)
    plt.grid(True, alpha=0.5)
    plt.show()