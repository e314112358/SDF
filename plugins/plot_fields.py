import matplotlib.pyplot as plt

from core import BasePlotter


class FieldPlotter(BasePlotter):
    name = "fields"

    def plot(self, data, base_name, time_fs):
        import sdf_helper as sh
        
        success = False
        
        for comp in self.config.fields.components:
            var_name = f"Electric_Field_{comp}" if comp.startswith('E') else f"Magnetic_Field_{comp}"
            
            field_block = self.safe_getattr(data, var_name)
            if field_block is None:
                continue
            
            # 归一化
            norm = self.config.laser.e_0 if comp.startswith('E') else self.config.laser.b_0
            field_block.data = field_block.data / norm
            
            fig = plt.figure(figsize=(10, 5))
            plt.set_cmap(self.config.fields.cmap)
            
            vrange = list(self.config.fields.vrange)
            iz = field_block.data.shape[2] // 2
            sh.plot2d(field_block, iz=iz, vrange=vrange, title=False)
            
            plt.title(f"{comp} Component | t = {time_fs:.0f} fs", fontsize='large', y=1.03)
            sh.axis_offset()
            
            plt.xlim(self.config.view.x_limits)
            plt.ylim(self.config.view.y_limits)
            
            subdir = f"Plots_{comp}"
            filename = f"{comp}_{base_name}.png"
            self.save_figure(fig, subdir, filename)
            
            success = True
        
        return success
