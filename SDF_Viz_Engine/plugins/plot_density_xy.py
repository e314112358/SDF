import os
import matplotlib.pyplot as plt
import sdf_helper as sh
import config
from core.base_plotter import BasePlotter

class DensityXYPlotter(BasePlotter):
    # 终端调用的代号
    name = "density_xy"

    def __init__(self):
        # 设定需要绘制的粒子种类及其对应的颜色和范围
        self.species_map = {
            'Electron': {'cmap': 'turbo',  'vrange': [0, 200]}, 
            'Proton':   {'cmap': 'turbo',   'vrange': [0, 30]},  
        }

    def plot(self, data, base_name, time_fs):
        success_count = 0
        
        for species_name, cfg in self.species_map.items():
            full_var_name = f"Derived_Number_Density_{species_name}"
            
            try:
                # 获取数据块
                density_block = getattr(data, full_var_name)
                
                # 归一化处理，N_C需要从config中读取
                density_block.data = density_block.data / config.N_C
                density_block.units = "n_c"
                density_block.name = f"Density of {species_name}"

                # 准备画布
                fig = plt.figure(figsize=(8, 6))
                plt.set_cmap(cfg['cmap'])
                
                # 绘图，iz=-1 表示沿Z轴中间切片提取XY平面
                sh.plot2d(density_block, iz=-1, vrange=cfg['vrange'], title=False)
                
                # 美化与标题
                plt.title(f"XY Plane | {species_name} Density | t = {time_fs:.0f} fs", fontsize='large', y=1.03)
                sh.axis_offset()

                # 读取 config.py 中的视野设置进行裁切
                if hasattr(config, 'X_LIMITS'):
                    plt.xlim(config.X_LIMITS)
                if hasattr(config, 'Y_LIMITS'):
                    plt.ylim(config.Y_LIMITS)

                # 处理输出路径
                output_base = getattr(config, 'OUTPUT_ROOT', '.')
                output_dir = os.path.join(output_base, f"Plots_XY_Density_{species_name}")
                os.makedirs(output_dir, exist_ok=True)
                
                # 保存并清理内存
                save_path = os.path.join(output_dir, f"XY_{species_name}_{base_name}.png")
                plt.savefig(save_path, dpi=300, bbox_inches='tight')
                plt.close(fig)
                
                success_count += 1
                
            except AttributeError:
                # 若文件中未找到该粒子数据，直接跳过并尝试下一种粒子
                continue
                
        # 只要成功绘制了至少一种粒子的密度，即向主程序报告成功
        return success_count > 0