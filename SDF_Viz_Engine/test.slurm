#!/bin/bash
#SBATCH -J plot
#SBATCH -N 1
#SBATCH -n 1
#SBATCH -t 24:00:00           # 视频编码较慢，建议多给点时间
#SBATCH --mem=16G              # 内存多给一点，防止大数组崩溃
#SBATCH -o _out.txt
#SBATCH -e _err.txt

module purge  #清空所有模块          

# module load vis

echo "running"
cd ..
python SDF_Viz_Engine/main.py -t fields density_xy density_xz density_yz list_vars -f "*.sdf"
echo "Production finished."