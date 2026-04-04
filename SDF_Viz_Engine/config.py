# config.py
import scipy.constants as const
import numpy as np
import os

_current_dir = os.path.dirname(os.path.abspath(__file__))
OUTPUT_ROOT = os.path.abspath(os.path.join(_current_dir, "..", "SDF_Outputs"))
# --- 物理常数与激光参数 ---
WAVELENGTH = 0.8e-6
OMEGA_L = 2 * np.pi * const.c / WAVELENGTH
N_C = (const.epsilon_0 * const.m_e * OMEGA_L**2) / (const.e**2)

I_0_W_cm2 = 1.5e21
I_0_W_m2 = I_0_W_cm2 * 1e4
E_0 = np.sqrt(2 * I_0_W_m2 / (const.c * const.epsilon_0))
B_0 = E_0 / const.c

# --- 视野裁切 (全局统一取景框) ---
X_LIMITS = [-3, 5]
Y_LIMITS = [-4, 4]