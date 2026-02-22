import numpy as np
import matplotlib.pyplot as plt
x_glass = np.array([0.00341297, 0.00335570, 0.00330011, 0.00324665, 0.00319458, 0.00314189, 0.00309569])
y_glass = np.array([0.045, -0.396, -0.783, -1.139, -1.427, -1.790, -2.064])
y_err_glass = np.array([0.024, 0.025, 0.024, 0.025, 0.025, 0.024, 0.024])
x_err = np.array([0, 0, 0, 0, 0, 0, 0])

k_glass, b_glass = np.polyfit(x_glass, y_glass, 1)

plt.errorbar(x_glass, y_glass, yerr=y_err_glass, xerr=x_err, fmt='o', color='blue', markersize=2, capsize=2)
plt.plot(x_glass, k_glass * x_glass + b_glass, color='green')
plt.xlabel('1/T')
plt.ylabel('ln η')
plt.grid(True)
plt.show()

print(f'Стекло: k = {k_glass:.4f}, b = {b_glass:.4f}')