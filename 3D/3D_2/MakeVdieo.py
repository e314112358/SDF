import cv2
import os
import re
import numpy as np

def extract_last_four_digits(filename):
    """
    专门匹配文件名结尾前四位数字用于排序
    例如匹配 xxx0001.png 中的 0001
    """
    # \d{4} 表示恰好 4 个数字，\.\w+$ 表示紧跟着文件后缀名如 .png
    match = re.search(r'(\d{4})\.\w+$', filename)
    return int(match.group(1)) if match else 0

def images_to_video(folder_path, output_name, fps=10):
    # 1. 提取并过滤图片文件
    images = [img for img in os.listdir(folder_path) if img.endswith((".png", ".jpg"))]
    
    # 2. 按后四位数字自然排序
    images.sort(key=extract_last_four_digits)

    if not images:
        print(f"跳过: 文件夹 '{os.path.basename(folder_path)}' 中无图片")
        return

    # 3. 读取第一张图获取分辨率 (使用 np.fromfile 防止 Windows 路径报错)
    first_image_path = os.path.join(folder_path, images[0])
    frame = cv2.imdecode(np.fromfile(first_image_path, dtype=np.uint8), cv2.IMREAD_COLOR)
    
    if frame is None:
        print(f"错误: 无法读取图片 {first_image_path}")
        return
        
    height, width, layers = frame.shape

    # 4. 初始化 MP4 视频写入器
    fourcc = cv2.VideoWriter_fourcc(*'mp4v') 
    video = cv2.VideoWriter(output_name, fourcc, fps, (width, height))

    print(f"正在合成: {os.path.basename(folder_path)} -> {os.path.basename(output_name)} (共 {len(images)} 帧)")

    # 5. 逐帧合成视频
    for image in images:
        img_path = os.path.join(folder_path, image)
        frame = cv2.imdecode(np.fromfile(img_path, dtype=np.uint8), cv2.IMREAD_COLOR)
        video.write(frame)

    video.release()
    print("完成。")

if __name__ == "__main__":
    # 获取当前 py 文件所在的绝对路径
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 【配置区】在这里填入你想要处理的、与 py 文件并列的文件夹名称
    # 你可以随时增加或删除列表里的名字
    target_folders = [
        "Plots_Bz",
        "Plots_Ex" 
    ]
    
    # 设置视频帧率
    fps_setting = 5 
    
    # 开始遍历你指定的文件夹列表
    for folder_name in target_folders:
        folder_path = os.path.join(base_dir, folder_name)
        
        # 检查该文件夹是否真的存在
        if os.path.isdir(folder_path):
            # 视频将输出在 py 文件所在目录，命名为 "文件夹名.mp4"
            output_video_path = os.path.join(base_dir, f"{folder_name}.mp4")
            images_to_video(folder_path, output_video_path, fps=fps_setting)
        else:
            print(f"警告: 找不到并列的文件夹 '{folder_name}'，已跳过。")