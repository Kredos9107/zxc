import numpy as np
import matplotlib.pyplot as plt

x = np.array([0.00341297, 0.00335570, 0.00330011, 0.00324665, 0.00319458, 0.00309569])
y = np.array([-0.321, -0.473, -0.800, -1.224, -1.640, -2.079])
y_err = np.array([0.070, 0.072, 0.062, 0.065, 0.062, 0.064])
x_err = np.array([0, 0, 0, 0, 0, 0])  # ΔT = 0
k, b = np.polyfit(x, y, 1)

plt.errorbar(x, y, yerr=y_err, xerr=x_err, fmt='o', color='blue', markersize=2, capsize=2)
plt.plot(x, k*x + b, color='green')
plt.xlabel('1/T')
plt.ylabel('ln η')
plt.grid()
plt.show()

print(f'Коэффициент = {k}')