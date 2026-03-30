import sdf_helper as sh
import matplotlib.pyplot as plt
import scipy.constants as const
import numpy as np
import glob
import os

# ==========================================
# 0. 创建输出文件夹 (新增部分)
# ==========================================
ey_dir = "Plots_Ey"  # 电场图片存放文件夹
bz_dir = "Plots_Bz"  # 磁场图片存放文件夹

# exist_ok=True 表示如果文件夹已经存在，就不会报错，直接继续使用
os.makedirs(ey_dir, exist_ok=True)
os.makedirs(bz_dir, exist_ok=True)
print(f"已就绪输出文件夹: '{ey_dir}' 和 '{bz_dir}'")

# ==========================================
# 1. 物理常数与归一化基准计算 (放在循环外)
# ==========================================
I_0_W_cm2 = 1.5e21  
I_0_W_m2 = I_0_W_cm2 * 1e4  # 转换为 W/m^2

# 计算电场基准 E_0 和磁场基准 B_0
E_0 = np.sqrt(2 * I_0_W_m2 / (const.c * const.epsilon_0))
B_0 = E_0 / const.c  # 真空中 B_0 = E_0 / c

# ==========================================
# 2. 自动搜索所有的 sdf 文件并排序
# ==========================================
sdf_files = sorted(glob.glob("*.sdf"))
print(f"总共找到 {len(sdf_files)} 个 SDF 文件，开始批量处理电磁场...")

# ==========================================
# 3. 开始循环批量画图
# ==========================================
for fname in sdf_files:
    try:
        data = sh.getdata(fname, verbose=False)
        base_name = os.path.splitext(fname)[0]
        
        # 提取时间并转换为飞秒 (fs)
        current_time_sec = data.Header['time']
        time_fs = current_time_sec * 1e15
        title_str = f"$t = {time_fs:.0f} \\, fs$"
        
        # ----------------------------------------
        # [A] 处理并绘制电场 E_y
        # ----------------------------------------
        ey_block = data.Electric_Field_Ey 
        ey_block.data = ey_block.data / E_0
        ey_block.units = "E_0"
        ey_block.name = "Normalized E_y"
        
        plt.figure(figsize=(10, 5))
        plt.set_cmap('RdBu') 
        # title=False 关掉原有的 ps 标题
        sh.plot2d(ey_block, iz=-1, vrange=[-1, 1], title=False)
        plt.title(title_str, fontsize='large', y=1.03) # 加上自定义的 fs 标题
        sh.axis_offset()
        
        # 【修改点】：将图片存入 ey_dir 文件夹下
        out_ey = os.path.join(ey_dir, f"Normalized_Ey_{base_name}.png")
        plt.savefig(out_ey, dpi=300, bbox_inches='tight')
        plt.close() 
        
        # ----------------------------------------
        # [B] 处理并绘制磁场 B_z
        # ----------------------------------------
        bz_block = data.Magnetic_Field_Bz 
        bz_block.data = bz_block.data / B_0
        bz_block.units = "B_0"
        bz_block.name = "Normalized B_z"
        
        plt.figure(figsize=(10, 5))
        plt.set_cmap('RdBu') # 磁场同样使用红蓝冷暖色带表示振荡
        sh.plot2d(bz_block, iz=-1, vrange=[-1, 1], title=False)
        plt.title(title_str, fontsize='large', y=1.03) 
        sh.axis_offset()
        
        # 【修改点】：将图片存入 bz_dir 文件夹下
        out_bz = os.path.join(bz_dir, f"Normalized_Bz_{base_name}.png")
        plt.savefig(out_bz, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"成功: [{fname}] -> 输出了 Ey 和 Bz 图片到对应文件夹")
        
    except AttributeError:
        # 如果找不到 Electric_Field_Ey 或 Magnetic_Field_Bz，优雅跳过
        print(f"跳过: [{fname}] (未找到完整的电磁场数据)")
        plt.close() 

print("🎉 所有电磁场文件批量处理并分类导出完成！")