import gc
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm
import scipy.constants as const

from core import BasePlotter, compute_kinetic_energy_mev, get_particle_mass


class RCFDetectorPlotter(BasePlotter):
    name = "rcf_detector"

    def plot(self, data, base_name, time_fs):
        try:
            rcf = self.config.rcf
            species_name = rcf.species_name
            var_suffix = rcf.var_suffix
            
            # 获取粒子数据
            var_px = self.safe_getattr(data, f"Particles_Px_{var_suffix}")
            var_py = self.safe_getattr(data, f"Particles_Py_{var_suffix}")
            var_pz = self.safe_getattr(data, f"Particles_Pz_{var_suffix}")
            var_w = self.safe_getattr(data, f"Particles_Weight_{var_suffix}")
            
            if any(v is None for v in [var_px, var_py, var_pz, var_w]):
                return False
            
            # 提取数据并释放引用
            px = var_px.data
            py = var_py.data
            pz = var_pz.data
            weight = var_w.data
            
            del var_px, var_py, var_pz, var_w
            
            # 过滤向前飞行的粒子
            mask_forward = px > 0
            px = px[mask_forward]
            py = py[mask_forward]
            pz = pz[mask_forward]
            w = weight[mask_forward]
            
            del mask_forward, weight
            gc.collect()
            
            if len(px) == 0:
                print(f"[RCF] 没有向前飞行的 {species_name}，已跳过。")
                return True
            
            # 计算动能和投影坐标
            mass = get_particle_mass(species_name)
            ek_mev = compute_kinetic_energy_mev(px, py, pz, mass)
            
            l_det_cm = rcf.detector_distance_m * 100
            y_det_cm = (py / px) * l_det_cm
            z_det_cm = (pz / px) * l_det_cm
            
            del px, py, pz
            gc.collect()
            
            # 遍历能量段
            success_count = 0
            for e_filter in rcf.energy_filters:
                if e_filter is None:
                    mask_e = np.ones(len(ek_mev), dtype=bool)
                    energy_title = "(All Energies)"
                    filter_tag = "_All"
                else:
                    mask_e = (ek_mev >= e_filter[0]) & (ek_mev <= e_filter[1])
                    energy_title = f"({e_filter[0]}-{e_filter[1]} MeV)"
                    filter_tag = f"_E{e_filter[0]}-{e_filter[1]}"
                
                y_curr = y_det_cm[mask_e]
                z_curr = z_det_cm[mask_e]
                w_curr = w[mask_e]
                
                if len(y_curr) == 0:
                    continue
                
                screen_range = [[-rcf.screen_limit_cm, rcf.screen_limit_cm],
                               [-rcf.screen_limit_cm, rcf.screen_limit_cm]]
                H, yedges, zedges = np.histogram2d(y_curr, z_curr, bins=rcf.bins,
                                                   range=screen_range, weights=w_curr)
                
                h_max = np.max(H)
                H_normalized = H / h_max if h_max > 0 else H
                
                fig = plt.figure(figsize=(7, 6))
                im = plt.pcolormesh(yedges, zedges, H_normalized.T, cmap='turbo',
                                   norm=LogNorm(vmin=1e-4, vmax=1.0), shading='auto')
                
                cbar = plt.colorbar(im)
                cbar.set_label(f'Normalized {species_name} Yield', fontsize=12)
                
                plt.title(f"{species_name} Detector at {l_det_cm:.0f} cm {energy_title}\n"
                         f"$t = {time_fs:.0f} fs$", fontsize=14, pad=10)
                plt.xlabel("Y Position on Screen (cm)", fontsize=12, fontweight='bold')
                plt.ylabel("Z Position on Screen (cm)", fontsize=12, fontweight='bold')
                
                plt.axhline(0, color='white', linestyle='--', alpha=0.3, lw=1)
                plt.axvline(0, color='white', linestyle='--', alpha=0.3, lw=1)
                
                subdir = f"Plots_Detector_{l_det_cm:.0f}cm_{species_name}"
                filename = f"Detector_{base_name}{filter_tag}.png"
                self.save_figure(fig, subdir, filename)
                
                success_count += 1
                
                del mask_e, y_curr, z_curr, w_curr, H, H_normalized
                gc.collect()
            
            return success_count > 0
            
        except Exception as e:
            print(f"[RCF] 绘图报错: {e}")
            return False
