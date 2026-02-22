import numpy as np
import matplotlib.pyplot as plt

x_steel = np.array([0.00341297, 0.00335570, 0.00330011, 0.00324665, 0.00319458, 0.00309569])
y_steel = np.array([-0.321, -0.473, -0.800, -1.224, -1.640, -2.079])
y_err_steel = np.array([0.070, 0.072, 0.062, 0.065, 0.062, 0.064])
x_err = np.array([0, 0, 0, 0, 0, 0])

k_steel, b_steel = np.polyfit(x_steel, y_steel, 1)

plt.errorbar(x_steel, y_steel, yerr=y_err_steel, xerr=x_err, fmt='o', color='blue', markersize=2, capsize=2)
plt.plot(x_steel, k_steel * x_steel + b_steel, color='green')
plt.xlabel('1/T')
plt.ylabel('ln η')
plt.grid(True)
plt.show()

print(f'Сталь: k = {k_steel:.4f}, b = {b_steel:.4f}')