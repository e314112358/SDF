import matplotlib
matplotlib.use('Agg')

import argparse
import glob
import os
import importlib
import pkgutil
from pathlib import Path

from config import load_config
from core import BasePlotter

# 自动加载插件
import plugins
for _, module_name, _ in pkgutil.iter_modules(plugins.__path__):
    importlib.import_module(f"plugins.{module_name}")


def list_experiments(config_dir: Path) -> list:
    """列出可用的实验配置"""
    exp_dir = config_dir / "experiments"
    if not exp_dir.exists():
        return []
    return [f.stem for f in exp_dir.glob("*.yaml")]


def main():
    available_plugins = list(BasePlotter.registry.keys())
    config_dir = Path(__file__).parent / "config"
    
    parser = argparse.ArgumentParser(description="SDF 数据处理与可视化程序")
    parser.add_argument('-t', '--tasks', nargs='+', choices=available_plugins, required=True,
                        help=f"指定需要执行的画图任务, 可选项: {available_plugins}")
    parser.add_argument('-f', '--files', type=str, default="*.sdf",
                        help="指定要读取的 SDF 文件，默认匹配当前目录下所有 *.sdf 文件")
    parser.add_argument('-c', '--config', type=str, default=None,
                        help="指定实验配置名称，对应 config/experiments/ 下的 YAML 文件")
    parser.add_argument('--list-configs', action='store_true',
                        help="列出所有可用的实验配置")
    
    args = parser.parse_args()
    
    # 列出可用配置
    if args.list_configs:
        experiments = list_experiments(config_dir)
        if experiments:
            print("可用的实验配置:")
            for exp in experiments:
                print(f"  - {exp}")
        else:
            print("没有找到实验配置文件，请在 config/experiments/ 目录下创建 YAML 文件")
        return
    
    # 加载配置
    try:
        config = load_config(args.config, config_dir)
    except FileNotFoundError as e:
        print(f"错误: {e}")
        return
    
    if args.config:
        print(f"使用实验配置: {config.name}")
    
    # 实例化插件
    active_plotters = [BasePlotter.registry[name](config) for name in args.tasks]
    
    # 查找文件
    sdf_files = sorted(glob.glob(args.files))
    if not sdf_files:
        print(f"未找到符合条件的文件: {args.files}")
        return
    
    print(f"总计发现 {len(sdf_files)} 个文件。")
    print(f"当前设定的执行任务: {args.tasks}\n")
    
    # 处理文件
    from core import SDFLoader
    
    for fname in sdf_files:
        base_name = os.path.splitext(fname)[0]
        
        with SDFLoader(fname) as data:
            time_fs = data.Header['time'] * 1e15
            print(f"[{fname}] 时间节点: {time_fs:.0f} fs | 开始分配任务...")
            
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
