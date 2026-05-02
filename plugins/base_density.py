import matplotlib.pyplot as plt

from core import BasePlotter


class BaseDensityPlotter(BasePlotter):
    """密度图基类，提取公共逻辑"""
    
    def _normalize_density(self, density_block, n_c):
        """归一化密度到 n_c"""
        if density_block.units != "n_c":
            density_block.data = density_block.data / n_c
            density_block.units = "n_c"
        return density_block

    def _plot_density(self, data, base_name, time_fs, species_cfg, plane, slice_axis):
        """绘制密度图
        
        Args:
            data: SDF 数据
            base_name: 文件名
            time_fs: 时间 (fs)
            species_cfg: 物种配置 {'name': ..., 'cmap': ..., 'vrange': ...}
            plane: 平面名称 ('XY', 'XZ', 'YZ')
            slice_axis: 切片参数 (iz=-1 或 iy=-1)
        """
        import sdf_helper as sh
        
        species_name = species_cfg['name']
        full_var_name = f"Derived_Number_Density_{species_name}"
        
        density_block = self.safe_getattr(data, full_var_name)
        if density_block is None:
            return False
        
        density_block = self._normalize_density(density_block, self.config.laser.n_c)
        
        fig = plt.figure(figsize=self.config.output.figsize)
        plt.set_cmap(species_cfg['cmap'])
        
        sh.plot2d(density_block, **slice_axis, vrange=species_cfg['vrange'], title=False)
        
        plt.title(f"{plane} Plane | {species_name} Density | t = {time_fs:.0f} fs", 
                  fontsize='large', y=1.03)
        sh.axis_offset()
        
        # 应用视野范围
        if plane in ('XY', 'YZ'):
            plt.xlim(self.config.view.x_limits)
            plt.ylim(self.config.view.y_limits)
        elif plane == 'XZ':
            plt.xlim(self.config.view.x_limits)
            plt.ylim(self.config.view.z_limits)
        
        subdir = f"Plots_{plane}_Density_{species_name}"
        filename = f"{plane}_{species_name}_{base_name}.png"
        self.save_figure(fig, subdir, filename)
        
        return True
