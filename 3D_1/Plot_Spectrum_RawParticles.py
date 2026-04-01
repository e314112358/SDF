import matplotlib
matplotlib.use('Agg') # 无头模式

import sdf_helper as sh
import matplotlib.pyplot as plt
import scipy.constants as const
import numpy as np
import glob
import os

# ==========================================
# 1. 🌟 多物种独立配置字典
# ==========================================
# e_lim: 能量范围 (MeV)。如果设为 None，脚本会自动寻找最大能量！
# bins: 能量分成的网格数（数值越大，能谱越精细但也越抖动，建议 200~500）
SPECIES_CONFIG = {
    "Electron": {
        "mass": const.m_e,
        "color": "blue",
        "e_lim": None,         # 电子能量范围 [0, 50] 等
        "bins": 400
    },
    "Proton": {
        "mass": const.m_p,
        "color": "red",
        "e_lim": [0, 60],     # 质子能量范围建议手动锁死，比如锁定 0~100 MeV
        "bins": 300
    },
    # "Carbon": {
    #     "mass": const.m_p * 12,
    #     "color": "green",
    #     "e_lim": [0, 100],
    #     "bins": 300
    # }
}

# 自动为每个物种创建专属输出文件夹
for species in SPECIES_CONFIG.keys():
    os.makedirs(f"Plots_RawSpectrum_{species}", exist_ok=True)

# ==========================================
# 2. 核心处理函数
# ==========================================
def process_spectrum_for_all_species(fname):
    try:
        data = sh.getdata(fname, verbose=False)
        base_name = os.path.splitext(fname)[0]
        time_fs = data.Header['time'] * 1e15
        
        print(f"\n📦 打开文件 [{fname}] (t = {time_fs:.0f} fs) ...")

        for species_name, config in SPECIES_CONFIG.items():
            
            # 1. 尝试获取动量与权重数据
            var_px = getattr(data, f"Particles_Px_{species_name}", None)
            var_py = getattr(data, f"Particles_Py_{species_name}", None)
            var_pz = getattr(data, f"Particles_Pz_{species_name}", None)
            var_w  = getattr(data, f"Particles_Weight_{species_name}", None)
            
            if not all([var_px, var_w]):
                print(f"  ⚠️ 跳过 {species_name}: 未找到 Px 或 Weight 数据。")
                continue
                
            px = var_px.data
            w = var_w.data
            num_particles = len(px)
            
            if num_particles == 0:
                print(f"  ➖ 跳过 {species_name}: 粒子数为 0。")
                continue

            print(f"  ⏳ 正在计算 {species_name} 的能谱 (粒子数: {num_particles:,}) ...")

            # 2. 提取 Py, Pz (如果未输出这些维度，则默认为 0)
            py = var_py.data if var_py else np.zeros_like(px)
            pz = var_pz.data if var_pz else np.zeros_like(px)

            # 3. 相对论动能计算
            p_square = px**2 + py**2 + pz**2
            mc = config["mass"] * const.c
            gamma = np.sqrt(1.0 + p_square / (mc**2))
            
            # Ek = (gamma - 1) * m * c^2 (单位: 焦耳 J)
            ek_J = (gamma - 1.0) * config["mass"] * const.c**2
            # 换算为 MeV
            ek_MeV = ek_J / (const.e * 1e6)

            # 4. 一维直方图网格化 (类似 dist_fn)
            e_lim = config["e_lim"]
            if e_lim is None:
                h_range = [0, np.max(ek_MeV)] if np.max(ek_MeV) > 0 else [0, 1]
            else:
                h_range = e_lim
                
            # H 里面存的就是 dN/dE (每个能量区间内的粒子总权重)
            H, edges = np.histogram(ek_MeV, bins=config["bins"], range=h_range, weights=w)
            
            # 获取每个能量 bin 的中心坐标，用于画线
            energy_centers = (edges[:-1] + edges[1:]) / 2.0

            # 5. 画图与美化
            fig = plt.figure(figsize=(8, 6))
            
            # 半对数坐标绘制能谱线
            plt.semilogy(energy_centers, H, color=config["color"], linewidth=2.5, label=species_name)
            
            # 如果你想强制统一 Y 轴，取消下面这行的注释并设置范围
            # plt.ylim(1e6, 1e14)
            
            plt.xlabel("Kinetic Energy (MeV)", fontsize=14, fontweight='bold')
            plt.ylabel("dN/dE (a.u.)", fontsize=14, fontweight='bold')
            plt.title(f"Energy Spectrum (from Raw Particles) | {species_name}\n$t = {time_fs:.0f} \\, fs$", 
                      fontsize=15, pad=10)
            
            plt.grid(True, which="both", ls="--", alpha=0.5)
            plt.legend(fontsize=13, loc='upper right')
            
            # PRL 质感边框
            ax = plt.gca()
            for spine in ax.spines.values():
                spine.set_linewidth(1.5)
            ax.tick_params(axis='both', labelsize=12, width=1.5)
            
            # 保存
            output_dir = f"Plots_RawSpectrum_{species_name}"
            save_path = os.path.join(output_dir, f"Spectrum_Raw_{species_name}_{base_name}.png")
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
    
    # 因为算几十万个粒子的相对论平方根只需要零点几秒，速度极快！
    print(f"🚀 开始极速提取多物种能谱 (共 {len(sdf_files)} 个文件)...")
    for fname in sdf_files:
        process_spectrum_for_all_species(fname)
    print("🎉 所有物种能谱图导出完成！")

if __name__ == "__main__":
    main()