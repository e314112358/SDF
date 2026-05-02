import numpy as np
import scipy.constants as const


def compute_kinetic_energy_mev(px, py, pz, mass):
    """计算动能 (MeV)
    
    Args:
        px, py, pz: 动量数组 (kg·m/s)
        mass: 粒子质量 (kg)
    
    Returns:
        动能数组 (MeV)
    """
    p_square = px**2 + py**2 + pz**2
    gamma = np.sqrt(1.0 + p_square / (mass * const.c)**2)
    return (gamma - 1.0) * mass * const.c**2 / (const.e * 1e6)


def get_particle_mass(species_name: str):
    """根据粒子名称返回质量"""
    if "electron" in species_name.lower():
        return const.m_e
    return const.m_p
