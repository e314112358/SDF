from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional
import matplotlib.pyplot as plt

from config import Config


class BasePlotter(ABC):
    """插件基类，所有插件必须继承此类"""
    
    registry = {}
    name = "base"

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        if cls.name != "base":
            BasePlotter.registry[cls.name] = cls

    def __init__(self, config: Config):
        self.config = config
        self._output_dirs = {}

    def get_output_dir(self, subdir: str) -> Path:
        """获取输出目录，自动创建"""
        if subdir not in self._output_dirs:
            output_root = self.config.get_output_root(Path(__file__).parent.parent)
            output_dir = output_root / subdir
            output_dir.mkdir(parents=True, exist_ok=True)
            self._output_dirs[subdir] = output_dir
        return self._output_dirs[subdir]

    def save_figure(self, fig: plt.Figure, subdir: str, filename: str) -> Path:
        """保存图片并关闭"""
        save_path = self.get_output_dir(subdir) / filename
        fig.savefig(save_path, dpi=self.config.output.dpi, bbox_inches='tight')
        plt.close(fig)
        return save_path

    def safe_getattr(self, data, var_name: str):
        """安全获取属性，不存在时返回 None"""
        return getattr(data, var_name, None)

    @abstractmethod
    def plot(self, data, base_name: str, time_fs: float) -> bool:
        """绘图接口，返回是否成功"""
        pass
