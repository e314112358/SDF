#!/bin/bash
#SBATCH -J plot
#SBATCH -N 1
#SBATCH -n 1
#SBATCH -t 24:00:00           # 视频编码较慢，建议多给点时间
#SBATCH --mem=16G              # 内存多给一点，防止大数组崩溃
#SBATCH -o density_out.txt
#SBATCH -e density_err.txt

module purge  #清空所有模块          

# module load vis

echo "running"
python density_xz.py
echo "Production finished."