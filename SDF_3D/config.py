# config.py
import scipy.constants as const
import numpy as np
import os

_current_dir = os.path.dirname(os.path.abspath(__file__))
OUTPUT_ROOT = os.path.abspath(os.path.join(_current_dir, "..", "SDF_Outputs"))
#------------------------------物理常数与激光参数----------------------------------
WAVELENGTH = 0.8e-6
OMEGA_L = 2 * np.pi * const.c / WAVELENGTH
N_C = (const.epsilon_0 * const.m_e * OMEGA_L**2) / (const.e**2)
I_0_W_cm2 = 4e21
I_0_W_m2 = I_0_W_cm2 * 1e4
E_0 = np.sqrt(2 * I_0_W_m2 / (const.c * const.epsilon_0))
B_0 = E_0 / const.c

#--------------------------视野裁切 (全局统一取景框，画电子密度用)--------------------------------------
X_LIMITS = [-8, 22]
Y_LIMITS = [-7.5, 7.5]
Z_LIMITS = [-10, 10]  # 为 XZ 平面新增的 Z 轴限制

#------------------------------倾斜切片参数设定----------------------------------
THETA_DEG = -45.0          # 靶面倾斜角度
SLICE_DEPTH_UM = 1.0     # 切片深度
X_PIVOT_UM = 0.0           # 旋转轴心 X 坐标
Y_PIVOT_UM = 0.0           # 旋转轴心 Y 坐标
Y_PRIME_LIMITS = [-8, 8]   # 沿着靶面方向的视野范围

#-------------------------------新增的厚度平均参数 ---------------------------------
SLICE_DEPTH_RANGE_UM = [-0.3, 0.3]  # 沿 X' 轴积分的起始和结束深度
SLICE_STEPS = 10                    # 在此厚度内采样多少个切片进行平均 (数值越大越平滑，但计算稍慢)

#---------------------------变量清单生成规则------------------------------------
# 'last' : 仅在处理最后一个 SDF 文件时生成； 'all'：  为每一个 SDF 文件生成； '0015' : 仅为名称为 '0015' 的文件生成
LIST_VARS_TARGET = 'last'
#----------------------------锁定能谱图的 X 轴显示范围------------------------------------

ENERGY_LIMITS_MEV = [0, 100] #只看 0 到 100 MeV 的区间
#---------------------------探测器投影插件 (RCF Detector) 参数设置-------------------------------------
RCF_L_DETECTOR_M = 0.05 # 探测器距离靶背的实际物理距离 (单位: m)典型设置：0.05 代表 5 cm

# 探测器屏幕的显示半宽 (单位: 厘米),设为 4.0，则屏幕横、纵坐标范围均为 -4.0 到 4.0 cm。
# 如果发现粒子发散角很大，跑到了画幅外面，请将此值调大
RCF_SCREEN_LIMIT_CM = 4.0

# 2. 变量与文件设置
# 图像标题和输出文件夹中显示的粒子名称
RCF_SPECIES_NAME = "Proton"

# SDF 文件中实际变量名的后缀 (精准匹配 subset 数据)
# 程序会自动拼接为 Particles_Px_subset_Proton_only_Proton
RCF_VAR_SUFFIX = "subset_Proton_only_Proton"

# 3. 图像渲染参数
RCF_BINS = 300

# 4. 能量切片过滤器 (单位: MeV)
# None 表示绘制所有能量段的叠加总体投影
# 列表格式为 [能量下限, 能量上限]
RCF_ENERGY_FILTERS = [
    [15.0, 20.0], 
    [20.0, 25.0], 
    [20.0, 25.0], 
    [20.0, 25.0],
    [30.0, 35.0],
    [35.0, 40.0],
    [40.0, 45.0],
    [45.0, 50.0],
    [50.0, 55.0],
    [55.0, 60.0],
    [60.0, 65.0],
    [65.0, 70.0],
    [70.0, 75.0],
    [75.0, 80.0]
]

# ---------------------空间能量分布图 (Particle Energy Map) 参数设置------------------

EMAP_SPECIES_NAME = "Proton"
EMAP_VAR_SUFFIX = "subset_Proton_only_Proton"

# 关键设置：能量剥离阈值 (MeV)。
# 设为 0.5 表示不画能量低于 0.5 MeV 的冷粒子，从而呈现出干净的边界和高能束。
# 如果想看全貌，可以设为 0.0。
EMAP_MIN_ENERGY_MEV = 0.5
# 色标范围 [最小, 最大] (MeV)，根据你的图像设为 0 到 40 或 50
EMAP_VRANGE = [0, 40]
# 画布分辨率，400x400 个像素块
EMAP_BINS = 400
# (可选) 强制锁定显示范围，保证做视频时不跳动。如果注释掉，则自适应。
EMAP_X_LIMITS = [-8, 22]
EMAP_Y_LIMITS = [-15, 15]
EMAP_Z_LIMITS = [-15, 15]