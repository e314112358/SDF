import os
import numpy as np
import matplotlib.pyplot as plt
import sdf_helper as sh
from scipy.interpolate import RegularGridInterpolator
import config
from core.base_plotter import BasePlotter

class DensityYZPlotter(BasePlotter):
    name = "density_yz"

    def __init__(self):
        self.species_map = {
            'Electron': {'cmap': 'turbo',  'vrange': [0, 40]},
            'Proton':   {'cmap': 'turbo',  'vrange': [0, 10]},
        }

    def plot(self, data, base_name, time_fs):
        theta_deg = getattr(config, 'THETA_DEG', -10.0)
        theta_rad = np.radians(theta_deg)
        x_pivot_um = getattr(config, 'X_PIVOT_UM', 0.0)
        y_pivot_um = getattr(config, 'Y_PIVOT_UM', 0.0)
        y_prime_limits = getattr(config, 'Y_PRIME_LIMITS', [-8, 8])
        z_limits = getattr(config, 'Z_LIMITS', [-6, 6])
        
        # 读取积分厚度参数
        depth_range = getattr(config, 'SLICE_DEPTH_RANGE_UM', [0.0, 0.05])
        slice_steps = getattr(config, 'SLICE_STEPS', 10)

        success_count = 0
        
        for species_name, cfg in self.species_map.items():
            full_var_name = f"Derived_Number_Density_{species_name}"
            
            try:
                # 获取网格并转换为微米
                grid = data.Grid_Grid_mid.data 
                x_um = grid[0] * 1e6
                y_um = grid[1] * 1e6
                z_um = grid[2] * 1e6
                
                # 获取数据块
                density_block = getattr(data, full_var_name)
                
                # 【核心修复】：检查状态锁，防止重复除以 N_C
                if getattr(density_block, 'units', '') != "n_c":
                    density_block.data = density_block.data / config.N_C
                    density_block.units = "n_c"
                    density_block.name = f"Density of {species_name}"
                
                # 安全地获取已归一化的 3D 矩阵，供插值器使用
                density_3d = density_block.data
                
                # 构建 3D 空间插值器 (针对当前物种只构建一次，提高效率)
                interpolator = RegularGridInterpolator((x_um, y_um, z_um), density_3d, 
                                                       bounds_error=False, fill_value=0.0)
                
                # ... 下方的网格生成、循环累加和绘图代码保持原样不变 ...
                
                # 生成局部画布网格点
                yp_coords = np.linspace(y_prime_limits[0], y_prime_limits[1], 500)
                z_coords = np.linspace(z_limits[0], z_limits[1], 500)
                YP, Z_mesh = np.meshgrid(yp_coords, z_coords)
                
                # 初始化平均密度矩阵
                averaged_data = np.zeros_like(YP, dtype=float)
                
                # 在指定厚度内生成采样点
                xp_array = np.linspace(depth_range[0], depth_range[1], slice_steps)
                
                # 循环累加每个切片的数据
                for xp in xp_array:
                    X_global = x_pivot_um + xp * np.cos(theta_rad) - YP * np.sin(theta_rad)
                    Y_global = y_pivot_um + xp * np.sin(theta_rad) + YP * np.cos(theta_rad)
                    Z_global = Z_mesh
                    
                    points = np.stack((X_global.ravel(), Y_global.ravel(), Z_global.ravel()), axis=-1)
                    sliced_data = interpolator(points).reshape(YP.shape)
                    averaged_data += sliced_data
                    
                # 除以切片数量，得到平均值
                averaged_data /= slice_steps
                
                # 绘图
                fig = plt.figure(figsize=(8, 6))
                im = plt.pcolormesh(YP, Z_mesh, averaged_data, cmap=cfg['cmap'], 
                                    vmin=cfg['vrange'][0], vmax=cfg['vrange'][1], shading='auto')
                
                cbar = plt.colorbar(im)
                cbar.set_label('Average Density (n_c)', fontsize='large')
                
                plt.xlabel("Tilted Target Surface Y' (um)")
                plt.ylabel("Z Axis (um)")
                
                # 标题中注明积分范围
                title_str = f"Avg YZ Plane (X': {depth_range[0]} to {depth_range[1]} um) | {species_name} | t = {time_fs:.0f} fs"
                plt.title(title_str, fontsize='medium', y=1.03)
                sh.axis_offset() 
                
                # 保存
                output_base = getattr(config, 'OUTPUT_ROOT', '.')
                output_dir = os.path.join(output_base, f"Plots_Tilted_YZ_Density_{species_name}")
                os.makedirs(output_dir, exist_ok=True)
                
                save_path = os.path.join(output_dir, f"AvgYZ_{species_name}_{base_name}.png")
                plt.savefig(save_path, dpi=300, bbox_inches='tight')
                plt.close(fig)
                
                success_count += 1
                
            except AttributeError:
                continue
                
        return success_count > 0