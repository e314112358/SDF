# main.py
import matplotlib
matplotlib.use('Agg') # 开启无头模式，防止在无显示器的计算节点上报错

import argparse
import glob
import os
import importlib
import pkgutil

from core.data_loader import SDFLoader
from core.base_plotter import BasePlotter

# 自动扫描并加载 plugins 文件夹下的所有插件脚本
import plugins
for _, module_name, _ in pkgutil.iter_modules(plugins.__path__):
    importlib.import_module(f"plugins.{module_name}")

def main():
    # 获取当前系统中已注册的绘图插件列表
    available_plugins = list(BasePlotter.registry.keys())
    
    # 设置命令行参数
    parser = argparse.ArgumentParser(description="SDF 数据处理与可视化程序")
    parser.add_argument('-t', '--tasks', nargs='+', choices=available_plugins, required=True,
                        help=f"指定需要执行的画图任务, 可选项: {available_plugins}")
    parser.add_argument('-f', '--files', type=str, default="*.sdf",
                        help="指定要读取的 SDF 文件，默认匹配当前目录下所有 *.sdf 文件")
    args = parser.parse_args()

    # 实例化用户选中的绘图插件
    active_plotters = [BasePlotter.registry[name]() for name in args.tasks]
    
    sdf_files = sorted(glob.glob(args.files))
    if not sdf_files:
        print(f"未找到符合条件的文件: {args.files}")
        return

    print(f"总计发现 {len(sdf_files)} 个文件。")
    print(f"当前设定的执行任务: {args.tasks}\n")

    # 循环遍历文件列表
    for fname in sdf_files:
        base_name = os.path.splitext(fname)[0]
        
        # 打开文件提取数据，with语句确保结束后自动清理内存
        with SDFLoader(fname) as data:
            time_fs = data.Header['time'] * 1e15
            print(f"[{fname}] 时间节点: {time_fs:.0f} fs | 开始分配任务...")
            
            # 将当前文件数据依次传递给各个插件处理
            for plotter in active_plotters:
                try:
                    success = plotter.plot(data, base_name, time_fs)
                    if success:
                        print(f"  [{plotter.name}] 绘图并导出成功")
                    else:
                        print(f"  [{plotter.name}] 已跳过 (文件中未包含所需数据块)")
                except Exception as e:
                    print(f"  [{plotter.name}] 运行报错: {e}")

    print("\n全部任务处理结束。")

if __name__ == "__main__":
    main()