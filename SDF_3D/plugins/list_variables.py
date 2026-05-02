import os
import glob
import contextlib
import sdf_helper as sh
import config
from core.base_plotter import BasePlotter

class VariablesListPlugin(BasePlotter):
    name = "list_vars"
    _last_file_cache = None

    def plot(self, data, base_name, time_fs):
        # 读取用户设定的目标规则
        target = getattr(config, 'LIST_VARS_TARGET', 'last')
        should_execute = False
        
        # 判断当前文件是否需要生成清单
        if target == 'all':
            should_execute = True
            
        elif target == 'last':
            # 扫描目录获取最后一个文件的名称并缓存
            if self._last_file_cache is None:
                sdf_files = sorted(glob.glob("*.sdf"))
                if sdf_files:
                    self._last_file_cache = os.path.splitext(os.path.basename(sdf_files[-1]))[0]
            
            if base_name == self._last_file_cache:
                should_execute = True
                
        else:
            # 判断是否为指定的具体文件名
            if base_name == str(target):
                should_execute = True

        # 若不满足条件，则直接跳过提取步骤
        if not should_execute:
            return True

        # 执行提取并保存
        try:
            output_base = getattr(config, 'OUTPUT_ROOT', '.')
            output_dir = os.path.join(output_base, "SDF_Variables_List")
            os.makedirs(output_dir, exist_ok=True)
            
            save_path = os.path.join(output_dir, f"Variables_{base_name}.txt")
            
            with open(save_path, 'w', encoding='utf-8') as f:
                with contextlib.redirect_stdout(f):
                    sh.list_variables(data)
            
            print(f"[ListVars] 已提取变量清单: {save_path}")
            return True
            
        except Exception as e:
            print(f"[ListVars] 提取报错: {e}")
            return False