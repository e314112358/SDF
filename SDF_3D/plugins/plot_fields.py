import os
import matplotlib.pyplot as plt
import sdf_helper as sh
import config
from core.base_plotter import BasePlotter

class FieldPlotter(BasePlotter):
    # 终端调用的代号
    name = "fields"

    def __init__(self):
        # 设定需要绘制的分量
        self.components = ['Ey', 'Bz','Ex','Bx','By']

    def plot(self, data, base_name, time_fs):
        success_count = 0
        
        for comp in self.components:
            is_electric = comp.startswith('E')
            norm_factor = config.E_0 if is_electric else config.B_0
            norm_unit = "E_0" if is_electric else "B_0"
            
            field_type = "Electric_Field" if is_electric else "Magnetic_Field"
            full_var_name = f"{field_type}_{comp}"
            
            try:
                # 获取数据块并归一化
                field_block = getattr(data, full_var_name)
                field_block.data = field_block.data / norm_factor
                field_block.units = norm_unit
                field_block.name = f"Normalized {comp}"

                # 准备画布
                fig = plt.figure(figsize=(10, 5))
                plt.set_cmap('RdBu')
                
                # 绘图
                sh.plot2d(field_block, iz=-1, vrange=[-2, 2], title=False)
                plt.title(f"{comp} Field | t = {time_fs:.0f} fs", fontsize='large', y=1.03)
                sh.axis_offset()

                # 读取 config.py 中的视野设置（如果存在）
                if hasattr(config, 'X_LIMITS'):
                    plt.xlim(config.X_LIMITS)
                if hasattr(config, 'Y_LIMITS'):
                    plt.ylim(config.Y_LIMITS)

                # 处理输出路径
                output_base = getattr(config, 'OUTPUT_ROOT', '.')
                output_dir = os.path.join(output_base, f"Plots_{comp}")
                os.makedirs(output_dir, exist_ok=True)
                
                # 保存并清理内存
                save_path = os.path.join(output_dir, f"{comp}_{base_name}.png")
                plt.savefig(save_path, dpi=300, bbox_inches='tight')
                plt.close(fig)
                
                success_count += 1
                
            except AttributeError:
                # 如果当前 SDF 文件中没有该分量数据，跳过并继续尝试下一个分量
                continue
                
        # 只要成功绘制了至少一个分量，即向主程序报告成功
        return success_count > 0