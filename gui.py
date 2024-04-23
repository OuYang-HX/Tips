import json
import os
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox

from project.common.engine import parse

current_dir = os.path.dirname(os.path.abspath(__file__))
relative_path = os.path.join("..", "..", "..", "res", "paths.json")
paths_json = os.path.abspath(os.path.join(current_dir, relative_path))


def load_paths():
    # 读取资源文件中的路径
    try:
        with open(paths_json, "r", encoding="utf-8") as f:
            paths = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        paths = {"input_folder": "", "output_file": ""}
    return paths


class AnalysisGUI:
    def __init__(self, master):
        self.master = master
        # 主窗口
        master.title("java组件解析")
        width = 800
        height = 300
        x = 400  # 左边距
        y = 300  # 顶边距
        # 设置窗口位置
        master.geometry(f'{width}x{height}+{x}+{y}')

        # 创建两个 Frame，分别用于放置选择输出文件部件和选择输入文件夹部件
        output_frame = tk.Frame(master)
        output_frame.pack(pady=5)

        input_frame = tk.Frame(master)
        input_frame.pack(pady=5)

        # 加载资源文件中的路径，如果文件不存在或内容为空则创建新的空字典
        self.paths = load_paths()

        # 输入文件夹路径
        self.input_folder_label = tk.Label(input_frame, text="选择输入文件夹:")
        self.input_folder_label.pack(side="left", padx=5)

        self.input_folder_entry = tk.Entry(input_frame, width=60)
        self.input_folder_entry.pack(side="left", padx=5)

        self.input_folder_button = tk.Button(input_frame, text="浏览", command=self.select_input_folder)
        self.input_folder_button.pack(side="left", padx=5)

        # 输出文件路径
        self.output_file_label = tk.Label(output_frame, text="选择输出文件:")
        self.output_file_label.pack(side="left", padx=5)

        self.output_file_entry = tk.Entry(output_frame, width=60)
        self.output_file_entry.pack(side="left", padx=5)

        self.output_file_button = tk.Button(output_frame, text="浏览", command=self.select_output_file)
        self.output_file_button.pack(side="left", padx=5)

        # 解析按钮
        self.analyze_button = tk.Button(master, text="解析", command=self.execute)
        # self.analyze_button.place(anchor="nw", x=300, y=100, width=100, height=30)
        self.analyze_button.pack(pady=10)

        # 完成信息显示区域
        self.result_label = tk.Label(master, text="")
        self.result_label.pack(pady=10)

        # 初始化输入文件夹路径和输出文件路径
        self.update_paths()

    def update_paths(self):
        # 更新输入文件夹路径和输出文件路径的文本框显示内容
        self.input_folder_entry.delete(0, tk.END)
        self.input_folder_entry.insert(0, self.paths["input_folder"])
        self.output_file_entry.delete(0, tk.END)
        self.output_file_entry.insert(0, self.paths["output_file"])

    def save_paths(self):
        # 将路径保存到资源文件中
        self.paths["input_folder"] = self.input_folder_entry.get()
        self.paths["output_file"] = self.output_file_entry.get()
        with open(paths_json, "w", encoding="utf-8") as f:
            json.dump(self.paths, f, ensure_ascii=False, indent=4)

    def select_input_folder(self):
        folder_path = filedialog.askdirectory()
        self.input_folder_entry.delete(0, tk.END)
        self.input_folder_entry.insert(0, folder_path)
        self.save_paths()  # 保存路径信息

    def select_output_file(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".txt")
        self.output_file_entry.delete(0, tk.END)
        self.output_file_entry.insert(0, file_path)
        self.save_paths()  # 保存路径信息

    def execute(self):
        directory = self.input_folder_entry.get()
        excel_file = self.output_file_entry.get()

        # 调用其他模块执行分析功能
        try:
            parse.execute(directory, excel_file)
            # messagebox.showinfo("完成", "分析完成")
            self.result_label.config(text="分析完成")
        except Exception as e:
            messagebox.showerror("错误", f"分析出错：{e}")
            self.result_label.config(text="分析出错")


def run():
    root = tk.Tk()
    AnalysisGUI(root)
    root.mainloop()
