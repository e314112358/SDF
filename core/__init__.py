from .base_plotter import BasePlotter
from .physics import compute_kinetic_energy_mev, get_particle_mass

__all__ = ['BasePlotter', 'compute_kinetic_energy_mev', 'get_particle_mass']

# 延迟导入 SDFLoader，避免 sdf_helper 未安装时的导入错误
def __getattr__(name):
    if name == 'SDFLoader':
        from .data_loader import SDFLoader
        return SDFLoader
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
