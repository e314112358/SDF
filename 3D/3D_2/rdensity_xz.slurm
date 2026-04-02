#!/bin/bash
#SBATCH -J plot           
#SBATCH -N 1                  
#SBATCH -n 1                 
#SBATCH -c 1                  
#SBATCH -t 24:00:00           
#SBATCH --mem=16G             
#SBATCH -o density_xz_out.txt
#SBATCH -e density_xz_err.txt

module purge  # 清空所有模块          

echo " Starting at $(date)"

python density_xz.py

echo "Finished at $(date)."