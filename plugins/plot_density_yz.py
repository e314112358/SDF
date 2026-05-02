import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import RegularGridInterpolator

from core import BasePlotter


class DensityYZPlotter(BasePlotter):
    name = "density_yz"

    def _plot_tilted_slice(self, data, base_name, time_fs, species_cfg):
        """绘制倾斜 YZ 切片"""
        import sdf_helper as sh
        
        species_name = species_cfg['name']
        full_var_name = f"Derived_Number_Density_{species_name}"
        
        density_block = self.safe_getattr(data, full_var_name)
        if density_block is None:
            return False
        
        # 归一化密度
        if density_block.units != "n_c":
            density_block.data = density_block.data / self.config.laser.n_c
            density_block.units = "n_c"
        
        # 获取网格
        grid = data.Grid_Grid_mid.data
        x_um = grid[0] * 1e6
        y_um = grid[1] * 1e6
        z_um = grid[2] * 1e6
        
        # 构建插值器
        interpolator = RegularGridInterpolator(
            (x_um, y_um, z_um), density_block.data,
            bounds_error=False, fill_value=0.0
        )
        
        # 读取配置
        ts = self.config.tilted_slice
        theta_rad = np.radians(ts.theta_deg)
        x_pivot, y_pivot = ts.pivot_um
        
        # 生成网格
        yp_coords = np.linspace(ts.y_prime_limits[0], ts.y_prime_limits[1], 500)
        z_coords = np.linspace(self.config.view.z_limits[0], self.config.view.z_limits[1], 500)
        YP, Z_mesh = np.meshgrid(yp_coords, z_coords)
        
        # 初始化平均密度
        averaged_data = np.zeros_like(YP, dtype=float)
        
        # 在厚度内采样累加
        xp_array = np.linspace(ts.depth_range_um[0], ts.depth_range_um[1], ts.steps)
        for xp in xp_array:
            X_global = x_pivot + xp * np.cos(theta_rad) - YP * np.sin(theta_rad)
            Y_global = y_pivot + xp * np.sin(theta_rad) + YP * np.cos(theta_rad)
            Z_global = Z_mesh
            
            points = np.stack((X_global.ravel(), Y_global.ravel(), Z_global.ravel()), axis=-1)
            sliced_data = interpolator(points).reshape(YP.shape)
            averaged_data += sliced_data
        
        averaged_data /= ts.steps
        
        # 绘图
        fig = plt.figure(figsize=self.config.output.figsize)
        im = plt.pcolormesh(YP, Z_mesh, averaged_data, cmap=species_cfg['cmap'],
                            vmin=species_cfg['vrange'][0], vmax=species_cfg['vrange'][1],
                            shading='auto')
        
        cbar = plt.colorbar(im)
        cbar.set_label('Average Density (n_c)', fontsize='large')
        
        plt.xlabel("Tilted Target Surface Y' (um)")
        plt.ylabel("Z Axis (um)")
        
        title_str = (f"Avg YZ Plane (X': {ts.depth_range_um[0]} to {ts.depth_range_um[1]} um) | "
                     f"{species_name} | t = {time_fs:.0f} fs")
        plt.title(title_str, fontsize='medium', y=1.03)
        sh.axis_offset()
        
        # 保存
        subdir = f"Plots_Tilted_YZ_Density_{species_name}"
        filename = f"AvgYZ_{species_name}_{base_name}.png"
        self.save_figure(fig, subdir, filename)
        
        return True

    def plot(self, data, base_name, time_fs):
        success = False
        for species_cfg in self.config.density.species:
            if self._plot_tilted_slice(data, base_name, time_fs, species_cfg):
                success = True
        return success
