#!/bin/bash
#SBATCH -J plot
#SBATCH -N 1
#SBATCH -n 1
#SBATCH -t 24:00:00           
#SBATCH --mem=16G              
#SBATCH -o Dete_out.txt
#SBATCH -e Dete_err.txt

module purge  #清空所有模块          


echo "running at $(date)"
python Plot_Detector_Proton.py
echo "Finished at $(date)."