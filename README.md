# SDF_3D

EPOCH 激光等离子体模拟后处理工具，用于批量处理 SDF 格式的 3D 场数据并生成可视化图像。

## 适用场景

- 激光-靶相互作用模拟（TNSA、靶后鞘场加速等）
- 粒子加速、能谱分析、相空间诊断
- 电磁场结构可视化
- RCF 探测器信号模拟

## 环境要求

| 依赖 | 版本要求 | 说明 |
|------|----------|------|
| Python | >= 3.8 | 推荐 3.10+ |
| numpy | >= 1.20 | 数值计算 |
| matplotlib | >= 3.5 | 绘图引擎 |
| scipy | >= 1.7 | 常数库、插值 |
| pyyaml | >= 5.0 | 配置文件解析 |
| sdf_helper | - | EPOCH 官方 SDF 读取库 |

## 安装

```bash
# 1. 克隆项目
git clone <repo_url>
cd SDF_3D

# 2. 安装依赖
pip install numpy matplotlib scipy pyyaml

# 3. 安装 sdf_helper（从 EPOCH 项目获取）
pip install sdf_helper
```

## 目录结构

```
SDF_3D/
├── main.py                 # 主程序入口
├── config/
│   ├── __init__.py
│   ├── loader.py           # 配置加载器
│   ├── default.yaml        # 默认配置
│   └── experiments/        # 实验配置目录
│       └── tnsa_2024.yaml  # 示例实验配置
├── core/
│   ├── __init__.py
│   ├── base_plotter.py     # 插件基类
│   ├── data_loader.py      # SDF 文件加载器
│   └── physics.py          # 物理计算工具
├── plugins/
│   ├── __init__.py
│   ├── base_density.py     # 密度图基类
│   ├── list_variables.py   # 变量清单提取
│   ├── plot_density_xy.py  # XY 平面电子密度
│   ├── plot_density_xz.py  # XZ 平面电子密度
│   ├── plot_density_yz.py  # 倾斜靶面 YZ 切片
│   ├── plot_fields.py      # 电磁场分量
│   ├── plot_particle_energy_map.py  # 空间能量分布
│   ├── plot_phase_space.py # 相空间分布
│   ├── plot_rcf_detector.py # RCF 探测器投影
│   └── plot_spectrum.py    # 粒子能谱
├── slurm/                  # Slurm 作业脚本目录
│   ├── run.slurm           # 运行所有插件
│   ├── spectrum.slurm      # 仅能谱
│   ├── fields.slurm        # 仅电磁场
│   └── ...                 # 其他专用脚本
└── README.md
```

## 快速开始

### 1. 使用默认配置

```bash
# 处理所有 SDF 文件
python main.py -t density_xy fields spectrum -f "*.sdf"

# 处理单个文件
python main.py -t spectrum -f "output0010.sdf"
```

### 2. 使用实验配置

```bash
# 列出所有可用配置
python main.py --list-configs

# 使用指定配置
python main.py -c tnsa_2024 -t density_xy fields -f "*.sdf"
```

### 3. 创建自定义实验配置

在 `config/experiments/` 目录下创建 YAML 文件：

```yaml
# config/experiments/my_experiment.yaml
name: my_experiment
description: 我的实验配置

# 覆盖激光参数
laser:
  wavelength_um: 0.8
  intensity_W_cm2: 1.0e+21

# 覆盖视野范围
view:
  x_limits: [-5, 15]
  y_limits: [-10, 10]
  z_limits: [-10, 10]

# 覆盖输出目录
output:
  root: /scratch/user/my_experiment_outputs

# 覆盖密度图配置
density:
  species:
    - name: Electron
      cmap: inferno
      vrange: [0, 50]
    - name: Proton
      cmap: turbo
      vrange: [0, 15]
```

然后使用：

```bash
python main.py -c my_experiment -t density_xy -f "*.sdf"
```

## 可用插件

使用 `-t` 参数指定要执行的任务，可同时指定多个：

```bash
python main.py -t density_xy fields spectrum
```

| 插件名 | 功能 | 输出目录 |
|--------|------|----------|
| `density_xy` | XY 平面电子密度切片 | `Plots_XY_Density_{物种}` |
| `density_xz` | XZ 平面电子密度切片 | `Plots_XZ_Density_{物种}` |
| `density_yz` | 倾斜靶面 YZ 切片（厚度平均） | `Plots_Tilted_YZ_Density_{物种}` |
| `fields` | 电磁场分量 (Ex, Ey, Bx, By, Bz) | `Plots_{分量}` |
| `spectrum` | 粒子能谱 (dN/dE) | `Plots_Spectrum` |
| `phase_space` | 相空间分布 (x-px) | `Plots_PhaseSpace_{物种}` |
| `energy_map` | 空间能量分布 (XY/XZ) | `Plots_EnergyMap_{物种}` |
| `rcf_detector` | RCF 探测器投影模拟 | `Plots_Detector_{距离}cm_{物种}` |
| `list_vars` | 提取 SDF 变量清单 | `SDF_Variables_List` |

## 配置详解

### 配置优先级

配置按以下优先级合并（高优先级覆盖低优先级）：

1. 命令行参数（如 `-f`）
2. 实验配置文件（`config/experiments/*.yaml`）
3. 默认配置（`config/default.yaml`）

### 激光参数

```yaml
laser:
  wavelength_um: 0.8           # 激光波长 (um)
  intensity_W_cm2: 4.0e+21     # 峰值强度 (W/cm^2)
```

程序会自动计算：
- `omega_l`: 激光角频率
- `n_c`: 临界密度
- `e_0`, `b_0`: 归一化电场/磁场

### 视野范围

```yaml
view:
  x_limits: [-8, 22]     # X 轴范围 (um)
  y_limits: [-7.5, 7.5]  # Y 轴范围 (um)
  z_limits: [-10, 10]    # Z 轴范围 (um)
```

### 倾斜切片参数

```yaml
tilted_slice:
  theta_deg: -45.0              # 靶面倾斜角度 (度)
  pivot_um: [0.0, 0.0]         # 旋转轴心坐标 (um)
  y_prime_limits: [-8, 8]       # 沿靶面方向视野 (um)
  depth_range_um: [-0.3, 0.3]   # 积分厚度范围 (um)
  steps: 10                     # 采样切片数
```

### RCF 探测器参数

```yaml
rcf:
  detector_distance_m: 0.05    # 探测器距离 (m), 5cm
  screen_limit_cm: 4.0         # 屏幕显示半宽 (cm)
  species_name: Proton         # 粒子种类
  var_suffix: subset_Proton_only_Proton  # 变量名后缀
  bins: 300                    # 直方图分辨率
  energy_filters:              # 能量切片 (MeV)
    - [15.0, 20.0]
    - [20.0, 25.0]
    - [25.0, 30.0]
```

### 能谱图参数

```yaml
spectrum:
  species:
    - name: Electron
      var_prefix: E
    - name: Proton
      var_prefix: P
  energy_limits_MeV: [0, 100]  # X 轴显示范围 (MeV)
```

### 能量分布图参数

```yaml
energy_map:
  species_name: Proton
  var_suffix: subset_Proton_only_Proton
  min_energy_MeV: 0.5          # 能量过滤阈值，剔除冷粒子
  vrange: [0, 40]              # 色标范围 (MeV)
  bins: 400                    # 空间分辨率
```

## 输出结构

```
SDF_Outputs/
├── Plots_XY_Density_Electron/
│   ├── XY_Electron_output0001.png
│   └── XY_Electron_output0002.png
├── Plots_XY_Density_Proton/
├── Plots_XZ_Density_Electron/
├── Plots_Tilted_YZ_Density_Proton/
├── Plots_Ey/
├── Plots_Bz/
├── Plots_Spectrum/
│   ├── Spec_output0001.png
│   └── Spec_output0002.png
├── Plots_PhaseSpace_Electron/
├── Plots_PhaseSpace_Proton/
├── Plots_EnergyMap_Proton/
├── Plots_Detector_5cm_Proton/
│   ├── Detector_output0001_All.png
│   ├── Detector_output0001_E15-20.png
│   └── ...
└── SDF_Variables_List/
    └── Variables_output0001.txt
```

## Slurm 脚本使用

Slurm 脚本位于 `slurm/` 目录下。

### 基本用法

```bash
# 进入 slurm 目录
cd slurm

# 运行所有插件
sbatch run.slurm

# 运行单个插件
sbatch spectrum.slurm
sbatch fields.slurm
```

### 使用实验配置

编辑 Slurm 脚本，取消注释 CONFIG 行：

```bash
#!/bin/bash
#SBATCH -J plot
#SBATCH -N 1
#SBATCH -n 1
#SBATCH -t 24:00:00
#SBATCH --mem=64G

# 指定实验配置
CONFIG="--config tnsa_2024"

cd ../..
python SDF_3D/main.py -t spectrum -f "*.sdf" $CONFIG
```

## 添加自定义插件

1. 在 `plugins/` 目录下创建新文件：

```python
# plugins/plot_my_analysis.py
import matplotlib.pyplot as plt
from core import BasePlotter


class MyAnalysisPlotter(BasePlotter):
    name = "my_analysis"  # 命令行调用的代号

    def plot(self, data, base_name, time_fs):
        # 你的分析逻辑
        # data: SDF 数据对象
        # base_name: 文件名（不含扩展名）
        # time_fs: 时间（飞秒）
        
        fig = plt.figure(figsize=self.config.output.figsize)
        # ... 绘图代码 ...
        
        # 保存图片
        subdir = "Plots_MyAnalysis"
        filename = f"MyAnalysis_{base_name}.png"
        self.save_figure(fig, subdir, filename)
        
        return True  # 成功返回 True
```

2. 直接使用，无需注册：

```bash
python main.py -t my_analysis -f "*.sdf"
```

插件通过 `__init_subclass__` 机制自动注册到 `BasePlotter.registry`。

## 常见问题

### Q: 内存不足 (OOM)

30GB+ 的 SDF 文件需要大量内存。建议：
- 申请 128G+ 内存
- 一次只运行一个插件：`python main.py -t spectrum -f "*.sdf"`
- 检查是否有内存泄漏（长时间运行后内存持续增长）

### Q: 找不到 sdf_helper

```bash
# 方法 1：从 EPOCH 官方仓库获取
git clone https://github.com/Warwick-Plasma/epoch.git
pip install epoch/sdf_helper

# 方法 2：设置 PYTHONPATH
export PYTHONPATH=/path/to/epoch/sdf_helper:$PYTHONPATH
```

### Q: 变量不存在

运行 `list_vars` 插件查看 SDF 文件中实际包含的变量：

```bash
python main.py -t list_vars -f "output0010.sdf"
cat ../SDF_Outputs/SDF_Variables_List/Variables_output0010.txt
```

### Q: 图片全白/全黑

调整配置文件中对应插件的 `vrange` 参数，或检查视野范围设置。

### Q: 如何添加新粒子种类

在实验配置文件中添加：

```yaml
density:
  species:
    - name: Electron
      cmap: turbo
      vrange: [0, 40]
    - name: Proton
      cmap: turbo
      vrange: [0, 10]
    - name: Carbon   # 新增
      cmap: turbo
      vrange: [0, 5]
```

## 许可证

[待定]

## 作者

[待定]

## 致谢

- EPOCH 开发团队 (Warwick Plasma)
- sdf_helper 库作者
