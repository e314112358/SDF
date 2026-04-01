import matplotlib
matplotlib.use('Agg') # 【关键防护】强制使用无头模式，防止多进程画图崩溃

import sdf_helper as sh
import matplotlib.pyplot as plt
import scipy.constants as const
import numpy as np
import glob
import os
from multiprocessing import Pool

# ==========================================
# 1. 物理参数、独立范围控制与【视野裁切】
# ==========================================
WAVELENGTH = 0.8e-6  
OMEGA_L = 2 * np.pi * const.c / WAVELENGTH
N_C = (const.epsilon_0 * const.m_e * OMEGA_L**2) / (const.e**2)

SPECIES_MAP = {
    'Electron': {'cmap': 'turbo',  'vrange': [0, 200]}, 
    'Proton':   {'cmap': 'turbo',   'vrange': [0, 30]},  
    'Carbon':   {'cmap': 'turbo', 'vrange': [0, 30]},  
}

# 【新增：视野裁切取景框】单位为微米 (um)
# 根据你的第一张参考图，这里设置核心作用区，你可以随意修改
X_LIMITS = [-3, 5]  # X轴锁定在 -3 到 5 微米
Y_LIMITS = [-4, 4]  # Y轴锁定在 -4 到 4 微米 (如果是画 XZ 平面，这里就是 Z_LIMITS)

# ==========================================
# 2. 核心绘图函数
# ==========================================
def plot_density_xy(data, species_name, cmap, vrange, base_name, time_fs):
    full_var_name = f"Derived_Number_Density_{species_name}"
    
    try:
        density_block = getattr(data, full_var_name)
        
        density_block.data = density_block.data / N_C
        density_block.units = "n_c"
        density_block.name = f"Density of {species_name}"

        # 稍微调整画布比例，让它更接近你要的那种正方形/微长方形质感
        fig = plt.figure(figsize=(8, 6)) 
        plt.set_cmap(cmap)
        
        # 【XY平面专属】：iz=-1 表示沿Z轴中间切片
        sh.plot2d(density_block, iz=-1, vrange=vrange, title=False)
        
        plt.title(f"XY Plane | {species_name} Density | t = {time_fs:.0f} fs", fontsize='large', y=1.03)
        sh.axis_offset()

        # 【核心动作：强行裁切视野】
        # 这两行代码会像剪刀一样，把图片多余的白边咔嚓掉
        plt.xlim(X_LIMITS)
        plt.ylim(Y_LIMITS)

        # 文件夹带上平面标记，防止被覆盖 (文件夹已在主进程预先创建)
        output_dir = f"Plots_XY_Density_{species_name}"
        save_path = os.path.join(output_dir, f"XY_{species_name}_{base_name}.png")
        
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close(fig) # 释放内存
        return True
    
    except AttributeError:
        return False

# ==========================================
# 3. 单个文件的任务包装函数 (分发给各核心)
# ==========================================
def process_single_file(fname):
    try:
        data = sh.getdata(fname, verbose=False)
        base_name = os.path.splitext(fname)[0]
        time_fs = data.Header['time'] * 1e15
        
        success_list = []
        for species, config in SPECIES_MAP.items():
            success = plot_density_xy(data, species, config['cmap'], config['vrange'], base_name, time_fs)
            if success:
                success_list.append(species)
                
        if success_list:
            return f"✅ [{fname}] 成功导出 XY 平面: {', '.join(success_list)}"
        else:
            return f"⚠️ [{fname}] 跳过: 未找到相关粒子数据"
            
    except Exception as e:
        return f"❌ [{fname}] 处理失败: {str(e)}"

# ==========================================
# 4. 多进程主控中心
# ==========================================
def main():
    # 提前建好所有文件夹防止多线程冲突
    for species in SPECIES_MAP.keys():
        os.makedirs(f"Plots_XY_Density_{species}", exist_ok=True)
        
    sdf_files = sorted(glob.glob("*.sdf"))
    print(f"🚀 [XY 平面] 开始 8核并行 处理 {len(sdf_files)} 个文件...")

    NUM_PROCESSES = 8
    print(f"⚙️ 启动 {NUM_PROCESSES} 个并行进程池，视野锁定: X {X_LIMITS}, Y {Y_LIMITS} ...")

    with Pool(processes=NUM_PROCESSES) as pool:
        for result_msg in pool.imap(process_single_file, sdf_files):
            print(result_msg)

    print("🎉 XY 密度图批量裁剪导出完成！")

if __name__ == "__main__":
    main()