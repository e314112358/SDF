import os
import gc
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm
import scipy.constants as const
import config
from core.base_plotter import BasePlotter

class RCFDetectorPlotter(BasePlotter):
    name = "rcf_detector"

    def __init__(self):
        # 探测器参数
        self.l_detector_m = getattr(config, 'RCF_L_DETECTOR_M', 0.05)
        
        # 将显示名称与实际的变量名后缀分离
        self.species_name = getattr(config, 'RCF_SPECIES_NAME', "Proton")
        # 匹配你提供的 subset 变量名后缀
        self.var_suffix = getattr(config, 'RCF_VAR_SUFFIX', "subset_Proton_only_Proton")
        
        self.screen_limit_cm = getattr(config, 'RCF_SCREEN_LIMIT_CM', 4.0)
        self.bins = getattr(config, 'RCF_BINS', 300)
        
        self.energy_filters = getattr(config, 'RCF_ENERGY_FILTERS', [
            None,
            [1.0, 5.0],
            [5.0, 15.0],
            [15.0, 30.0],
            [30.0, 50.0],
            [50.0, 70.0]
        ])

    def plot(self, data, base_name, time_fs):
        try:
            # 1. 精准获取 subset 变量数据块
            var_px = getattr(data, f"Particles_Px_{self.var_suffix}")
            var_py = getattr(data, f"Particles_Py_{self.var_suffix}")
            var_pz = getattr(data, f"Particles_Pz_{self.var_suffix}")
            var_w  = getattr(data, f"Particles_Weight_{self.var_suffix}")
            
            # 提取为 numpy 数组
            px = var_px.data
            py = var_py.data
            pz = var_pz.data
            weight = var_w.data
            
            # 【内存优化】：立即解除对 SDF block 的引用
            del var_px, var_py, var_pz, var_w
            
            # 2. 过滤向前飞行的粒子
            mask_forward = px > 0
            px = px[mask_forward]
            py = py[mask_forward]
            pz = pz[mask_forward]
            w = weight[mask_forward]
            
            # 【内存优化】：删除原始的 4 亿全量数据和掩码，强制回收内存
            del mask_forward
            gc.collect() 
            
            if len(px) == 0:
                print(f"[RCF] 没有向前飞行的 {self.species_name}，已跳过。")
                return True
                
            mass = const.m_e if "electron" in self.species_name.lower() else const.m_p
                
            # 3. 计算动能和投影坐标
            p_square = px**2 + py**2 + pz**2
            gamma = np.sqrt(1.0 + p_square / (mass * const.c)**2)
            ek_mev_all = (gamma - 1.0) * mass * const.c**2 / (const.e * 1e6)
            
            Y_det_cm_all = (py / px) * self.l_detector_m * 100.0
            Z_det_cm_all = (pz / px) * self.l_detector_m * 100.0
            
            # 【内存优化】：计算完毕后，立刻删除不再需要的动量数组
            del px, py, pz, p_square, gamma
            gc.collect()

            success_count = 0
            output_base = getattr(config, 'OUTPUT_ROOT', '.')
            output_dir = os.path.join(output_base, f"Plots_Detector_{self.l_detector_m*100:.0f}cm_{self.species_name}")
            os.makedirs(output_dir, exist_ok=True)

            # 4. 遍历能量段批量出图
            for e_filter in self.energy_filters:
                if e_filter is None:
                    mask_e = np.ones(len(ek_mev_all), dtype=bool)
                    energy_title = "(All Energies)"
                    filter_tag = "_All"
                else:
                    mask_e = (ek_mev_all >= e_filter[0]) & (ek_mev_all <= e_filter[1])
                    energy_title = f"({e_filter[0]}-{e_filter[1]} MeV)"
                    filter_tag = f"_E{e_filter[0]}-{e_filter[1]}"
                    
                Y_curr = Y_det_cm_all[mask_e]
                Z_curr = Z_det_cm_all[mask_e]
                w_curr = w[mask_e]
                
                if len(Y_curr) == 0:
                    continue
                    
                screen_range = [[-self.screen_limit_cm, self.screen_limit_cm], 
                                [-self.screen_limit_cm, self.screen_limit_cm]]
                H, yedges, zedges = np.histogram2d(Y_curr, Z_curr, bins=self.bins, 
                                                   range=screen_range, weights=w_curr)
                
                h_max = np.max(H)
                H_normalized = H / h_max if h_max > 0 else H

                fig = plt.figure(figsize=(7, 6))
                im = plt.pcolormesh(yedges, zedges, H_normalized.T, cmap='turbo', 
                                    norm=LogNorm(vmin=1e-4, vmax=1.0), shading='auto')
                
                cbar = plt.colorbar(im)
                cbar.set_label(f'Normalized {self.species_name} Yield', fontsize=12)
                
                plt.title(f"{self.species_name} Detector at {self.l_detector_m*100:.0f} cm {energy_title}\n$t = {time_fs:.0f} fs$", fontsize=14, pad=10)
                plt.xlabel("Y Position on Screen (cm)", fontsize=12, fontweight='bold')
                plt.ylabel("Z Position on Screen (cm)", fontsize=12, fontweight='bold')
                
                plt.axhline(0, color='white', linestyle='--', alpha=0.3, lw=1)
                plt.axvline(0, color='white', linestyle='--', alpha=0.3, lw=1)
                
                save_path = os.path.join(output_dir, f"Detector_{base_name}{filter_tag}.png")
                plt.savefig(save_path, dpi=300, bbox_inches='tight')
                plt.close(fig)
                
                success_count += 1
                
                # 再次清理循环内的临时变量
                del mask_e, Y_curr, Z_curr, w_curr, H, H_normalized
                gc.collect()

            return success_count > 0

        except AttributeError:
            return False
        except Exception as e:
            print(f"[{self.name}] 绘图报错: {e}")
            return False