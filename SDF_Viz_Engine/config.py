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
Z_LIMITS = [-4, 4]  # 为 XZ 平面新增的 Z 轴限制

# 倾斜切片参数设定
THETA_DEG = -10.0          # 靶面倾斜角度
SLICE_DEPTH_UM = 0.025     # 切片深度
X_PIVOT_UM = 0.0           # 旋转轴心 X 坐标
Y_PIVOT_UM = 0.0           # 旋转轴心 Y 坐标
Y_PRIME_LIMITS = [-8, 8]   # 沿着靶面方向的视野范围

# --- 新增的厚度平均参数 ---
SLICE_DEPTH_RANGE_UM = [0.0, 0.05]  # 沿 X' 轴积分的起始和结束深度
SLICE_STEPS = 10                    # 在此厚度内采样多少个切片进行平均 (数值越大越平滑，但计算稍慢)