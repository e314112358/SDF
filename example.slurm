#!/bin/bash
#SBATCH -J plot
#SBATCH -N 1
#SBATCH -n 1
#SBATCH -t 24:00:00           
#SBATCH --mem=16G             
#SBATCH -o _out.txt
#SBATCH -e _err.txt

module purge  #清空所有模块          

# module load vis

echo "running at $(date)"
python EM_field.py
echo "Production finished at $(date)."