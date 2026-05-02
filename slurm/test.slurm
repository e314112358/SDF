#!/bin/bash
#SBATCH -J plot               # 任务名称
#SBATCH -N 1                  # 节点数   
#SBATCH -n 1                  # 核心数
#SBATCH -t 24:00:00           # 运行时间
#SBATCH --mem=32G             # 运行内存
#SBATCH -o out_%j.txt
#SBATCH -e err_%j.txt

module purge

# 可选：指定实验配置（取消注释并修改）
# CONFIG="--config tnsa_2024"

echo "running at $(date)"
cd ../..
python SDF_3D/main.py -t phase_space energy_map rcf_detector -f "0010.sdf" $CONFIG
echo "Production finished at $(date)."
