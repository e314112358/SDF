import os
import numpy as np
import matplotlib.pyplot as plt
import sdf_helper as sh
import config
from core.base_plotter import BasePlotter

class SpectrumPlotter(BasePlotter):
    name = "spectrum"

    def __init__(self):
        self.species_dict = {
            'Electron': 'E',
            'Proton': 'P'
        }

    def plot(self, data, base_name, time_fs):
        success_count = 0
        fig = plt.figure(figsize=(8, 6))
        
        for formal_name, short_name in self.species_dict.items():
            var_name = f"dist_fn_{short_name}_en_spe_{formal_name}"
            
            try:
                # 1. 获取分布函数数据块 (dN/dE)
                dist_block = getattr(data, var_name)
                
                # 2. 获取对应的能级网格并转换为 MeV
                energy_mev = dist_block.grid.data[0] / (1.602e-13)
                
                # 3. 获取分布函数数值
                dn_de = dist_block.data
                
                # 4. 绘图数据过滤
                # 由于 X 轴是线性坐标，能量为 0 是合法的。只需过滤 dn_de > 0 防止 Y 轴对数报错
                mask = (dn_de > 0)
                plt.plot(energy_mev[mask], dn_de[mask], label=formal_name, linewidth=2)
                
                success_count += 1
                
            except AttributeError:
                print(f"[Spectrum] 未找到变量 {var_name}")
                continue

        if success_count > 0:
            # --- 坐标轴美化 ---
            plt.yscale('log')
            # X 轴保持默认的线性坐标 (Linear Scale)
            
            plt.xlabel('Energy (MeV)', fontsize=12)
            plt.ylabel('dN/dE (Arbitrary Units)', fontsize=12)
            plt.title(f'Energy Spectrum | t = {time_fs:.0f} fs', fontsize=14)
            
            # 读取 config 中的能量显示范围（可选）
            if hasattr(config, 'ENERGY_LIMITS_MEV'):
                plt.xlim(config.ENERGY_LIMITS_MEV)
            
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