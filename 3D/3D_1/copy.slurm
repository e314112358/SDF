#!/bin/bash
#SBATCH -J copy_sdf        # 任务名称
#SBATCH -N 1               # 节点数
#SBATCH -n 1               # 任务数
#SBATCH -c 1               # 核心数 
#SBATCH -t 04:00:00        # 申请 4 小时 
#SBATCH --mem=8G           # 申请 8G 内存
#SBATCH -o copy_out.txt    # 正常输出日志
#SBATCH -e copy_err.txt    # 报错日志

module purge  # 清空模块，防止环境冲突

# === 请在这里修改你要复制的文件名 ===
SOURCE_FILE="CH_50/0010.sdf"   # 例如: 1/0010.sdf
DEST_DIR="sdf_test/"              # 目标文件夹
# ====================================

echo "========================================"
echo "开始时间: $(date)"
echo "正在搬运文件: ${SOURCE_FILE} -> ${DEST_DIR}"
echo "========================================"

# 使用 rsync 替代 cp，-a 归档，-v 显示详情，-P 支持断点续传
rsync -avP "${SOURCE_FILE}" "${DEST_DIR}"

echo "========================================"
echo "结束时间: $(date)"
echo "搬运任务已完成！"
echo "========================================"