import numpy as np
import matplotlib.pyplot as plt
import scipy.constants as const

from core import BasePlotter


class SpectrumPlotter(BasePlotter):
    name = "spectrum"

    def plot(self, data, base_name, time_fs):
        fig, ax = plt.subplots(figsize=self.config.output.figsize)
        success = False
        
        for species_cfg in self.config.spectrum.species:
            species_name = species_cfg['name']
            var_prefix = species_cfg['var_prefix']
            var_name = f"dist_fn_{var_prefix}_en_spe_{species_name}"
            
            dist_block = self.safe_getattr(data, var_name)
            if dist_block is None:
                print(f"[Spectrum] 未找到变量 {var_name}")
                continue
            
            # 提取数据
            energy_mev = dist_block.grid.data[0] / (const.e * 1e6)
            dn_de = dist_block.data
            
            # 过滤无效值
            mask = dn_de > 0
            ax.plot(energy_mev[mask], dn_de[mask], label=species_name, linewidth=2)
            
            success = True
        
        if not success:
            plt.close(fig)
            return False
        
        # 美化
        ax.set_yscale('log')
        ax.set_xlabel('Energy (MeV)', fontsize=12)
        ax.set_ylabel('dN/dE (Arbitrary Units)', fontsize=12)
        ax.set_title(f'Energy Spectrum | t = {time_fs:.0f} fs', fontsize=14)
        ax.set_xlim(self.config.spectrum.energy_limits_MeV)
        ax.grid(True, which="both", ls="-", alpha=0.2)
        ax.legend()
        
        # 保存
        subdir = "Plots_Spectrum"
        filename = f"Spec_{base_name}.png"
        self.save_figure(fig, subdir, filename)
        
        return True
