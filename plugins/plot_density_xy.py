from plugins.base_density import BaseDensityPlotter


class DensityXYPlotter(BaseDensityPlotter):
    name = "density_xy"

    def plot(self, data, base_name, time_fs):
        success = False
        for species_cfg in self.config.density.species:
            if self._plot_density(data, base_name, time_fs, species_cfg, 'XY', {'iz': -1}):
                success = True
        return success
