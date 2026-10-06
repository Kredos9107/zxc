import matplotlib.pyplot as plt
import numpy as np

# Данные
T = np.array([293.1, 297.9, 302.9, 308.0, 312.8, 317.8, 322.9, 327.6])
sigma = np.array([66.40, 64.86, 63.86, 62.59, 62.23, 61.59, 61.14, 60.59])
sigma_err = np.array([1.63, 1.59, 1.57, 1.54, 1.53, 1.51, 1.50, 1.49])

# Линейная аппроксимация
coeffs = np.polyfit(T, sigma, 1)
poly = np.poly1d(coeffs)
T_fit = np.linspace(290, 330, 100)
sigma_fit = poly(T_fit)

# График
plt.figure(figsize=(8, 5))
plt.errorbar(T, sigma, yerr=sigma_err, fmt='o', capsize=2, markersize=2.5,
             elinewidth=1, capthick=1)
plt.plot(T_fit, sigma_fit, 'r-', label=f'Температурный коэффициент: dσ/dT = {coeffs[0]:.3f} мН/(м·К)')

plt.xlabel('Температура T, K')
plt.ylabel('σ, мН/м')
plt.title('Зависимость σ(T)')
plt.grid(True, linestyle='--', alpha=0.6)
plt.legend()
plt.show()