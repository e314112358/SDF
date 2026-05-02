#!/bin/bash
#SBATCH -J plot               # 任务名称
#SBATCH -N 1                  # 节点数   
#SBATCH -n 1                  # 核心数
#SBATCH -t 24:00:00           # 运行时间
#SBATCH --mem=64G             # 运行内存
#SBATCH -o out_%j.txt
#SBATCH -e err_%j.txt

module purge

# 可选：指定实验配置（取消注释并修改）
# CONFIG="--config tnsa_2024"

echo "running at $(date)"
cd ../..
python SDF_3D/main.py -t fields density_xy density_xz density_yz list_vars spectrum phase_space energy_map rcf_detector -f "*.sdf" $CONFIG
echo "Production finished at $(date)."
