#!/bin/bash
#SBATCH -J plot            
#SBATCH -N 1                  
#SBATCH -n 1                  
#SBATCH -c 1                
#SBATCH -t 24:00:00           
#SBATCH --mem=16G             
#SBATCH -o EM_out.txt
#SBATCH -e EM_err.txt

module purge  # 清空所有模块          

echo " Starting  at $(date)"

python EM_field.py

echo " finished at $(date)."