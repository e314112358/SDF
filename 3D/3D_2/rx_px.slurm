#!/bin/bash
#SBATCH -J plot
#SBATCH -N 1
#SBATCH -n 1
#SBATCH -t 24:00:00           
#SBATCH --mem=16G             
#SBATCH -o x_px_out.txt
#SBATCH -e x_px_err.txt

module purge  #清空所有模块          

# module load vis

echo "running at $(date)"
python x_px.py
echo "Finished at $(date)."