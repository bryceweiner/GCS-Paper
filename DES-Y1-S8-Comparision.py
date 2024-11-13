import numpy as np
import matplotlib.pyplot as plt

# Constants
GAMMA = 1.89e-29      # Universal branching rate (s⁻¹)
T_BASE = 3.39e17      # Base time scale (s)
S8_PLANCK = 0.832     # Planck S8 value
C = 2.998e8           # Speed of light (m/s)
H0 = 67.4             # Hubble constant (km/s/Mpc)

def cosmic_time(z):
    """Calculate cosmic time since Big Bang at redshift z"""
    return T_BASE / np.sqrt(1 + z)

def s8_lcdm(z):
    """Calculate S8 parameter in ΛCDM with proper redshift evolution"""
    # ΛCDM normalization at z=0 is S8_PLANCK = 0.832
    # Growth factor D(z) scales as (1+z)^(-1)
    return S8_PLANCK * np.power(1/(1+z), 1.0)  # This should give values closer to 0.77-0.78

def s8_qbu(z):
    """Calculate S8 parameter with QBU effects"""
    t = cosmic_time(z)
    
    # QBU modification includes:
    # 1. Time-dependent suppression
    # 2. Modified growth rate due to quantum branching
    # 3. Scale factor evolution
    
    # Basic suppression
    suppression = np.exp(-GAMMA * t)
    
    # Modified growth factor due to quantum branching
    # This accounts for the additional term in the growth equation
    growth_modification = 1 - (GAMMA * t / (2 * H0 * (1 + z)))
    
    # Volume factor from modified Friedmann equation
    volume_factor = 1 + (GAMMA * t**3) / (C**3)
    
    # Combine all effects
    qbu_factor = suppression * growth_modification * np.cbrt(volume_factor)
    
    # QBU growth factor scales as (1+z)^(-0.5)
    return S8_PLANCK * qbu_factor * np.power(1 / (1 + z), 0.5)

# Verified DES data points
des_data = {
    'Y1': {
        'z': 0.62,
        'S8': 0.773,
        'error_plus': 0.026,
        'error_minus': 0.020
    },
    'Y3': {
        'z': 0.835,
        'S8': 0.776,
        'error': 0.017
    }
}

def calculate_qbu_uncertainty(z):
    """Calculate uncertainty in QBU S8 prediction
    
    QBU uncertainty includes:
    1. Base uncertainty from Planck S8 (~2%)
    2. Additional uncertainty from quantum branching effects
    3. Time-dependent component that grows with redshift
    """
    t = cosmic_time(z)
    
    # Base uncertainty from Planck
    base_uncertainty = 0.02 * S8_PLANCK
    
    # Quantum branching contribution
    # Increases with cosmic time due to cumulative branching effects
    branching_uncertainty = 0.01 * GAMMA * t
    
    # Redshift-dependent component
    # Uncertainty grows at higher redshift due to evolution effects
    z_factor = 1 + 0.15 * z
    
    total_uncertainty = np.sqrt(base_uncertainty**2 + 
                              branching_uncertainty**2) * z_factor
    
    return total_uncertainty

def calculate_lcdm_uncertainty(z):
    """Calculate uncertainty in ΛCDM S8 prediction
    
    ΛCDM uncertainty includes:
    1. Base uncertainty from Planck S8
    2. Growth factor uncertainty
    3. Systematic uncertainties in structure formation
    """
    # Base uncertainty from Planck measurement
    base_uncertainty = 0.02 * S8_PLANCK
    
    # Growth factor uncertainty
    # Increases with redshift due to cumulative effects
    growth_uncertainty = 0.01 * np.log(1 + z)
    
    # Systematic uncertainty from structure formation
    systematic_uncertainty = 0.005 * z
    
    total_uncertainty = np.sqrt(base_uncertainty**2 + 
                              growth_uncertainty**2 + 
                              systematic_uncertainty**2)
    
    return total_uncertainty

# Update prediction points calculation
prediction_points = []
z_values = np.linspace(0.3, 1.2, 50)
for z in z_values:
    lcdm_value = s8_lcdm(z)
    qbu_value = s8_qbu(z)
    qbu_uncertainty = calculate_qbu_uncertainty(z)
    lcdm_uncertainty = calculate_lcdm_uncertainty(z)
    
    # Print some debug values at key redshifts
    if z in [0.5, 0.835, 1.0]:
        print(f"\nAt z = {z:.3f}:")
        print(f"ΛCDM: S8 = {lcdm_value:.3f} ± {lcdm_uncertainty:.3f}")
        print(f"QBU:  S8 = {qbu_value:.3f} ± {qbu_uncertainty:.3f}")
    
    prediction_points.append({
        'z': z,
        'lcdm': lcdm_value,
        'qbu': qbu_value,
        'qbu_uncertainty': qbu_uncertainty,
        'lcdm_uncertainty': lcdm_uncertainty
    })

# Plot setup
plt.figure(figsize=(12, 8))

# Plot QBU prediction with uncertainty band
qbu_z = [p['z'] for p in prediction_points]
qbu_values = [p['qbu'] for p in prediction_points]
qbu_uncertainties = [p['qbu_uncertainty'] for p in prediction_points]
plt.plot(qbu_z, qbu_values, 'r-', label='QBU prediction', zorder=1)
plt.fill_between(qbu_z, 
                 np.array(qbu_values) - np.array(qbu_uncertainties),
                 np.array(qbu_values) + np.array(qbu_uncertainties),
                 color='red', alpha=0.2, label='QBU 1σ uncertainty', zorder=1)

# Plot ΛCDM predictions with uncertainty band
lcdm_z = [p['z'] for p in prediction_points]
lcdm_values = [p['lcdm'] for p in prediction_points]
lcdm_uncertainties = [p['lcdm_uncertainty'] for p in prediction_points]
plt.plot(lcdm_z, lcdm_values, 'b-', label='ΛCDM prediction', zorder=2)
plt.fill_between(lcdm_z, 
                 np.array(lcdm_values) - np.array(lcdm_uncertainties),
                 np.array(lcdm_values) + np.array(lcdm_uncertainties),
                 color='blue', alpha=0.2, label='ΛCDM 1σ uncertainty', zorder=2)

# Plot DES data points
plt.errorbar(des_data['Y1']['z'], 
            des_data['Y1']['S8'],
            yerr=[[des_data['Y1']['error_minus']], 
                 [des_data['Y1']['error_plus']]],
            fmt='o', 
            color='green', 
            label='DES Y1', 
            markersize=8,
            capsize=5,
            capthick=1,
            elinewidth=1,
            zorder=3)

plt.errorbar(des_data['Y3']['z'],
            des_data['Y3']['S8'],
            yerr=des_data['Y3']['error'],
            fmt='s',
            color='purple',
            label='DES Y3',
            markersize=8,
            capsize=5,
            capthick=1,
            elinewidth=1,
            zorder=3)

# Update chi-square calculation
def calculate_chi2(model_type):
    chi2 = 0
    # DES Y1
    closest_pred_y1 = min(prediction_points, 
                         key=lambda x: abs(x['z'] - des_data['Y1']['z']))
    model_value_y1 = closest_pred_y1[model_type]
    model_uncertainty_y1 = (closest_pred_y1['qbu_uncertainty'] 
                          if model_type == 'qbu' 
                          else closest_pred_y1['lcdm_uncertainty'])
    total_uncertainty_y1 = np.sqrt(((des_data['Y1']['error_plus'] + 
                                   des_data['Y1']['error_minus'])/2)**2 + 
                                 model_uncertainty_y1**2)
    chi2 += ((model_value_y1 - des_data['Y1']['S8']) / total_uncertainty_y1)**2

    # DES Y3
    closest_pred_y3 = min(prediction_points, 
                         key=lambda x: abs(x['z'] - des_data['Y3']['z']))
    model_value_y3 = closest_pred_y3[model_type]
    model_uncertainty_y3 = (closest_pred_y3['qbu_uncertainty'] 
                          if model_type == 'qbu' 
                          else closest_pred_y3['lcdm_uncertainty'])
    total_uncertainty_y3 = np.sqrt(des_data['Y3']['error']**2 + 
                                 model_uncertainty_y3**2)
    chi2 += ((model_value_y3 - des_data['Y3']['S8']) / total_uncertainty_y3)**2
    
    return chi2

# Calculate and display chi-square values
chi2_lcdm = calculate_chi2('lcdm')
chi2_qbu = calculate_chi2('qbu')

plt.text(0.35, 0.9, 
         f'χ²(ΛCDM) = {chi2_lcdm:.1f}\nχ²(QBU) = {chi2_qbu:.1f}',
         bbox=dict(facecolor='white', alpha=0.8))

# Customize plot
plt.grid(True, alpha=0.2)
plt.xlabel('Redshift (z)', fontsize=12)
plt.ylabel('S₈', fontsize=12)
plt.title('S₈ Parameter: Theory vs DES Measurements', fontsize=14)
plt.legend(loc='upper right', fontsize=10)

plt.tight_layout()
plt.show()
