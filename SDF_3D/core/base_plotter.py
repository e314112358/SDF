# core/base_plotter.py
from abc import ABC, abstractmethod

class BasePlotter(ABC):
    # 终极黑科技：插件自动注册表
    registry = {}
    
    # 插件的代号，必须在子类中重写 (例如 "fields")
    name = "base" 

    def __init_subclass__(cls, **kwargs):
        """当任何类继承 BasePlotter 时，自动触发，将自己写入字典"""
        super().__init_subclass__(**kwargs)
        if cls.name != "base":
            BasePlotter.registry[cls.name] = cls

    @abstractmethod
    def plot(self, data, base_name, time_fs):
        """所有插件必须遵守合同，实现这个 plot 方法"""
        pass