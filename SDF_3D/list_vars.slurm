#!/bin/bash
#SBATCH -J plot               # 任务名称
#SBATCH -N 1                  # 节点数   
#SBATCH -n 10                  # 核心数
#SBATCH -t 24:00:00           # 运行时间
#SBATCH --mem=16G             # 运行内存
#SBATCH -o out_1.txt
#SBATCH -e err_1.txt

module purge  #清空所有模块          

# module load vis

echo "running at $(date)"
cd ..
python SDF_3D/main.py -t list_vars -f "*.sdf"
echo "Production finished at $(date)."