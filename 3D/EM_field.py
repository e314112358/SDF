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
# 你可以根据需要删减这个列表
COMPONENTS_TO_PLOT = ['Ex','Ey', 'Bz'] 

# ==========================================
# 2. 核心绘图函数
# ==========================================
def plot_field_component(data, component_name, base_name, time_fs):
    """
    绘制特定方向的电磁场并归一化保存
    """
    # 自动根据 E 或 B 选择归一化系数和全名
    is_electric = component_name.startswith('E')
    norm_factor = E_0 if is_electric else B_0
    norm_unit = "E_0" if is_electric else "B_0"
    
    # 构造 SDF 中的标准变量全名 (例如 'Electric_Field_Ey' 或 'Magnetic_Field_Bz')
    field_type = "Electric_Field" if is_electric else "Magnetic_Field"
    full_var_name = f"{field_type}_{component_name}"
    
    try:
        # 获取数据块
        field_block = getattr(data, full_var_name)
        
        # 归一化处理（原地篡改副本以保留网格信息）
        field_block.data = field_block.data / norm_factor
        field_block.units = norm_unit
        field_block.name = f"Normalized {component_name}"

        # 准备画布
        plt.figure(figsize=(10, 5))
        plt.set_cmap('RdBu')
        
        # 绘图 (3D切片, 关掉默认标题, 限制范围)
        sh.plot2d(field_block, iz=-1, vrange=[-1, 1], title=False)
        
        # 美化：飞秒标题与PRL滤镜
        plt.title(f"$t = {time_fs:.0f} \\, fs$", fontsize='large', y=1.03)
        sh.axis_offset()

        # 文件夹管理：自动创建对应文件夹 (如 Plots_Ey)
        output_dir = f"Plots_{component_name}"
        os.makedirs(output_dir, exist_ok=True)
        
        # 保存图片
        save_path = os.path.join(output_dir, f"{component_name}_{base_name}.png")
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
        return True
    
    except AttributeError:
        return False

# ==========================================
# 3. 主程序循环
# ==========================================
def main():
    sdf_files = sorted(glob.glob("*.sdf"))
    print(f"🚀 开始批量处理 {len(sdf_files)} 个文件...")

    for fname in sdf_files:
        data = sh.getdata(fname, verbose=False)
        base_name = os.path.splitext(fname)[0]
        time_fs = data.Header['time'] * 1e15
        
        # 循环调用函数绘制所选分量
        for comp in COMPONENTS_TO_PLOT:
            success = plot_field_component(data, comp, base_name, time_fs)
            if success:
                print(f"成功: [{fname}] -> {comp} 已保存")
            else:
                print(f"跳过: [{fname}] -> 缺少 {comp} 分量")

    print("🎉 任务全部完成！")

if __name__ == "__main__":
    main()