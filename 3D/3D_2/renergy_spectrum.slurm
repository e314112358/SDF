#!/bin/bash
#SBATCH -J plot
#SBATCH -N 1
#SBATCH -n 1
#SBATCH -t 24:00:00           
#SBATCH --mem=16G           
#SBATCH -o spe_out.txt
#SBATCH -e spe_err.txt

module purge  #清空所有模块          

# module load vis

echo " Starting  at $(date)"
python Plot_Spectrum_RawParticles.py
echo " Finished at $(date)."