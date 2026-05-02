#!/bin/bash
#SBATCH -J plot
#SBATCH -N 1
#SBATCH -n 1
#SBATCH -t 24:00:00            # 运行时间
#SBATCH --mem=64G              # 运行内存
#SBATCH -o out_%j.txt
#SBATCH -e err_%j.txt

module purge

# 可选：指定实验配置
# CONFIG="--config tnsa_2024"

echo "running at $(date)"
cd ../..
python SDF_3D/main.py -t rcf_detector -f "*.sdf" $CONFIG
echo "Production finished at $(date)."
