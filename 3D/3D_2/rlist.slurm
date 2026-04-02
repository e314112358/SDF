#!/bin/bash
#SBATCH -J plot
#SBATCH -N 1
#SBATCH -n 1
#SBATCH -t 24:00:00           
#SBATCH --mem=4G              
#SBATCH -o list_out.txt
#SBATCH -e list_err.txt

module purge  #清空所有模块          

# module load vis

echo "running"
python list_variables.py
echo "Production finished."