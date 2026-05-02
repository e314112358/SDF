import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as colors
import scipy.constants as const

from core import BasePlotter


class PhaseSpacePlotter(BasePlotter):
    name = "phase_space"

    def plot(self, data, base_name, time_fs):
        success = False
        
        for species_cfg in self.config.phase_space.species:
            species_name = species_cfg['name']
            var_prefix = species_cfg['var_prefix']
            var_name = f"dist_fn_{var_prefix}_x_px_{species_name}"
            
            dist_block = self.safe_getattr(data, var_name)
            if dist_block is None:
                continue
            
            # 提取网格坐标
            grid = dist_block.grid.data
            x_um = grid[0] * 1e6
            mass = const.m_e if species_name.lower() == "electron" else const.m_p
            px_norm = grid[1] / (mass * const.c)
            
            # 获取分布数据，处理 3D 情况
            dist_data = dist_block.data
            if dist_data.ndim == 3:
                # 3D 数据：沿中间轴求和或取切片
                dist_data = dist_data[:, dist_data.shape[1] // 2, :]
            elif dist_data.ndim == 2:
                pass
            else:
                continue
            
            # 转置（matplotlib 行=Y，列=X）
            dist_data = dist_data.T
            
            # 绘图
            fig, ax = plt.subplots(figsize=(10, 6))
            
            v_max = np.max(dist_data)
            v_min = v_max * 1e-5 if v_max > 0 else 1e-10
            
            im = ax.pcolormesh(x_um, px_norm, dist_data,
                              norm=colors.LogNorm(vmin=v_min, vmax=v_max),
                              cmap='inferno', shading='auto')
            
            plt.colorbar(im, ax=ax, label='Log Density (a.u.)')
            ax.set_xlabel('X (um)', fontsize=12)
            ax.set_ylabel('px / (mc)', fontsize=12)
            ax.set_title(f'{species_name} Phase Space (x-px) | t = {time_fs:.0f} fs', fontsize=14)
            ax.set_xlim(self.config.view.x_limits)
            
            subdir = f"Plots_PhaseSpace_{species_name}"
            filename = f"x_px_{species_name}_{base_name}.png"
            self.save_figure(fig, subdir, filename)
            
            success = True
        
        return success
