import os
import contextlib
import sdf_helper as sh
import config
from core.base_plotter import BasePlotter

class VariablesListPlugin(BasePlotter):
    # 终端调用的代号
    name = "list_vars"

    def plot(self, data, base_name, time_fs):
        try:
            # 处理输出路径
            output_base = getattr(config, 'OUTPUT_ROOT', '.')
            output_dir = os.path.join(output_base, "SDF_Variables_List")
            os.makedirs(output_dir, exist_ok=True)
            
            # 为每个处理的 SDF 文件生成对应的 txt 变量清单
            save_path = os.path.join(output_dir, f"Variables_{base_name}.txt")
            
            # 拦截标准输出并写入文本文件
            with open(save_path, 'w', encoding='utf-8') as f:
                with contextlib.redirect_stdout(f):
                    sh.list_variables(data)
                    
            return True
            
        except Exception:
            return False