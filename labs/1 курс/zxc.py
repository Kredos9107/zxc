import numpy as np
import matplotlib.pyplot as plt

tau = np.array([5, 10, 15, 20, 25, 30, 35])
h1 = np.array([19.1, 18.8, 19.4, 19.5, 19.8, 19.1, 19.8])
h2 = np.array([3.9, 2.8, 2.4, 1.9, 1.4, 1.1, 1.0])
sigma_h = 0.1

ln_ratio = np.log(h1 / h2)
sigma_ln = np.sqrt((sigma_h / h1)**2 + (sigma_h / h2)**2)

n = len(tau)
sum_tau = np.sum(tau)
sum_ln = np.sum(ln_ratio)
sum_tau2 = np.sum(tau**2)
sum_tau_ln = np.sum(tau * ln_ratio)

slope = (n * sum_tau_ln - sum_tau * sum_ln) / (n * sum_tau2 - sum_tau**2)
intercept = (sum_ln - slope * sum_tau) / n

# Остатки
y_pred = intercept + slope * tau
residuals = ln_ratio - y_pred

# Среднеквадратичная ошибка остатков
sigma_res = np.sqrt(np.sum(residuals**2) / (n - 2))

# Погрешность углового коэффициента
tau_mean = np.mean(tau)
sigma_slope = sigma_res / np.sqrt(np.sum((tau - tau_mean)**2))

# Погрешность свободного члена
sigma_intercept = sigma_res * np.sqrt(np.sum(tau**2) / (n * np.sum((tau - tau_mean)**2)))

# Погрешность gamma
gamma = np.exp(intercept) / (np.exp(intercept) - 1)
dgamma_dintercept = np.exp(intercept) / (np.exp(intercept) - 1)**2
sigma_gamma = dgamma_dintercept * sigma_intercept

print(f'γ = {gamma:.3f} ± {sigma_gamma:.3f}')
print(f'Угловой коэффициент a = {slope:.4f} ± {sigma_slope:.4f}')
print(f'Свободный член b = {intercept:.4f} ± {sigma_intercept:.4f}')