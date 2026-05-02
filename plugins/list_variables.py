import os
import contextlib

from core import BasePlotter


class VariablesListPlugin(BasePlotter):
    name = "list_vars"
    _last_file_cache = None

    def plot(self, data, base_name, time_fs):
        import sdf_helper as sh
        
        # 读取目标规则
        target = self.config.list_vars.target
        should_execute = False
        
        if target == 'all':
            should_execute = True
        elif target == 'last':
            # 由 main.py 处理，这里总是执行
            should_execute = True
        else:
            if base_name == str(target):
                should_execute = True

        if not should_execute:
            return True

        # 提取变量清单
        var_list = []
        for attr_name in dir(data):
            if attr_name.startswith('_'):
                continue
            try:
                attr = getattr(data, attr_name)
                if hasattr(attr, 'data') and hasattr(attr, 'name'):
                    shape = attr.data.shape if hasattr(attr.data, 'shape') else 'N/A'
                    dtype = attr.data.dtype if hasattr(attr.data, 'dtype') else 'N/A'
                    var_list.append((attr_name, str(shape), str(dtype)))
            except Exception:
                continue
        
        var_list.sort(key=lambda x: x[0])
        
        # 保存
        subdir = "SDF_Variables_List"
        filename = f"Variables_{base_name}.txt"
        save_path = self.get_output_dir(subdir) / filename
        
        with open(save_path, 'w', encoding='utf-8') as f:
            f.write(f"File: {base_name}\n")
            f.write(f"Time: {time_fs:.0f} fs\n")
            f.write(f"Variables ({len(var_list)}):\n")
            f.write("-" * 70 + "\n")
            f.write(f"{'Variable':<45} {'Shape':<15} {'Dtype'}\n")
            f.write("-" * 70 + "\n")
            for name, shape, dtype in var_list:
                f.write(f"{name:<45} {shape:<15} {dtype}\n")
        
        return True
