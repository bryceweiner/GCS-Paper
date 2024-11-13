import matplotlib.pyplot as plt
import numpy as np

# Constants and scaling relations from papers
gamma = 1.89e-29  # Universal branching rate
t_eff = 3.39e17   # Effective time at z=0.835
gamma_t = gamma * t_eff  # ≈ 0.057

# Data points with full covariance
class DataPoint:
    def __init__(self, omega_m, s8, omega_err, s8_err, omega_s8_corr=0):
        self.omega_m = omega_m
        self.s8 = s8
        self.omega_err = omega_err
        self.s8_err = s8_err
        self.correlation = omega_s8_corr

# Data from papers
des_y1 = DataPoint(
    omega_m=0.267,
    s8=0.773,
    omega_err=np.mean([0.030, 0.017]),  # Symmetrized
    s8_err=np.mean([0.026, 0.020]),     # Symmetrized
    omega_s8_corr=0.51  # From DES Y1 paper
)

planck = DataPoint(
    omega_m=0.315,
    s8=0.834,
    omega_err=0.007,
    s8_err=0.016,
    omega_s8_corr=0.32  # From Planck paper
)

# Create plot
plt.figure(figsize=(12, 8))

# Plot uncertainty bands
omega_range = np.linspace(0.22, 0.38, 100)

# Calculate bands considering covariance
def get_confidence_bands(base_point, scaling_func, n_sigma=1):
    bands = []
    for omega in omega_range:
        var_s8 = (scaling_func(omega, base_point.s8, base_point.omega_m) / 
                  base_point.s8 * base_point.s8_err)**2
        var_omega = (scaling_func(omega, base_point.s8, base_point.omega_m) / 
                    base_point.omega_m * base_point.omega_err)**2
        covar_term = 2 * base_point.correlation * base_point.s8_err * base_point.omega_err
        
        total_err = np.sqrt(var_s8 + var_omega + covar_term)
        bands.append(total_err * n_sigma)
    return bands

# QBU scaling
def qbu_scaling(omega_m, base_s8, base_omega):
    return base_s8 * np.sqrt(1 - gamma_t) * (omega_m/base_omega)

# ΛCDM scaling
def lcdm_scaling(x, base_s8, base_omega):
    return base_s8 * np.sqrt(x/base_omega)

# Calculate and plot QBU predictions and bands
qbu_central = qbu_scaling(omega_range, planck.s8, planck.omega_m)
qbu_bands_1sigma = get_confidence_bands(planck, qbu_scaling, 1)
qbu_bands_2sigma = get_confidence_bands(planck, qbu_scaling, 2)

plt.fill_between(omega_range, 
                 qbu_central - qbu_bands_2sigma,
                 qbu_central + qbu_bands_2sigma,
                 color='green', alpha=0.1, label='QBU 2σ')
plt.fill_between(omega_range,
                 qbu_central - qbu_bands_1sigma,
                 qbu_central + qbu_bands_1sigma,
                 color='green', alpha=0.2, label='QBU 1σ')
plt.plot(omega_range, qbu_central, '--', color='green', 
         alpha=0.8, label='QBU prediction')

# Calculate and plot ΛCDM predictions and bands
lcdm_central = lcdm_scaling(omega_range, planck.s8, planck.omega_m)
lcdm_bands_1sigma = get_confidence_bands(planck, lcdm_scaling, 1)
lcdm_bands_2sigma = get_confidence_bands(planck, lcdm_scaling, 2)

plt.fill_between(omega_range, 
                 lcdm_central - lcdm_bands_2sigma,
                 lcdm_central + lcdm_bands_2sigma,
                 color='purple', alpha=0.1, label='ΛCDM 2σ')
plt.fill_between(omega_range,
                 lcdm_central - lcdm_bands_1sigma,
                 lcdm_central + lcdm_bands_1sigma,
                 color='purple', alpha=0.2, label='ΛCDM 1σ')
plt.plot(omega_range, lcdm_central, '--', color='purple', 
         alpha=0.8, label='ΛCDM prediction')

# Plot data points with error ellipses
def plot_error_ellipse(point, color, label):
    from matplotlib.patches import Ellipse
    import matplotlib.transforms as transforms
    
    # Calculate correlation matrix
    pearson = point.correlation
    cov = [[point.omega_err**2, pearson*point.omega_err*point.s8_err],
           [pearson*point.omega_err*point.s8_err, point.s8_err**2]]
    
    eigenvals, eigenvecs = np.linalg.eigh(cov)
    angle = np.degrees(np.arctan2(eigenvecs[1,0], eigenvecs[0,0]))
    
    for n_std in [1, 2]:
        ell = Ellipse((point.omega_m, point.s8),
                     2*n_std*np.sqrt(eigenvals[0]),
                     2*n_std*np.sqrt(eigenvals[1]),
                     angle=angle,
                     facecolor=color,
                     alpha=0.1 if n_std==2 else 0.2)
        plt.gca().add_patch(ell)
    
    plt.plot(point.omega_m, point.s8, 'o', color=color, label=label)

# Plot data with error ellipses
plot_error_ellipse(des_y1, 'blue', 'DES Y1')
plot_error_ellipse(planck, 'red', 'Planck')

# Customize plot
plt.xlabel('Ωm', fontsize=12)
plt.ylabel('S8', fontsize=12)
plt.title('Structure Formation Parameters with Full Covariance', fontsize=14)
plt.grid(True, linestyle='--', alpha=0.3)
plt.legend(fontsize=10)
plt.xlim(0.22, 0.38)
plt.ylim(0.72, 0.88)

plt.tight_layout()
plt.show()
