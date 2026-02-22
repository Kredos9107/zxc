import matplotlib.pyplot as plt
import numpy as np

# твои данные
T = np.array([293.1, 297.9, 302.9, 308.0, 312.8, 317.8, 322.9, 327.6])
sigma = np.array([66.40, 64.86, 63.86, 62.59, 62.23, 61.59, 61.14, 60.59])

dSdT = -0.1597  # из графика

q = -T * dSdT
U_over_F = sigma - T * dSdT  # это sigma + |dSdT|*T, т.к. dSdT отрицательный

plt.figure(figsize=(8,5))
plt.plot(T, q, 's-', label='q = -T dσ/dT')
plt.plot(T, U_over_F, 'o-', label='U/F = σ - T dσ/dT')
plt.xlabel('T, K')
plt.ylabel('мН/м')
plt.title('Теплота и поверхностная энергия')
plt.grid(True)
plt.legend()
plt.show()