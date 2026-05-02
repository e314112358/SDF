#!/bin/bash
#SBATCH -J plot
#SBATCH -N 1
#SBATCH -n 1
#SBATCH -t 24:00:00            # 运行时间
#SBATCH --mem=32G              # 运行内存
#SBATCH -o _out.txt
#SBATCH -e _err.txt

module purge  #清空所有模块          

# module load vis

echo "running at $(date)"
cd ..
python SDF_3D/main.py -t rcf_detector -f "00[2-3]?.sdf"
echo "Production finished at $(date)."