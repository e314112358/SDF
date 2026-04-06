import os
import numpy as np
import matplotlib.pyplot as plt
import sdf_helper as sh
import config
from core.base_plotter import BasePlotter

class SpectrumPlotter(BasePlotter):
    # 终端调用的代号
    name = "spectrum"

    def __init__(self):
        # 根据你提供的变量名，定义物种映射
        # 格式：{ '物种名': '变量名中的缩写' }
        self.species_dict = {
            'Electron': 'electron',
            'Proton': 'proton'
        }

    def plot(self, data, base_name, time_fs):
        success_count = 0
        fig = plt.figure(figsize=(8, 6))
        
        for formal_name, short_name in self.species_dict.items():
            var_name = f"dist_fn_{short_name}_energy_spectrum_{formal_name}"
            
            try:
                # 1. 获取分布函数数据块 (dN/dE)
                dist_block = getattr(data, var_name)
                
                # 2. 获取对应的能级网格 (Grid)
                # EPOCH 的 dist_fn 对应网格通常在 dist_block.grid 属性中
                # 能量单位通常是 Joule，转换为 MeV
                energy_mev = dist_block.grid.data[0] / (1.602e-13)
                
                # 3. 获取分布函数数值
                # 这里的单位通常是 (粒子数/m^3/J)，我们只需关注相对形态或乘以体积
                dn_de = dist_block.data
                
                # 4. 绘图 (只画有数据的部分)
                # 剔除能量为 0 或分布为 0 的点，防止对数轴报错
                mask = (energy_mev > 0) & (dn_de > 0)
                plt.plot(energy_mev[mask], dn_de[mask], label=formal_name, linewidth=2)
                
                success_count += 1
                
            except AttributeError:
                print(f"⚠️ [{base_name}] 未找到变量 {var_name}")
                continue

        if success_count > 0:
            # --- 坐标轴美化 ---
            plt.yscale('log')
            plt.xscale('log') # 能谱标准配置：双对数坐标
            
            plt.xlabel('Energy (MeV)', fontsize=12)
            plt.ylabel('$dN/dE$ (Arbitrary Units)', fontsize=12)
            plt.title(f'Energy Spectrum | $t = {time_fs:.0f} \\, fs$', fontsize=14)
            
            plt.grid(True, which="both", ls="-", alpha=0.2)
            plt.legend()

            # --- 保存路径 ---
            output_base = getattr(config, 'OUTPUT_ROOT', '.')
            output_dir = os.path.join(output_base, "Plots_Spectrum")
            os.makedirs(output_dir, exist_ok=True)
            
            save_path = os.path.join(output_dir, f"Spec_{base_name}.png")
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            plt.close(fig)
            return True
        else:
            plt.close(fig)
            return False