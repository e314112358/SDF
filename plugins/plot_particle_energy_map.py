import gc
import numpy as np
import matplotlib.pyplot as plt
import scipy.constants as const

from core import BasePlotter, compute_kinetic_energy_mev, get_particle_mass


class ParticleEnergyMapPlotter(BasePlotter):
    name = "energy_map"

    def plot(self, data, base_name, time_fs):
        try:
            emap = self.config.energy_map
            species_name = emap.species_name
            var_suffix = emap.var_suffix
            
            # 获取粒子坐标
            pos_var = self.safe_getattr(data, f"Grid_Particles_{var_suffix}")
            if pos_var is None:
                return False
            
            x_um = pos_var.data[0] * 1e6
            y_um = pos_var.data[1] * 1e6
            z_um = pos_var.data[2] * 1e6
            del pos_var
            
            # 获取粒子动量与权重
            var_px = self.safe_getattr(data, f"Particles_Px_{var_suffix}")
            var_py = self.safe_getattr(data, f"Particles_Py_{var_suffix}")
            var_pz = self.safe_getattr(data, f"Particles_Pz_{var_suffix}")
            var_w = self.safe_getattr(data, f"Particles_Weight_{var_suffix}")
            
            if any(v is None for v in [var_px, var_py, var_pz, var_w]):
                return False
            
            px = var_px.data
            py = var_py.data
            pz = var_pz.data
            weight = var_w.data
            del var_px, var_py, var_pz, var_w
            
            # 计算动能
            mass = get_particle_mass(species_name)
            ek_mev = compute_kinetic_energy_mev(px, py, pz, mass)
            del px, py, pz
            gc.collect()
            
            # 过滤低能粒子
            mask = ek_mev >= emap.min_energy_MeV
            x_um = x_um[mask]
            y_um = y_um[mask]
            z_um = z_um[mask]
            ek_mev = ek_mev[mask]
            weight = weight[mask]
            del mask
            gc.collect()
            
            if len(x_um) == 0:
                print(f"[EnergyMap] {species_name} 粒子能量均低于阈值，跳过。")
                return True
            
            # 空间范围
            x_range = list(emap.x_limits)
            y_range = list(emap.y_limits)
            z_range = list(emap.z_limits)
            
            success_count = 0
            
            # 绘制 XY 平面
            fig_xy = plt.figure(figsize=self.config.output.figsize)
            
            H_weight_xy, xedges, yedges = np.histogram2d(
                x_um, y_um, bins=emap.bins, range=[x_range, y_range], weights=weight)
            H_energy_xy, _, _ = np.histogram2d(
                x_um, y_um, bins=emap.bins, range=[x_range, y_range], weights=weight * ek_mev)
            
            with np.errstate(divide='ignore', invalid='ignore'):
                Avg_Ek_XY = H_energy_xy / H_weight_xy
                Avg_Ek_XY[H_weight_xy == 0] = np.nan
            
            im_xy = plt.pcolormesh(xedges, yedges, Avg_Ek_XY.T, cmap='turbo',
                                   vmin=emap.vrange[0], vmax=emap.vrange[1], shading='auto')
            
            cbar = plt.colorbar(im_xy)
            cbar.set_label('Average Kinetic Energy (MeV)', fontsize=12)
            plt.title(f"XY Plane | {species_name} Energy | t = {time_fs:.0f} fs", fontsize=14)
            plt.xlabel("X (um)", fontsize=12)
            plt.ylabel("Y (um)", fontsize=12)
            plt.xlim(x_range)
            plt.ylim(y_range)
            
            subdir = f"Plots_EnergyMap_{species_name}"
            filename_xy = f"EnergyMap_XY_{base_name}.png"
            self.save_figure(fig_xy, subdir, filename_xy)
            success_count += 1
            
            # 绘制 XZ 平面
            fig_xz = plt.figure(figsize=self.config.output.figsize)
            
            H_weight_xz, xedges_z, zedges = np.histogram2d(
                x_um, z_um, bins=emap.bins, range=[x_range, z_range], weights=weight)
            H_energy_xz, _, _ = np.histogram2d(
                x_um, z_um, bins=emap.bins, range=[x_range, z_range], weights=weight * ek_mev)
            
            with np.errstate(divide='ignore', invalid='ignore'):
                Avg_Ek_XZ = H_energy_xz / H_weight_xz
                Avg_Ek_XZ[H_weight_xz == 0] = np.nan
            
            im_xz = plt.pcolormesh(xedges_z, zedges, Avg_Ek_XZ.T, cmap='turbo',
                                   vmin=emap.vrange[0], vmax=emap.vrange[1], shading='auto')
            
            cbar_xz = plt.colorbar(im_xz)
            cbar_xz.set_label('Average Kinetic Energy (MeV)', fontsize=12)
            plt.title(f"XZ Plane | {species_name} Energy | t = {time_fs:.0f} fs", fontsize=14)
            plt.xlabel("X (um)", fontsize=12)
            plt.ylabel("Z (um)", fontsize=12)
            plt.xlim(x_range)
            plt.ylim(z_range)
            
            filename_xz = f"EnergyMap_XZ_{base_name}.png"
            self.save_figure(fig_xz, subdir, filename_xz)
            success_count += 1
            
            del x_um, y_um, z_um, ek_mev, weight
            gc.collect()
            
            return success_count > 0
            
        except Exception as e:
            print(f"[EnergyMap] 绘图报错: {e}")
            return False
