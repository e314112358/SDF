import os
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as colors
import sdf_helper as sh
import config
import scipy.constants as const
from core.base_plotter import BasePlotter

class PhaseSpacePlotter(BasePlotter):
    # 终端调用的代号
    name = "phase_space"

    def __init__(self):
        # 对应变量名中的缩写和正式物种名
        self.species_dict = {
            'Electron': {'short': 'electron', 'mass': const.m_e},
            'Proton':   {'short': 'proton',   'mass': const.m_p}
        }

    def plot(self, data, base_name, time_fs):
        success_count = 0
        
        for formal_name, info in self.species_dict.items():
            var_name = f"dist_fn_{info['short']}_x_px_{formal_name}"
            
            try:
                # 1. 获取 2D 分布数据块 [x, px]
                dist_block = getattr(data, var_name)
                
                # 2. 提取网格坐标并转换单位
                # x 轴坐标 (通常在 grid.data[0]) 换算为微米
                x_um = dist_block.grid.data[0] * 1e6
                # px 轴坐标 (通常在 grid.data[1]) 归一化为 m*c
                # 这样 y 轴数值 1 就代表相对论阈值
                px_norm = dist_block.grid.data[1] / (info['mass'] * const.c)
                
                # 3. 获取分布强度 (dN / dx dpx)
                # 必须转置数据，因为 matplotlib 默认行是 Y，列是 X
                dist_data = dist_block.data.T 

                # 4. 绘图
                fig = plt.figure(figsize=(10, 6))
                
                # 使用 LogNorm 映射颜色，因为相空间密度跨度极大
                # vmin 设为最大值的 1e-4 左右可以滤除噪声
                v_max = np.max(dist_data)
                v_min = v_max * 1e-5 if v_max > 0 else 1e-10
                
                im = plt.pcolormesh(x_um, px_norm, dist_data, 
                                    norm=colors.LogNorm(vmin=v_min, vmax=v_max),
                                    cmap='inferno', shading='auto')
                
                # 5. 美化
                plt.colorbar(im, label='Log Density (a.u.)')
                plt.xlabel('X ($\mu m$)', fontsize=12)
                plt.ylabel('$p_x / (m c)$', fontsize=12)
                plt.title(f'{formal_name} Phase Space ($x-p_x$) | $t = {time_fs:.0f} \\, fs$', fontsize=14)
                
                # 如果 config 里定义了 X 视野，则应用
                if hasattr(config, 'X_LIMITS'):
                    plt.xlim(config.X_LIMITS)

                # 6. 保存
                output_base = getattr(config, 'OUTPUT_ROOT', '.')
                output_dir = os.path.join(output_base, f"Plots_PhaseSpace_{formal_name}")
                os.makedirs(output_dir, exist_ok=True)
                
                save_path = os.path.join(output_dir, f"x_px_{formal_name}_{base_name}.png")
                plt.savefig(save_path, dpi=300, bbox_inches='tight')
                plt.close(fig)
                
                success_count += 1
                
            except AttributeError:
                print(f"⚠️ [{base_name}] 未找到相空间变量 {var_name}")
                continue
                
        return success_count > 0