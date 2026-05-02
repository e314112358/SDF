from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Tuple, Optional
import yaml
import scipy.constants as const
import numpy as np


@dataclass
class LaserConfig:
    """激光参数"""
    wavelength_um: float = 0.8
    intensity_W_cm2: float = 4e21

    @property
    def wavelength_m(self) -> float:
        return self.wavelength_um * 1e-6

    @property
    def omega_l(self) -> float:
        return 2 * np.pi * const.c / self.wavelength_m

    @property
    def n_c(self) -> float:
        return (const.epsilon_0 * const.m_e * self.omega_l**2) / (const.e**2)

    @property
    def e_0(self) -> float:
        i_0_w_m2 = self.intensity_W_cm2 * 1e4
        return np.sqrt(2 * i_0_w_m2 / (const.c * const.epsilon_0))

    @property
    def b_0(self) -> float:
        return self.e_0 / const.c


@dataclass
class ViewConfig:
    """视野范围 (um)"""
    x_limits: Tuple[float, float] = (-8.0, 22.0)
    y_limits: Tuple[float, float] = (-7.5, 7.5)
    z_limits: Tuple[float, float] = (-10.0, 10.0)


@dataclass
class DensityConfig:
    """密度图配置"""
    species: List[dict] = field(default_factory=lambda: [
        {'name': 'Electron', 'cmap': 'turbo', 'vrange': [0, 40]},
        {'name': 'Proton', 'cmap': 'turbo', 'vrange': [0, 10]},
    ])


@dataclass
class TiltedSliceConfig:
    """倾斜切片参数"""
    theta_deg: float = -45.0
    pivot_um: Tuple[float, float] = (0.0, 0.0)
    y_prime_limits: Tuple[float, float] = (-8.0, 8.0)
    depth_range_um: Tuple[float, float] = (-0.3, 0.3)
    steps: int = 10


@dataclass
class RCFConfig:
    """RCF探测器配置"""
    detector_distance_m: float = 0.05
    screen_limit_cm: float = 4.0
    species_name: str = "Proton"
    var_suffix: str = "subset_Proton_only_Proton"
    bins: int = 300
    energy_filters: List[List[float]] = field(default_factory=lambda: [
        [15.0, 20.0], [20.0, 25.0], [25.0, 30.0], [30.0, 35.0],
        [35.0, 40.0], [40.0, 45.0], [45.0, 50.0], [50.0, 55.0],
        [55.0, 60.0], [60.0, 65.0], [65.0, 70.0], [70.0, 75.0],
    ])


@dataclass
class EnergyMapConfig:
    """能量分布图配置"""
    species_name: str = "Proton"
    var_suffix: str = "subset_Proton_only_Proton"
    min_energy_MeV: float = 0.5
    vrange: Tuple[float, float] = (0, 40)
    bins: int = 400
    x_limits: Tuple[float, float] = (-8.0, 22.0)
    y_limits: Tuple[float, float] = (-15.0, 15.0)
    z_limits: Tuple[float, float] = (-15.0, 15.0)


@dataclass
class SpectrumConfig:
    """能谱图配置"""
    species: List[dict] = field(default_factory=lambda: [
        {'name': 'Electron', 'var_prefix': 'E'},
        {'name': 'Proton', 'var_prefix': 'P'},
    ])
    energy_limits_MeV: Tuple[float, float] = (0, 100)


@dataclass
class PhaseSpaceConfig:
    """相空间配置"""
    species: List[dict] = field(default_factory=lambda: [
        {'name': 'Electron', 'var_prefix': 'E'},
        {'name': 'Proton', 'var_prefix': 'P'},
    ])


@dataclass
class FieldsConfig:
    """场分量配置"""
    components: List[str] = field(default_factory=lambda: ['Ey', 'Bz', 'Ex', 'Bx', 'By'])
    vrange: Tuple[float, float] = (-2, 2)
    cmap: str = 'RdBu'


@dataclass
class ListVarsConfig:
    """变量清单配置"""
    target: str = 'last'  # 'last', 'all', 或文件编号如 '0015'


@dataclass
class OutputConfig:
    """输出配置"""
    root: str = ""
    dpi: int = 300
    figsize: Tuple[float, float] = (8, 6)


@dataclass
class Config:
    """主配置类"""
    name: str = "default"
    description: str = ""
    laser: LaserConfig = field(default_factory=LaserConfig)
    view: ViewConfig = field(default_factory=ViewConfig)
    output: OutputConfig = field(default_factory=OutputConfig)
    density: DensityConfig = field(default_factory=DensityConfig)
    tilted_slice: TiltedSliceConfig = field(default_factory=TiltedSliceConfig)
    rcf: RCFConfig = field(default_factory=RCFConfig)
    energy_map: EnergyMapConfig = field(default_factory=EnergyMapConfig)
    spectrum: SpectrumConfig = field(default_factory=SpectrumConfig)
    phase_space: PhaseSpaceConfig = field(default_factory=PhaseSpaceConfig)
    fields: FieldsConfig = field(default_factory=FieldsConfig)
    list_vars: ListVarsConfig = field(default_factory=ListVarsConfig)

    def get_output_root(self, script_dir: Path) -> Path:
        """获取输出根目录"""
        if self.output.root:
            return Path(self.output.root)
        return script_dir.parent / "SDF_Outputs"


def _merge_dict(base: dict, override: dict) -> dict:
    """递归合并字典"""
    result = base.copy()
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = _merge_dict(result[key], value)
        else:
            result[key] = value
    return result


def _dict_to_dataclass(data: dict, cls):
    """将字典转换为dataclass"""
    import dataclasses
    field_names = {f.name for f in dataclasses.fields(cls)}
    filtered = {k: v for k, v in data.items() if k in field_names}
    return cls(**filtered)


def load_config(experiment_name: Optional[str] = None, config_dir: Optional[Path] = None) -> Config:
    """加载配置
    
    Args:
        experiment_name: 实验名称，对应 experiments/ 目录下的 YAML 文件名
        config_dir: 配置目录路径，默认为当前文件所在目录
    
    Returns:
        Config 对象
    """
    if config_dir is None:
        config_dir = Path(__file__).parent
    
    # 加载默认配置
    default_file = config_dir / "default.yaml"
    if default_file.exists():
        with open(default_file, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f) or {}
    else:
        data = {}
    
    # 如果指定了实验配置，合并覆盖
    if experiment_name:
        exp_file = config_dir / "experiments" / f"{experiment_name}.yaml"
        if not exp_file.exists():
            raise FileNotFoundError(f"实验配置文件不存在: {exp_file}")
        with open(exp_file, 'r', encoding='utf-8') as f:
            exp_data = yaml.safe_load(f) or {}
        data = _merge_dict(data, exp_data)
    
    # 构建配置对象
    config = Config()
    config.name = data.get('name', 'default')
    config.description = data.get('description', '')
    
    if 'laser' in data:
        config.laser = _dict_to_dataclass(data['laser'], LaserConfig)
    if 'view' in data:
        config.view = _dict_to_dataclass(data['view'], ViewConfig)
    if 'output' in data:
        config.output = _dict_to_dataclass(data['output'], OutputConfig)
    if 'density' in data:
        config.density = _dict_to_dataclass(data['density'], DensityConfig)
    if 'tilted_slice' in data:
        config.tilted_slice = _dict_to_dataclass(data['tilted_slice'], TiltedSliceConfig)
    if 'rcf' in data:
        config.rcf = _dict_to_dataclass(data['rcf'], RCFConfig)
    if 'energy_map' in data:
        config.energy_map = _dict_to_dataclass(data['energy_map'], EnergyMapConfig)
    if 'spectrum' in data:
        config.spectrum = _dict_to_dataclass(data['spectrum'], SpectrumConfig)
    if 'phase_space' in data:
        config.phase_space = _dict_to_dataclass(data['phase_space'], PhaseSpaceConfig)
    if 'fields' in data:
        config.fields = _dict_to_dataclass(data['fields'], FieldsConfig)
    if 'list_vars' in data:
        config.list_vars = _dict_to_dataclass(data['list_vars'], ListVarsConfig)
    
    return config
