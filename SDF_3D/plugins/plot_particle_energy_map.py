import os
import gc
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize
import scipy.constants as const
import config
from core.base_plotter import BasePlotter

class ParticleEnergyMapPlotter(BasePlotter):
    name = "energy_map"

    def __init__(self):
        self.species_name = getattr(config, 'EMAP_SPECIES_NAME', "Proton")
        self.var_suffix = getattr(config, 'EMAP_VAR_SUFFIX', "subset_Proton_only_Proton")
        
        # 图像分辨率 (网格数量)，越高图像越细腻，但计算稍慢
        self.bins = getattr(config, 'EMAP_BINS', 400)
        # 能量过滤阈值：低于此能量(MeV)的粒子将被忽略，这能带来极其干净的白色背景
        self.min_energy_mev = getattr(config, 'EMAP_MIN_ENERGY_MEV', 0.5)
        
        # 颜色条的能量显示范围 [最小MeV, 最大MeV]
        self.vrange = getattr(config, 'EMAP_VRANGE', [0, 50])

    def plot(self, data, base_name, time_fs):
        try:
            # 1. 获取粒子坐标 (Grid_Particles)
            # 注意：EPOCH 输出的坐标变量名通常为 Grid_Particles_物种名
            pos_var = getattr(data, f"Grid_Particles_{self.var_suffix}")
            x_um = pos_var.data[0] * 1e6
            y_um = pos_var.data[1] * 1e6
            z_um = pos_var.data[2] * 1e6

            # 2. 获取粒子动量与权重
            var_px = getattr(data, f"Particles_Px_{self.var_suffix}")
            var_py = getattr(data, f"Particles_Py_{self.var_suffix}")
            var_pz = getattr(data, f"Particles_Pz_{self.var_suffix}")
            var_w  = getattr(data, f"Particles_Weight_{self.var_suffix}")
            
            px = var_px.data
            py = var_py.data
            pz = var_pz.data
            weight = var_w.data
            
            # 释放 SDF 原始对象引用
            del pos_var, var_px, var_py, var_pz, var_w

            # 3. 计算动能 (MeV)
            mass = const.m_e if "electron" in self.species_name.lower() else const.m_p
            p_square = px**2 + py**2 + pz**2
            gamma = np.sqrt(1.0 + p_square / (mass * const.c)**2)
            ek_mev = (gamma - 1.0) * mass * const.c**2 / (const.e * 1e6)
            
            # 清理动量数组
            del px, py, pz, p_square, gamma
            gc.collect()

            # 4. 过滤低能粒子 (剥离冷背景，让图形轮廓清晰)
            mask = ek_mev >= self.min_energy_mev
            x_um = x_um[mask]
            y_um = y_um[mask]
            z_um = z_um[mask]
            ek_mev = ek_mev[mask]
            weight = weight[mask]
            
            del mask
            gc.collect()

            if len(x_um) == 0:
                print(f"[EnergyMap] {self.species_name} 粒子能量均低于阈值，跳过。")
                return True

            # 确定空间范围 (优先读取 config，否则使用数据边界)
            x_range = getattr(config, 'EMAP_X_LIMITS', [np.min(x_um), np.max(x_um)])
            y_range = getattr(config, 'EMAP_Y_LIMITS', [np.min(y_um), np.max(y_um)])
            z_range = getattr(config, 'EMAP_Z_LIMITS', [np.min(z_um), np.max(z_um)])

            success_count = 0
            output_base = getattr(config, 'OUTPUT_ROOT', '.')
            output_dir = os.path.join(output_base, f"Plots_EnergyMap_{self.species_name}")
            os.makedirs(output_dir, exist_ok=True)

            # ==========================================
            # 绘制 XY 平面
            # ==========================================
            fig_xy = plt.figure(figsize=(8, 6))
            
            # 分母：总权重分布
            H_weight_xy, xedges, yedges = np.histogram2d(
                x_um, y_um, bins=self.bins, range=[x_range, y_range], weights=weight)
            # 分子：总能量*权重分布
            H_energy_xy, _, _ = np.histogram2d(
                x_um, y_um, bins=self.bins, range=[x_range, y_range], weights=weight * ek_mev)
            
            # 计算网格平均能量，避免除以0
            with np.errstate(divide='ignore', invalid='ignore'):
                Avg_Ek_XY = H_energy_xy / H_weight_xy
                # 将没有粒子的网格设为 NaN，这样 pcolormesh 画出来就是透明的(白色背景)
                Avg_Ek_XY[H_weight_xy == 0] = np.nan

            im_xy = plt.pcolormesh(xedges, yedges, Avg_Ek_XY.T, cmap='turbo', 
                                   vmin=self.vrange[0], vmax=self.vrange[1], shading='auto')
            
            cbar = plt.colorbar(im_xy)
            cbar.set_label('Average Kinetic Energy (MeV)', fontsize=12)
            
            plt.title(f"XY Plane | {self.species_name} Energy | t = {time_fs:.0f} fs", fontsize=14)
            plt.xlabel("X ($\mu m$)", fontsize=12)
            plt.ylabel("Y ($\mu m$)", fontsize=12)
            plt.xlim(x_range)
            plt.ylim(y_range)
            plt.tight_layout()
            
            plt.savefig(os.path.join(output_dir, f"EnergyMap_XY_{base_name}.png"), dpi=300)
            plt.close(fig_xy)
            success_count += 1

            # ==========================================
            # 绘制 XZ 平面
            # ==========================================
            fig_xz = plt.figure(figsize=(8, 6))
            
            H_weight_xz, xedges_z, zedges = np.histogram2d(
                x_um, z_um, bins=self.bins, range=[x_range, z_range], weights=weight)
            H_energy_xz, _, _ = np.histogram2d(
                x_um, z_um, bins=self.bins, range=[x_range, z_range], weights=weight * ek_mev)
            
            with np.errstate(divide='ignore', invalid='ignore'):
                Avg_Ek_XZ = H_energy_xz / H_weight_xz
                Avg_Ek_XZ[H_weight_xz == 0] = np.nan

            im_xz = plt.pcolormesh(xedges_z, zedges, Avg_Ek_XZ.T, cmap='turbo', 
                                   vmin=self.vrange[0], vmax=self.vrange[1], shading='auto')
            
            cbar_xz = plt.colorbar(im_xz)
            cbar_xz.set_label('Average Kinetic Energy (MeV)', fontsize=12)
            
            plt.title(f"XZ Plane | {self.species_name} Energy | t = {time_fs:.0f} fs", fontsize=14)
            plt.xlabel("X ($\mu m$)", fontsize=12)
            plt.ylabel("Z ($\mu m$)", fontsize=12)
            plt.xlim(x_range)
            plt.ylim(z_range)
            plt.tight_layout()
            
            plt.savefig(os.path.join(output_dir, f"EnergyMap_XZ_{base_name}.png"), dpi=300)
            plt.close(fig_xz)
            success_count += 1
            
            # 最后大清理
            del x_um, y_um, z_um, ek_mev, weight, Avg_Ek_XY, Avg_Ek_XZ
            gc.collect()

            return success_count > 0

        except AttributeError as e:
            print(f"[EnergyMap] 未找到必要的变量，请检查后缀名。详细错误: {e}")
            return False
        except Exception as e:
            print(f"[EnergyMap] 绘图报错: {e}")
            return False