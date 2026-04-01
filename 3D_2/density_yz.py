import matplotlib
matplotlib.use('Agg') # 强制无头模式

import sdf_helper as sh
import matplotlib.pyplot as plt
import scipy.constants as const
import numpy as np
import glob
import os
from multiprocessing import Pool
from scipy.interpolate import RegularGridInterpolator

# ==========================================
# 1. 物理参数与物种配置
# ==========================================
WAVELENGTH = 0.8e-6  
OMEGA_L = 2 * np.pi * const.c / WAVELENGTH
N_C = (const.epsilon_0 * const.m_e * OMEGA_L**2) / (const.e**2)

SPECIES_MAP = {
    'Electron': {'cmap': 'turbo',  'vrange': [0, 200]},
    'Proton':   {'cmap': 'turbo',   'vrange': [0, 30]},
    'Carbon':   {'cmap': 'turbo', 'vrange': [0, 30]}, 
}

# ==========================================
# 2. 🌟 倾斜切片核心参数 (重点调整区)
# ==========================================
# 假设你的靶子在 XY 平面上倾斜了 30 度 (根据你的 input.deck 设定修改)
THETA_DEG = -10.0  
THETA_RAD = np.radians(THETA_DEG)

# 你想切在哪个深度？(沿着垂直于靶面的 X' 轴)
# 0.0 表示切在旋转轴心上；如果是负数，代表切在靶前真空区
SLICE_DEPTH_UM = 0.025 

# 旋转轴心 (假设靶子绕着原点 x=0, y=0 倾斜)
X_PIVOT_UM = 0.0
Y_PIVOT_UM = 0.0

# 视野裁切 (取景框)
Y_PRIME_LIMITS = [-8, 8]  # 沿着靶面方向 (Y'轴) 的视野
Z_LIMITS = [-6, 6]        # 沿着 Z 轴的视野

# ==========================================
# 3. 核心绘图函数 (完全重写)
# ==========================================
def plot_tilted_yz(data, species_name, cmap, vrange, base_name, time_fs):
    full_var_name = f"Derived_Number_Density_{species_name}"
    
    try:
        # 1. 获取全局网格坐标 (换算为微米)
        grid = data.Grid_Grid_mid.data 
        x_um = grid[0] * 1e6
        y_um = grid[1] * 1e6
        z_um = grid[2] * 1e6
        
        # 获取 3D 密度数据并归一化
        density_3d = getattr(data, full_var_name).data / N_C
        
        # 2. 构建 3D 空间插值器 (这是最耗内存的一步)
        # bounds_error=False 保证超出边界时不会报错，而是填充 0
        interpolator = RegularGridInterpolator((x_um, y_um, z_um), density_3d, 
                                               bounds_error=False, fill_value=0.0)
        
        # 3. 生成局部倾斜画布 (Y', Z) 的网格点
        # 我们只在取景框内生成 500x500 的高清网格，避免全局插值浪费算力
        yp_coords = np.linspace(Y_PRIME_LIMITS[0], Y_PRIME_LIMITS[1], 500)
        z_coords = np.linspace(Z_LIMITS[0], Z_LIMITS[1], 500)
        YP, Z_mesh = np.meshgrid(yp_coords, z_coords)
        
        # 4. 坐标逆变换：将 (Y', Z) 映射回真实的全局 (X, Y, Z)
        # X = X_pivot + Depth * cos(θ) - Y' * sin(θ)
        # Y = Y_pivot + Depth * sin(θ) + Y' * cos(θ)
        X_global = X_PIVOT_UM + SLICE_DEPTH_UM * np.cos(THETA_RAD) - YP * np.sin(THETA_RAD)
        Y_global = Y_PIVOT_UM + SLICE_DEPTH_UM * np.sin(THETA_RAD) + YP * np.cos(THETA_RAD)
        Z_global = Z_mesh
        
        # 组合成探测点云并执行插值提取
        points = np.stack((X_global.ravel(), Y_global.ravel(), Z_global.ravel()), axis=-1)
        sliced_data = interpolator(points).reshape(YP.shape)
        
        # 5. 接管 Matplotlib 手动绘图
        fig = plt.figure(figsize=(8, 6))
        
        # 使用 pcolormesh 画出插值后的平滑图像
        im = plt.pcolormesh(YP, Z_mesh, sliced_data, cmap=cmap, 
                            vmin=vrange[0], vmax=vrange[1], shading='auto')
        
        # 手动添加 Colorbar (因为抛弃了 sdf_helper.plot2d)
        cbar = plt.colorbar(im)
        cbar.set_label(f'Density $(n_c)$', fontsize='large')
        
        # 标签与排版
        plt.xlabel("Tilted Target Surface $Y' (\\mu m)$")
        plt.ylabel("Z Axis $(\\mu m)$")
        title_str = f"Tilted YZ Plane (Tilt: {THETA_DEG}°) | {species_name} | $t = {time_fs:.0f} \\, fs$"
        plt.title(title_str, fontsize='large', y=1.03)
        
        sh.axis_offset() # 依然可以使用神级滤镜！
        
        # 路径与保存
        output_dir = f"Plots_Tilted_YZ_Density_{species_name}"
        save_path = os.path.join(output_dir, f"TiltedYZ_{species_name}_{base_name}.png")
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close(fig)
        
        return True
    
    except AttributeError:
        return False

# ==========================================
# 4. 多进程任务分发
# ==========================================
def process_single_file(fname):
    try:
        data = sh.getdata(fname, verbose=False)
        base_name = os.path.splitext(fname)[0]
        time_fs = data.Header['time'] * 1e15
        
        success_list = []
        for species, config in SPECIES_MAP.items():
            success = plot_tilted_yz(data, species, config['cmap'], config['vrange'], base_name, time_fs)
            if success:
                success_list.append(species)
                
        if success_list:
            return f"✅ [{fname}] 成功切片 Tilted YZ: {', '.join(success_list)}"
        else:
            return f"⚠️ [{fname}] 跳过: 未找到粒子数据"
            
    except Exception as e:
        return f"❌ [{fname}] 处理失败: {str(e)}"

# ==========================================
# 5. 主程序启动
# ==========================================
def main():
    for species in SPECIES_MAP.keys():
        os.makedirs(f"Plots_Tilted_YZ_Density_{species}", exist_ok=True)
        
    sdf_files = sorted(glob.glob("*.sdf"))
    print(f"🚀 [倾斜 YZ 平面] 开始 24核并行 处理 {len(sdf_files)} 个文件...")

    NUM_PROCESSES = 24
    print(f"⚙️ 目标倾角: {THETA_DEG} 度 | 切片深度 (X'): {SLICE_DEPTH_UM} um")

    with Pool(processes=NUM_PROCESSES) as pool:
        for result_msg in pool.imap(process_single_file, sdf_files):
            print(result_msg)

    print("🎉 倾斜 YZ 切面图批量导出完成！")

if __name__ == "__main__":
    main()