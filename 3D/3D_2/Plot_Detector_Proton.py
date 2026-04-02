import matplotlib
matplotlib.use('Agg') # 无头模式

import sdf_helper as sh
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm
import scipy.constants as const
import numpy as np
import glob
import os

# ==========================================
# 1. 探测器与物理参数设置
# ==========================================
L_DETECTOR_M = 0.05  # 探测器距离：0.05 米 (5 cm)
SPECIES_NAME = "Proton"

# 探测器屏幕大小设置 (单位：cm)
SCREEN_LIMIT_CM = 4.0  # 建议稍微调大一点，看清低能发散光晕
BINS = 300  # 像素分辨率：300x300

# 🌟 【核心升级】：定义你要一次性画出的所有能量段 (MeV)
# None 表示全能量段。你可以往列表里无限添加你想要的区间！
ENERGY_FILTERS = [
    None,            # 画第一张：全能量叠加图
    [1.0, 5.0],      # 画第二张：1~5 MeV 低能段
    [5.0, 15.0],     # 画第三张：5~15 MeV 中能段
    [15.0, 30.0],    # 画第四张：15~30 MeV 高能段
    [30.0, 50.0],     # 画第五张：30~50 MeV 极高能段
    [50.0, 70.0]
]

output_dir = "Plots_Detector_5cm_Turbo"
os.makedirs(output_dir, exist_ok=True)

# ==========================================
# 2. 核心处理函数
# ==========================================
def plot_rcf_film(fname):
    try:
        data = sh.getdata(fname, verbose=False)
        base_name = os.path.splitext(fname)[0]
        time_fs = data.Header['time'] * 1e15
        
        # 1. 尝试获取粒子动量与权重数据块
        var_px = getattr(data, f"Particles_Px_{SPECIES_NAME}", None)
        var_py = getattr(data, f"Particles_Py_{SPECIES_NAME}", None)
        var_pz = getattr(data, f"Particles_Pz_{SPECIES_NAME}", None)
        var_w  = getattr(data, f"Particles_Weight_{SPECIES_NAME}", None)
        
        if not all([var_px, var_py, var_pz, var_w]):
            print(f"⚠️ [{fname}] 跳过: 缺少宏粒子动量或权重数据。")
            return
            
        px = var_px.data
        py = var_py.data
        pz = var_pz.data
        weight = var_w.data
        
        # 2. 基础筛选：只保留向前飞行的质子 (Px > 0)
        mask_forward = px > 0
        px = px[mask_forward]; py = py[mask_forward]; pz = pz[mask_forward]; w = weight[mask_forward]
        
        if len(px) == 0:
            print(f"⚠️ [{fname}] 没有向前飞行的粒子。")
            return
            
        # 🌟 性能优化：在循环外，只计算一次所有粒子的动能和投影坐标！
        print(f"⏳ 正在计算 {len(px)} 个质子的动能和投影坐标...")
        p_square = px**2 + py**2 + pz**2
        gamma = np.sqrt(1.0 + p_square / (const.m_p * const.c)**2)
        ek_mev_all = (gamma - 1.0) * const.m_p * const.c**2 / (const.e * 1e6)
        
        Y_det_cm_all = (py / px) * L_DETECTOR_M * 100.0
        Z_det_cm_all = (pz / px) * L_DETECTOR_M * 100.0

        # 3. 遍历你设定的所有能量段，开始极速批量出图
        for e_filter in ENERGY_FILTERS:
            if e_filter is None:
                # 全能量段，不用过滤
                mask_e = np.ones(len(px), dtype=bool)
                energy_title = "(All Energies)"
                filter_tag = "_All"
            else:
                # 特定能量段过滤
                mask_e = (ek_mev_all >= e_filter[0]) & (ek_mev_all <= e_filter[1])
                energy_title = f"({e_filter[0]}-{e_filter[1]} MeV)"
                filter_tag = f"_E{e_filter[0]}-{e_filter[1]}"
                
            # 切出当前能量段的数据
            Y_curr = Y_det_cm_all[mask_e]
            Z_curr = Z_det_cm_all[mask_e]
            w_curr = w[mask_e]
            
            if len(Y_curr) == 0:
                print(f"  ➖ 能量段 {energy_title} 内没有粒子，已跳过。")
                continue
                
            # 4. 2D 像素化 (生成探测器直方图)
            screen_range = [[-SCREEN_LIMIT_CM, SCREEN_LIMIT_CM], [-SCREEN_LIMIT_CM, SCREEN_LIMIT_CM]]
            H, yedges, zedges = np.histogram2d(Y_curr, Z_curr, bins=BINS, range=screen_range, weights=w_curr)
            
            # 归一化处理
            h_max = np.max(H)
            H_normalized = H / h_max if h_max > 0 else H

            # 5. 画图与美化
            fig = plt.figure(figsize=(7, 6))
            im = plt.pcolormesh(yedges, zedges, H_normalized.T, cmap='turbo', 
                                norm=LogNorm(vmin=1e-4, vmax=1.0), shading='auto')
            
            cbar = plt.colorbar(im)
            cbar.set_label('Normalized Proton Yield', fontsize=12)
            
            plt.title(f"Proton Detector at 5 cm {energy_title}\n$t = {time_fs:.0f} \\, fs$", fontsize=14, pad=10)
            plt.xlabel("Y Position on Screen (cm)", fontsize=12, fontweight='bold')
            plt.ylabel("Z Position on Screen (cm)", fontsize=12, fontweight='bold')
            
            plt.axhline(0, color='white', linestyle='--', alpha=0.3, lw=1)
            plt.axvline(0, color='white', linestyle='--', alpha=0.3, lw=1)
            
            save_path = os.path.join(output_dir, f"Detector_5cm_{base_name}{filter_tag}.png")
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            plt.close(fig)
            
            print(f"  ✅ 成功导出: {filter_tag} 投影图")

    except Exception as e:
        print(f"❌ [{fname}] 处理失败: {str(e)}")

# ==========================================
# 3. 主程序启动
# ==========================================
def main():
    sdf_files = sorted(glob.glob("*.sdf"))
    target_files = sdf_files[-1:]  # 通常只画最后一步
    
    print(f"🚀 开始生成质子 5cm 探测器投影 (多能段极速版)...")
    for fname in target_files:
        plot_rcf_film(fname)
    print("🎉 所有能量段投影图导出完成！")

if __name__ == "__main__":
    main()