import matplotlib
matplotlib.use('Agg') # 习惯性加入无头模式，防止批量画图报错

import sdf_helper as sh
import matplotlib.pyplot as plt
import scipy.constants as const
import numpy as np
import glob
import os

# ==========================================
# 物理常量
# ==========================================
J_TO_MEV = 1.0 / (const.e * 1e6) # 焦耳 (J) 转换到 兆电子伏特 (MeV)

# ==========================================
# 🌟 核心通用能谱绘图函数
# ==========================================
def plot_energy_spectrum(sdf_files, dist_name, species_label, color='red', xlim=None, ylim=None, output_dir=None):
    """
    通用能谱处理与绘图函数。
    
    参数:
    - sdf_files: 需要处理的 SDF 文件列表
    - dist_name: 你在 input.deck 中定义的 dist_fn 的 name (如 'proton_energy_spectrum')
    - species_label: 粒子的显示名称 (如 'Proton', 'Electron')，用于图片标题和寻找数据块
    - color: 曲线颜色
    - xlim: X轴(能量)显示范围, 例如 [0, 100] (可选)
    - ylim: Y轴(数量)显示范围, 例如 [1e6, 1e13] (可选)
    - output_dir: 输出文件夹名 (可选，如果不填会自动根据物种名生成)
    """
    # 如果没有指定输出文件夹，自动创建一个
    if output_dir is None:
        output_dir = f"Plots_Spectrum_{species_label}"
    os.makedirs(output_dir, exist_ok=True)

    print(f"🚀 开始处理 {len(sdf_files)} 个文件的 {species_label} 能谱...")

    for fname in sdf_files:
        try:
            data = sh.getdata(fname, verbose=False)
            base_name = os.path.splitext(fname)[0]
            time_fs = data.Header['time'] * 1e15
            
            # 【变量名嗅探机制】：兼容不同版本的 EPOCH 输出
            var_name_full = f"dist_fn_{dist_name}_{species_label}"
            var_name_short = f"dist_fn_{dist_name}"
            
            if hasattr(data, var_name_full):
                spectrum_block = getattr(data, var_name_full)
            elif hasattr(data, var_name_short):
                spectrum_block = getattr(data, var_name_short)
            else:
                print(f"⚠️ [{fname}] 跳过: 未找到匹配的能谱数据 (尝试了 {var_name_full} 和 {var_name_short})")
                continue

            # 提取数据并换算单位 (J -> MeV)
            energy_J = spectrum_block.grid_mid[0]
            energy_MeV = energy_J * J_TO_MEV
            dN_dE = spectrum_block.data
            
            # 准备画布与半对数绘图
            fig = plt.figure(figsize=(8, 6))
            plt.semilogy(energy_MeV, dN_dE, color=color, linewidth=2.5, label=species_label)
            
            # 坐标轴范围锁定 (如果有设置)
            if xlim is not None:
                plt.xlim(xlim)
            if ylim is not None:
                plt.ylim(ylim)
            
            # 标签与排版 (PRL 质感)
            plt.xlabel("Energy (MeV)", fontsize=14, fontweight='bold')
            plt.ylabel("dN/dE (a.u.)", fontsize=14, fontweight='bold')
            plt.title(f"{species_label} Energy Spectrum | $t = {time_fs:.0f} \\, fs$", fontsize=16, y=1.03)
            plt.grid(True, which="both", ls="--", alpha=0.5)
            plt.legend(fontsize=12, loc='upper right')
            
            ax = plt.gca()
            for spine in ax.spines.values():
                spine.set_linewidth(1.5)
            ax.tick_params(axis='both', labelsize=12, width=1.5)
            
            # 保存
            save_path = os.path.join(output_dir, f"Spectrum_{species_label}_{base_name}.png")
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            plt.close(fig)
            
            print(f"✅ [{fname}] 成功导出 -> {save_path}")
            
        except Exception as e:
            print(f"❌ [{fname}] 处理失败: {str(e)}")
            
    print(f"🎉 {species_label} 能谱全部导出完成！\n")

# ==========================================
# 🚀 主程序：在这里灵活调用！
# ==========================================
def main():
    sdf_files = sorted(glob.glob("*.sdf"))
    
    if len(sdf_files) == 0:
        print("未找到任何 .sdf 文件，请检查目录。")
        return

    # ----------------------------------------------------
    # 调用 1：画质子能谱 (使用红色)
    # dist_name = 'proton_energy_spectrum' (对应你 input.deck 中的 name)
    # ----------------------------------------------------
    plot_energy_spectrum(
        sdf_files=sdf_files, 
        dist_name="proton_energy_spectrum", 
        species_label="Proton", 
        color="red",
        # xlim=[0, 100],  # 取消注释即可锁定能量在 0-100 MeV
        # ylim=[1e6, 1e13] # 取消注释即可锁定数量级
    )

    # ----------------------------------------------------
    # 调用 2：如果你同时输出了电子能谱，可以直接加一行调用 (使用蓝色)
    # 假设你在 input.deck 里写的 name 是 'electron_energy_spectrum'
    # ----------------------------------------------------
    plot_energy_spectrum(
        sdf_files=sdf_files, 
        dist_name="carbon_energy_spectrum", 
        species_label="Carbon", 
        color="blue"
     )

if __name__ == "__main__":
    main()