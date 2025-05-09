import os
import subprocess
import pymysql
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import logging
from datetime import datetime
import threading

# 配置日志
logging.basicConfig(
    filename="import_sql.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)


class SQLImporterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("SQL 文件导入工具")
        self.root.geometry("1000x800")
        self.root.configure(bg="#f0f0f0")

        # 数据库连接配置
        self.host = "localhost"
        self.user = "root"
        self.password = "123456"
        self.port = 3306
        self.mysql_path = r"C:\Program Files\MySQL\MySQL Server 8.0\bin\mysql.exe"

        # 初始化变量
        self.selected_files = []
        self.import_mode = tk.StringVar(value="database_per_file")  # 导入模式

        # 创建主框架
        self.main_frame = tk.Frame(root, bg="#f0f0f0")
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # 创建标题
        self.title_label = tk.Label(
            self.main_frame,
            text="SQL 文件导入工具",
            font=("Arial", 18, "bold"),
            bg="#f0f0f0"
        )
        self.title_label.pack(pady=10)

        # 文件选择区域
        self.file_frame = tk.LabelFrame(
            self.main_frame,
            text="选择 SQL 文件",
            font=("Arial", 12),
            bg="#f0f0f0"
        )
        self.file_frame.pack(fill=tk.X, pady=10)

        self.file_listbox = tk.Listbox(
            self.file_frame,
            selectmode=tk.EXTENDED,
            height=6,
            font=("Arial", 10),
            bg="white"
        )
        self.file_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)

        scrollbar = tk.Scrollbar(self.file_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.file_listbox.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.file_listbox.yview)

        self.button_frame = tk.Frame(self.file_frame, bg="#f0f0f0")
        self.button_frame.pack(side=tk.RIGHT, padx=5)

        self.select_dir_btn = tk.Button(
            self.button_frame,
            text="选择目录",
            width=12,
            command=self.select_directory,
            bg="#4CAF50",
            fg="white"
        )
        self.select_dir_btn.pack(pady=5)

        self.select_files_btn = tk.Button(
            self.button_frame,
            text="选择文件",
            width=12,
            command=self.select_files,
            bg="#2196F3",
            fg="white"
        )
        self.select_files_btn.pack(pady=5)

        # 导入模式选择
        self.mode_frame = tk.LabelFrame(
            self.main_frame,
            text="导入模式",
            font=("Arial", 12),
            bg="#f0f0f0"
        )
        self.mode_frame.pack(fill=tk.X, pady=10)

        tk.Radiobutton(
            self.mode_frame,
            text="每个文件创建独立数据库（使用文件名作为数据库名）",
            variable=self.import_mode,
            value="database_per_file",
            bg="#f0f0f0",
            font=("Arial", 10)
        ).pack(anchor=tk.W)

        tk.Radiobutton(
            self.mode_frame,
            text="导入到指定数据库（多个文件合并到同一数据库）",
            variable=self.import_mode,
            value="single_database",
            bg="#f0f0f0",
            font=("Arial", 10)
        ).pack(anchor=tk.W)

        # 目标数据库输入
        self.target_db_frame = tk.Frame(self.main_frame, bg="#f0f0f0")
        self.target_db_frame.pack(fill=tk.X, pady=5)

        self.db_label = tk.Label(
            self.target_db_frame,
            text="目标数据库：",
            font=("Arial", 10),
            bg="#f0f0f0"
        )
        self.db_label.pack(side=tk.LEFT, padx=5)

        self.db_entry = tk.Entry(
            self.target_db_frame,
            font=("Arial", 10),
            width=30
        )
        self.db_entry.pack(side=tk.LEFT, padx=5)

        # 日志区域
        self.log_frame = tk.LabelFrame(
            self.main_frame,
            text="导入日志",
            font=("Arial", 12),
            bg="#f0f0f0"
        )
        self.log_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        self.log_text = scrolledtext.ScrolledText(
            self.log_frame,
            font=("Arial", 9),
            wrap=tk.WORD,
            bg="white",
            height=15
        )
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # 进度条
        self.progress = ttk.Progressbar(
            self.main_frame,
            orient=tk.HORIZONTAL,
            mode='determinate'
        )
        self.progress.pack(fill=tk.X, pady=5)

        # 控制按钮
        self.control_frame = tk.Frame(self.main_frame, bg="#f0f0f0")
        self.control_frame.pack(pady=10)

        self.import_btn = tk.Button(
            self.control_frame,
            text="开始导入",
            font=("Arial", 12),
            bg="#FF5722",
            fg="white",
            command=self.start_import,
            width=15
        )
        self.import_btn.pack(side=tk.LEFT, padx=10)

        self.clear_log_btn = tk.Button(
            self.control_frame,
            text="清空日志",
            font=("Arial", 12),
            command=self.clear_log,
            width=15
        )
        self.clear_log_btn.pack(side=tk.LEFT, padx=10)

        # 状态栏
        self.status_var = tk.StringVar()
        self.status_var.set("就绪")
        self.status_bar = tk.Label(
            root,
            textvariable=self.status_var,
            font=("Arial", 9),
            bd=1,
            relief=tk.SUNKEN,
            anchor=tk.W
        )
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def log_message(self, message, level="INFO"):
        """记录日志并显示在日志区域"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] [{level}] {message}\n"
        self.log_text.insert(tk.END, log_entry)
        self.log_text.see(tk.END)
        if level == "INFO":
            logging.info(message)
        elif level == "ERROR":
            logging.error(message)

    def select_directory(self):
        """选择目录并加载SQL文件"""
        directory = filedialog.askdirectory()
        if directory:
            self.file_listbox.delete(0, tk.END)
            files = [f for f in os.listdir(directory) if f.endswith('.sql')]
            for f in sorted(files):
                self.file_listbox.insert(tk.END, os.path.join(directory, f))
            self.log_message(f"已加载目录：{directory}")

    def select_files(self):
        """选择多个SQL文件"""
        files = filedialog.askopenfilenames(filetypes=[("SQL files", "*.sql")])
        if files:
            self.file_listbox.delete(0, tk.END)
            for f in files:
                self.file_listbox.insert(tk.END, f)
            self.log_message(f"已选择 {len(files)} 个文件")

    def clear_log(self):
        """清空日志"""
        self.log_text.delete(1.0, tk.END)

    def validate_connection(self):
        """验证数据库连接"""
        try:
            conn = pymysql.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                port=self.port
            )
            conn.close()
            return True
        except MySQLError as e:
            self.log_message(f"数据库连接失败：{e}", "ERROR")
            return False

    def create_database(self, db_name):
        """创建新数据库"""
        try:
            conn = pymysql.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                port=self.port
            )
            cursor = conn.cursor()
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{db_name}`")
            conn.commit()
            self.log_message(f"数据库 {db_name} 创建成功")
            return True
        except MySQLError as e:
            self.log_message(f"创建数据库失败：{e}", "ERROR")
            return False
        finally:
            if 'conn' in locals():
                conn.close()

    def import_sql_file(self, file_path, target_db):
        """导入单个SQL文件"""
        try:
            cmd = [
                self.mysql_path,
                "-h", self.host,
                "-u", self.user,
                f"-p{self.password}",
                "--default-character-set=utf8mb4",
                target_db
            ]
            with open(file_path, 'r', encoding='utf-8') as f:
                result = subprocess.run(
                    cmd,
                    stdin=f,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    check=True
                )
            return True
        except subprocess.CalledProcessError as e:
            self.log_message(f"导入失败：{e.stderr}", "ERROR")
            return False
        except Exception as e:
            self.log_message(f"发生未知错误：{str(e)}", "ERROR")
            return False

    def start_import(self):
        """开始导入主逻辑"""
        if not self.validate_connection():
            messagebox.showerror("错误", "数据库连接验证失败")
            return

        selected_files = self.file_listbox.get(0, tk.END)
        if not selected_files:
            messagebox.showwarning("警告", "请先选择要导入的SQL文件")
            return

        if self.import_mode.get() == "single_database":
            target_db = self.db_entry.get().strip()
            if not target_db:
                messagebox.showwarning("警告", "请指定目标数据库名称")
                return
            if not self.create_database(target_db):
                return

        # 设置进度条
        total_files = len(selected_files)
        self.progress["maximum"] = total_files
        self.progress["value"] = 0

        # 在新线程中执行导入
        threading.Thread(
            target=self.process_import,
            args=(selected_files,),
            daemon=True
        ).start()

    def process_import(self, files):
        """处理导入过程"""
        self.import_btn.config(state=tk.DISABLED)
        success_count = 0
        failed_count = 0

        for idx, file_path in enumerate(files):
            self.status_var.set(f"正在处理文件 {idx + 1}/{len(files)}")
            self.progress["value"] = idx + 1
            self.root.update_idletasks()

            try:
                if self.import_mode.get() == "database_per_file":
                    db_name = os.path.splitext(os.path.basename(file_path))[0]
                    if not self.create_database(db_name):
                        failed_count += 1
                        continue
                    target_db = db_name
                else:
                    target_db = self.db_entry.get().strip()

                if self.import_sql_file(file_path, target_db):
                    self.log_message(f"成功导入：{file_path} -> {target_db}")
                    success_count += 1
                else:
                    failed_count += 1

            except Exception as e:
                self.log_message(f"处理文件 {file_path} 时发生错误：{str(e)}", "ERROR")
                failed_count += 1

        # 完成处理
        self.status_var.set(f"导入完成：成功 {success_count} 个，失败 {failed_count} 个")
        messagebox.showinfo(
            "完成",
            f"导入完成！\n成功：{success_count} 个\n失败：{failed_count} 个"
        )
        self.import_btn.config(state=tk.NORMAL)
        self.progress["value"] = 0

        # 弹出提示框让用户选择是否生成日志
        response = messagebox.askyesno(
            "日志",
            "导入完成，是否生成日志文件？"
        )
        if response:
            self.generate_log_file()

    def generate_log_file(self):
        """生成日志文件"""
        log_filename = "import_sql.log"
        with open(log_filename, "w") as log_file:
            log_file.write(self.log_text.get(1.0, tk.END))
        messagebox.showinfo("日志", f"日志文件已生成：{log_filename}")


if __name__ == "__main__":
    root = tk.Tk()
    app = SQLImporterApp(root)
    root.mainloop()
