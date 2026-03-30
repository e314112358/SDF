import sdf_helper as sh
import matplotlib.pyplot as plt
import scipy.constants as const
import numpy as np
import glob
import os

# ==========================================
# 1. 物理参数与独立范围控制 (XZ平面)
# ==========================================
WAVELENGTH = 0.8e-6  
OMEGA_L = 2 * np.pi * const.c / WAVELENGTH
N_C = (const.epsilon_0 * const.m_e * OMEGA_L**2) / (const.e**2)

SPECIES_MAP = {
    'Electron': {'cmap': 'Blues', 'vrange': [0, 200]},
    'Proton':   {'cmap': 'Reds',  'vrange': [0, 30]},
    'Carbon':   {'cmap': 'Greens',  'vrange': [0, 30]}, # 碳密度相对较低
}

# ==========================================
# 2. 核心绘图函数
# ==========================================
def plot_density_xz(data, species_name, cmap, vrange, base_name, time_fs):
    full_var_name = f"Derived_Number_Density_{species_name}"
    
    try:
        density_block = getattr(data, full_var_name)
        
        density_block.data = density_block.data / N_C
        density_block.units = "n_c"
        density_block.name = f"Density of {species_name}"

        plt.figure(figsize=(10, 5))
        plt.set_cmap(cmap)
        
        # 【XZ平面专属】：iy=-1 表示沿Y轴中间切片
        sh.plot2d(density_block, iy=-1, vrange=vrange, title=False)
        
        plt.title(f"XZ Plane | {species_name} Density | $t = {time_fs:.0f} \\, fs$", fontsize='large', y=1.03)
        sh.axis_offset()

        # 文件夹带上平面标记
        output_dir = f"Plots_XZ_Density_{species_name}"
        os.makedirs(output_dir, exist_ok=True)
        
        save_path = os.path.join(output_dir, f"XZ_{species_name}_{base_name}.png")
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
        return True
    
    except AttributeError:
        return False

# ==========================================
# 3. 主程序
# ==========================================
def main():
    sdf_files = sorted(glob.glob("*.sdf"))
    print(f"🚀 [XZ 平面] 开始处理 {len(sdf_files)} 个文件...")

    for fname in sdf_files:
        data = sh.getdata(fname, verbose=False)
        base_name = os.path.splitext(fname)[0]
        time_fs = data.Header['time'] * 1e15
        
        for species, config in SPECIES_MAP.items():
            success = plot_density_xz(data, species, config['cmap'], config['vrange'], base_name, time_fs)
            if success:
                print(f"成功: [{fname}] -> XZ_{species} 已保存")

if __name__ == "__main__":
    main()