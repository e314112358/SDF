from plugins.base_density import BaseDensityPlotter


class DensityXZPlotter(BaseDensityPlotter):
    name = "density_xz"

    def plot(self, data, base_name, time_fs):
        success = False
        for species_cfg in self.config.density.species:
            if self._plot_density(data, base_name, time_fs, species_cfg, 'XZ', {'iy': -1}):
                success = True
        return success
