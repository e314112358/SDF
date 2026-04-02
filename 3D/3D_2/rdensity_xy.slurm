#!/bin/bash
#SBATCH -J plot            
#SBATCH -N 1                  
#SBATCH -n 1                  
#SBATCH -c 1                
#SBATCH -t 24:00:00           
#SBATCH --mem=16G             # 申请 32G 内存 (：如果运行时因内存不足被杀，请加到 64G)
#SBATCH -o density_xy_out.txt
#SBATCH -e density_xy_err.txt

module purge  # 清空所有模块          

# ==========================================
# 【关键修改 2】：超算多进程“保命”环境变量
# 封印 Numpy 底层的隐式多线程，防止 8进程 × 8线程 = 64线程的互相踩踏！
# ==========================================


echo "🚀 Starting 8-core parallel plotting at $(date)"

# 运行你的 8 核并行 Python 脚本
python density_xy.py

echo "🎉 Production finished at $(date)."