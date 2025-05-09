# importmysql
SQL 文件导入工具
介绍
本工具是一个用于将 SQL 文件批量导入 MySQL 数据库的桌面应用程序，提供了图形化界面和多种导入模式，帮助用户高效地管理 SQL 文件的导入工作。
功能特点
批量导入 SQL 文件
两种导入模式：
每个 SQL 文件创建独立数据库（使用文件名作为数据库名）
批量导入到指定数据库（多个文件合并到同一数据库）
支持从目录或选择文件导入
实时日志记录和显示
进度条可视化导入进度
日志文件生成和导出功能
安装步骤
安装 Python
确保已安装 Python 3.6 或更高版本
推荐使用 Python 官方下载页面
安装依赖库
bash
复制
pip install pymysql
pip install tkinter
下载本项目
从项目仓库克隆代码或下载 ZIP 文件
配置 MySQL 信息
在代码中修改以下数据库连接配置：
Python
复制
self.host = "localhost"
self.user = "root"
self.password = "123456"
self.port = 3306
self.mysql_path = r"C:\Program Files\MySQL\MySQL Server 8.0\bin\mysql.exe"
使用方法
启动应用程序
bash
复制
python importTest.py
选择 SQL 文件
点击“选择目录”按钮加载整个目录中的 SQL 文件
或点击“选择文件”按钮选择单个或多个 SQL 文件
选择导入模式
每个文件创建独立数据库：每个 SQL 文件会被导入到以文件名命名的独立数据库中
导入到指定数据库：所有 SQL 文件会被导入到您指定的数据库中
设置目标数据库（仅在“导入到指定数据库”模式下需要）
在“目标数据库”输入框中输入目标数据库名称
开始导入
点击“开始导入”按钮开始导入过程
导入进度会在进度条中显示
导入结果会在日志区域实时显示
查看日志
导入过程中的所有操作都会记录在日志区域
可以点击“清空日志”按钮清除日志
可以选择在导入完成后生成日志文件
界面说明
以下是工具的主要界面元素：
文件选择区域： 显示已选择的 SQL 文件列表
导入模式选择： 提供两种导入模式的单选按钮
目标数据库输入框： 在“导入到指定数据库”模式下输入目标数据库名称
日志区域： 显示导入过程中的详细日志信息
进度条： 显示当前导入进度
控制按钮： 包括“开始导入”和“清空日志”按钮
代码结构
SQLImporterApp 类：主应用程序类，包含所有功能实现
log_message 方法：记录日志到界面和文件
select_directory 和 select_files 方法：处理文件选择逻辑
validate_connection 方法：验证数据库连接
create_database 方法：创建新数据库
import_sql_file 方法：执行单个 SQL 文件导入
start_import 方法：导入主逻辑入口
process_import 方法：在新线程中处理导入过程
