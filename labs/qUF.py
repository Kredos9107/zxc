import matplotlib.pyplot as plt
import numpy as np

# Данные
T = np.array([293.1, 297.9, 302.9, 308.0, 312.8, 317.8, 322.9, 327.6])
q = np.array([46.81, 47.57, 48.38, 49.19, 49.96, 50.75, 51.57, 52.32])
q_err = np.array([2.49, 2.53, 2.57, 2.62, 2.66, 2.70, 2.74, 2.78])
U = np.array([113.21, 112.43, 112.24, 111.78, 112.19, 112.34, 112.71, 112.91])
U_err = np.array([2.98, 2.97, 2.98, 2.99, 3.00, 3.01, 3.02, 3.04])

# Аппроксимация q
coeffs_q = np.polyfit(T, q, 1)
q_fit = np.poly1d(coeffs_q)

# Аппроксимация U
coeffs_U = np.polyfit(T, U, 1)
U_fit = np.poly1d(coeffs_U)

T_fit = np.linspace(290, 330, 100)

# График 1: q(T)
plt.figure(figsize=(8, 5))
plt.errorbar(T, q, yerr=q_err, fmt='o', capsize=3, markersize=4,
             elinewidth=1, capthick=1)
plt.plot(T_fit, q_fit(T_fit), 'r-', label=f'Аппроксимация: q = {coeffs_q[0]:.4f}·T + {coeffs_q[1]:.4f}')
plt.xlabel('T, K')
plt.ylabel('q, мН/м')
plt.title('Теплота образования единицы поверхности')
plt.grid(True, linestyle='--', alpha=0.6)
plt.legend()
plt.show()

# График 2: U/F (T)
plt.figure(figsize=(8, 5))
plt.errorbar(T, U, yerr=U_err, fmt='s', capsize=3, markersize=4,
             elinewidth=1, capthick=1)
plt.plot(T_fit, U_fit(T_fit), 'b-', label=f'Аппроксимация: U/F = {coeffs_U[0]:.4f}·T + {coeffs_U[1]:.4f}')
plt.xlabel('T, K')
plt.ylabel('U/F, мН/м')
plt.title('Поверхностная энергия единицы площади')
plt.grid(True, linestyle='--', alpha=0.6)
plt.legend()
plt.show()