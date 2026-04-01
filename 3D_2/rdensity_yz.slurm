#!/bin/bash
#SBATCH -J plot            # 任务名改得更有辨识度一点
#SBATCH -N 1                  # 保持 1 个节点 (Node)
#SBATCH -n 1                  # 保持 1 个任务 (Task)
#SBATCH -c 24                  # 【关键修改 1】：为该任务申请 8 个 CPU 核心！
#SBATCH -t 06:00:00           # 运行时间 6 小时
#SBATCH --mem=32G             # 申请 32G 内存 (注意：如果运行时因内存不足被杀，请加到 64G)
#SBATCH -o density_out.txt
#SBATCH -e density_err.txt

module purge  # 清空所有模块          
# module load vis  # 【提示】确保这里或者下面加载了你的 Python/Conda 环境

# ==========================================
# 【关键修改 2】：超算多进程“保命”环境变量
# 封印 Numpy 底层的隐式多线程，防止 8进程 × 8线程 = 64线程的互相踩踏！
# ==========================================
export OMP_NUM_THREADS=1
export MKL_NUM_THREADS=1
export OPENBLAS_NUM_THREADS=1
export NUMEXPR_NUM_THREADS=1

echo "🚀 Starting 24-core parallel plotting at $(date)"

# 运行你的 8 核并行 Python 脚本
python density_yz.py

echo "🎉 Production finished at $(date)."