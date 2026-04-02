#!/bin/bash
#SBATCH -J plot            
#SBATCH -N 1                 
#SBATCH -n 1                 
#SBATCH -c 1                
#SBATCH -t 24:00:00          
#SBATCH --mem=16G             
#SBATCH -o density_yz_out.txt
#SBATCH -e density_yz_err.txt

module purge  # 清空所有模块          


echo "Starting at $(date)"

python density_yz.py

echo "Finished at $(date)."