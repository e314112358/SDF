import matplotlib
matplotlib.use('Agg') # 习惯性加入无头模式，防止批量画图报错

import sdf_helper as sh
import matplotlib.pyplot as plt
import scipy.constants as const
import numpy as np
import glob
import os

# ==========================================
# 1. 物理参数与环境配置
# ==========================================
I_0_W_cm2 = 1.5e21  # 激光强度
I_0_W_m2 = I_0_W_cm2 * 1e4
E_0 = np.sqrt(2 * I_0_W_m2 / (const.c * const.epsilon_0))
B_0 = E_0 / const.c

# 定义你想画的分量：['Ex', 'Ey', 'Ez', 'Bx', 'By', 'Bz']
COMPONENTS_TO_PLOT = [ 'Ey', 'Bz'] 

# ==========================================
# 2. 核心绘图函数
# ==========================================
def plot_field_component(data, component_name, base_name, time_fs):
    """
    绘制特定方向的电磁场并归一化保存
    """
    is_electric = component_name.startswith('E')
    norm_factor = E_0 if is_electric else B_0
    norm_unit = "E_0" if is_electric else "B_0"
    
    field_type = "Electric_Field" if is_electric else "Magnetic_Field"
    full_var_name = f"{field_type}_{component_name}"
    
    try:
        # 获取数据块
        field_block = getattr(data, full_var_name)
        
        # 归一化处理
        field_block.data = field_block.data / norm_factor
        field_block.units = norm_unit
        field_block.name = f"Normalized {component_name}"

        # 准备独立画布
        fig = plt.figure(figsize=(10, 5))
        plt.set_cmap('RdBu')
        
        # 绘图
        sh.plot2d(field_block, iz=-1, vrange=[-1, 1], title=False)
        
        # 美化
        plt.title(f"$t = {time_fs:.0f} \\, fs$", fontsize='large', y=1.03)
        sh.axis_offset()

        # 路径与保存 (文件夹已在主进程预先创建)
        output_dir = f"Plots_{component_name}"
        save_path = os.path.join(output_dir, f"{component_name}_{base_name}.png")
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        
        # 【极其重要】彻底关闭 fig 释放内存
        plt.close(fig) 
        return True
    
    except AttributeError:
        return False

# ==========================================
# 3. 单个文件的处理逻辑
# ==========================================
def process_single_file(fname):
    """
    处理一个完整的 SDF 文件
    """
    try:
        data = sh.getdata(fname, verbose=False)
        base_name = os.path.splitext(fname)[0]
        time_fs = data.Header['time'] * 1e15
        
        success_list = []
        for comp in COMPONENTS_TO_PLOT:
            success = plot_field_component(data, comp, base_name, time_fs)
            if success:
                success_list.append(comp)
                
        if success_list:
            return f"✅ [{fname}] 成功导出: {', '.join(success_list)}"
        else:
            return f"⚠️ [{fname}] 跳过: 缺少指定的电磁场分量"
            
    except Exception as e:
        return f"❌ [{fname}] 处理失败: {str(e)}"

# ==========================================
# 4. 主程序 (单核串行版)
# ==========================================
def main():
    # 提前建好所有需要的文件夹
    for comp in COMPONENTS_TO_PLOT:
        os.makedirs(f"Plots_{comp}", exist_ok=True)
        
    sdf_files = sorted(glob.glob("*.sdf"))
    total_files = len(sdf_files)
    
    print(f"🚀 开始单核串行处理 {total_files} 个文件...")
    
    for fname in sdf_files:
        result_msg = process_single_file(fname)
        print(result_msg)

    print("\n🎉 任务全部完成！")

if __name__ == "__main__":
    main()