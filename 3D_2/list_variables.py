import sdf_helper as sh
import glob
import sys
import contextlib

def main():
    # 找到当前文件夹下最后一个 SDF 文件
    sdf_files = sorted(glob.glob("*.sdf"))
    if not sdf_files:
        print("❌ 当前目录下没有找到任何 .sdf 文件！")
        sys.exit()

    last_file = sdf_files[-1]
    print(f"🔍 正在使用官方函数解析: {last_file} ...")

    # 读取数据
    data = sh.getdata(last_file, verbose=False)

    # 🌟 定义你要保存的 txt 文件名
    output_txt = "SDF_Variables_List.txt"

    # 使用黑魔法：拦截屏幕输出，存入 txt 文件
    with open(output_txt, 'w', encoding='utf-8') as f:
        with contextlib.redirect_stdout(f):
            sh.list_variables(data)

    print(f"✅ 大功告成！所有的变量名已全部保存到当前目录的 👉 {output_txt}")

if __name__ == "__main__":
    main()