# core/data_loader.py
import sdf_helper as sh

class SDFLoader:
    def __init__(self, fname):
        self.fname = fname
        self.data = None

    def __enter__(self):
        """进入 with 块时自动调用：极速静默读取"""
        self.data = sh.getdata(self.fname, verbose=False)
        return self.data

    def __exit__(self, exc_type, exc_val, exc_tb):
        """离开 with 块时自动调用：清理内存，永不 OOM"""
        self.data = None
        # 返回 False 表示如果有错误，继续向上抛出
        return False