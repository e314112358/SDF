#!/bin/bash
#SBATCH -J plot
#SBATCH -N 1
#SBATCH -n 1
#SBATCH -t 02:00:00           # 视频编码较慢，建议多给点时间
#SBATCH --mem=8G              # 内存多给一点，防止大数组崩溃
#SBATCH -o Dete_out.txt
#SBATCH -e Dete_err.txt

module purge  #清空所有模块          

# module load vis

echo "running at $(date)"
python Plot_Detector_Proton.py
echo "Production finished at $(date)."