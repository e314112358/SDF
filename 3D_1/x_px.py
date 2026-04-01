import matplotlib
matplotlib.use('Agg') # 无头模式

import sdf_helper as sh
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm
import scipy.constants as const
import numpy as np
import glob
import os

# ==========================================
# 1. 🌟 多物种独立配置字典 (极其强大灵活)
# ==========================================
# 你可以在这里无限添加物种。
# x_lim 和 px_lim 设为 None 表示自动缩放；如果你想锁定范围，请填入列表如 [-5.0, 15.0]
SPECIES_CONFIG = {
    "Electron": {
        "mass": const.m_e,
        "p_label": r"$P_x / (m_e c)$",
        "x_lim": None,      # 电子 X 轴范围 (um)
        "px_lim": None      # 电子 Px 轴范围 (归一化动量)
    },
    "Proton": {
        "mass": const.m_p,
        "p_label": r"$P_x / (m_p c)$",
        "x_lim": None,      # 质子 X 轴范围
        "px_lim": None      # 质子 Px 轴范围
    },
    # 如果有碳离子，取消下面这段注释即可：
    # "Carbon": {
    #     "mass": const.m_p * 12,
    #     "p_label": r"$P_x / (12 m_p c)$",
    #     "x_lim": None,
    #     "px_lim": None
    # }
}

BINS = [1000, 1000] # 统一的网格分辨率

# 自动为每个物种创建专属输出文件夹
for species in SPECIES_CONFIG.keys():
    os.makedirs(f"Plots_PhaseSpace_{species}", exist_ok=True)

# ==========================================
# 2. 核心处理函数 (读一次文件，画所有物种)
# ==========================================
def process_file_for_all_species(fname):
    try:
        # 🌟 硬盘 I/O 极其昂贵，所以我们只读一次！
        data = sh.getdata(fname, verbose=False)
        base_name = os.path.splitext(fname)[0]
        time_fs = data.Header['time'] * 1e15
        
        print(f"\n📦 打开文件 [{fname}] (t = {time_fs:.0f} fs) ...")

        # 遍历配置字典中的每一个物种
        for species_name, config in SPECIES_CONFIG.items():
            
            # 1. 尝试获取该物种的数据块
            var_grid = getattr(data, f"Grid_Particles_{species_name}", None)
            var_px = getattr(data, f"Particles_Px_{species_name}", None)
            var_w  = getattr(data, f"Particles_Weight_{species_name}", None)
            
            if not all([var_grid, var_px, var_w]):
                print(f"  ⚠️ 跳过 {species_name}: 未找到对应的宏粒子数据。")
                continue
                
            # 2. 提取并换算数据
            x_data_um = var_grid.data[0] * 1e6
            p_norm_factor = config["mass"] * const.c
            px_data_norm = var_px.data / p_norm_factor
            weight_data = var_w.data
            
            num_particles = len(x_data_um)
            if num_particles == 0:
                print(f"  ➖ 跳过 {species_name}: 粒子数为 0。")
                continue

            print(f"  ⏳ 正在绘制 {species_name} (粒子数: {num_particles:,}) ...")

            # 3. 极速网格化计算 2D 直方图
            # 判断是否设置了固定的坐标轴范围
            if config["x_lim"] and config["px_lim"]:
                h_range = [config["x_lim"], config["px_lim"]]
            else:
                h_range = None
                
            H, xedges, yedges = np.histogram2d(x_data_um, px_data_norm, 
                                               bins=BINS, range=h_range, weights=weight_data)
            
            # 归一化处理
            h_max = np.max(H)
            H_normalized = H / h_max if h_max > 0 else H

            # 4. 画图与美化
            fig = plt.figure(figsize=(8, 6))
            im = plt.pcolormesh(xedges, yedges, H_normalized.T, cmap='turbo', 
                                norm=LogNorm(vmin=1e-5, vmax=1.0), shading='auto')
            
            cbar = plt.colorbar(im)
            cbar.set_label('Normalized Density (a.u.)', fontsize=12)
            
            # 标题与排版
            plt.title(f"Raw Particle Phase Space $(x - P_x)$ | {species_name}\n$t = {time_fs:.0f} \\, fs$", 
                      fontsize=15, pad=10)
            plt.xlabel("X Position $(\\mu m)$", fontsize=14, fontweight='bold')
            plt.ylabel(f"Momentum {config['p_label']}", fontsize=14, fontweight='bold')
            
            plt.axhline(0, color='white', linestyle='--', alpha=0.3, lw=1.5)
            
            ax = plt.gca()
            for spine in ax.spines.values():
                spine.set_linewidth(1.5)
            ax.tick_params(axis='both', labelsize=12, width=1.5)
            
            # 导出到该物种的专属文件夹
            output_dir = f"Plots_PhaseSpace_{species_name}"
            save_path = os.path.join(output_dir, f"PhaseSpace_Raw_{species_name}_{base_name}.png")
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            plt.close(fig)
            
            print(f"  ✅ 成功导出 -> {save_path}")

    except Exception as e:
        print(f"❌ [{fname}] 发生严重错误: {str(e)}")

# ==========================================
# 3. 主程序启动
# ==========================================
def main():
    sdf_files = sorted(glob.glob("*.sdf"))
    
    print(f"🚀 开始极速提取多物种相空间 (共 {len(sdf_files)} 个文件)...")
    for fname in sdf_files:
        process_file_for_all_species(fname)
    print("🎉 所有物种相空间出图完成！")

if __name__ == "__main__":
    main()