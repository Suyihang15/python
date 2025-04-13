import requests
from bs4 import BeautifulSoup
import os
import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext
import threading
from urllib.parse import urljoin
import re
import json
import webbrowser

class WebCrawlerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("网页文件下载器")
        self.root.geometry("800x700")  # 增加高度以容纳新的选项
        self.root.resizable(True, True)
        
        # 设置主题颜色
        self.bg_color = "#f0f0f0"
        self.accent_color = "#4a6baf"
        self.text_color = "#333333"
        self.root.configure(bg=self.bg_color)
        
        # 默认请求头
        self.default_headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Connection": "keep-alive"
        }
        
        self.create_widgets()
        
    def create_widgets(self):
        # 创建主框架
        main_frame = tk.Frame(self.root, bg=self.bg_color)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # 标题
        title_label = tk.Label(
            main_frame, 
            text="网页文件爬取下载工具", 
            font=("微软雅黑", 18, "bold"),
            fg=self.accent_color,
            bg=self.bg_color
        )
        title_label.pack(pady=(0, 20))
        
        # 创建选项卡控件
        tab_control = ttk.Notebook(main_frame)
        
        # 基本设置选项卡
        basic_tab = tk.Frame(tab_control, bg=self.bg_color)
        tab_control.add(basic_tab, text="基本设置")
        
        # 高级设置选项卡
        advanced_tab = tk.Frame(tab_control, bg=self.bg_color)
        tab_control.add(advanced_tab, text="高级设置")
        
        tab_control.pack(fill=tk.BOTH, expand=True)
        
        # ===== 基本设置选项卡内容 =====
        # 输入区域框架
        input_frame = tk.LabelFrame(
            basic_tab, 
            text="配置选项", 
            font=("微软雅黑", 12),
            fg=self.text_color,
            bg=self.bg_color
        )
        input_frame.pack(fill=tk.X, pady=(10, 15))
        
        # URL输入
        url_frame = tk.Frame(input_frame, bg=self.bg_color)
        url_frame.pack(fill=tk.X, padx=10, pady=10)
        
        url_label = tk.Label(
            url_frame, 
            text="网页地址:", 
            width=10, 
            font=("微软雅黑", 10),
            bg=self.bg_color,
            fg=self.text_color
        )
        url_label.pack(side=tk.LEFT, padx=(0, 5))
        
        self.url_entry = tk.Entry(url_frame, font=("微软雅黑", 10))
        self.url_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # 添加预览按钮
        preview_button = tk.Button(
            url_frame, 
            text="预览网页",
            command=self.preview_webpage,
            bg="#2ecc71",
            fg="white",
            font=("微软雅黑", 9),
            relief=tk.FLAT,
            padx=10
        )
        preview_button.pack(side=tk.LEFT, padx=(5, 0))
        
        # 文件类型输入
        file_type_frame = tk.Frame(input_frame, bg=self.bg_color)
        file_type_frame.pack(fill=tk.X, padx=10, pady=10)
        
        file_type_label = tk.Label(
            file_type_frame, 
            text="文件类型:", 
            width=10, 
            font=("微软雅黑", 10),
            bg=self.bg_color,
            fg=self.text_color
        )
        file_type_label.pack(side=tk.LEFT, padx=(0, 5))
        
        self.file_type_entry = tk.Entry(file_type_frame, font=("微软雅黑", 10))
        self.file_type_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.file_type_entry.insert(0, ".pdf,.jpg,.png")
        
        # 提示标签
        hint_label = tk.Label(
            input_frame, 
            text="提示: 文件类型请使用逗号分隔，如 .pdf,.jpg,.png，留空则下载所有类型",
            font=("微软雅黑", 9),
            fg="#666666",
            bg=self.bg_color
        )
        hint_label.pack(padx=10, pady=(0, 10), anchor="w")
        
        # 保存路径选择
        save_path_frame = tk.Frame(input_frame, bg=self.bg_color)
        save_path_frame.pack(fill=tk.X, padx=10, pady=10)
        
        save_path_label = tk.Label(
            save_path_frame, 
            text="保存位置:", 
            width=10, 
            font=("微软雅黑", 10),
            bg=self.bg_color,
            fg=self.text_color
        )
        save_path_label.pack(side=tk.LEFT, padx=(0, 5))
        
        self.save_path_var = tk.StringVar()
        self.save_path_var.set(os.path.join(os.getcwd(), "downloads"))
        
        self.save_path_entry = tk.Entry(
            save_path_frame, 
            textvariable=self.save_path_var,
            font=("微软雅黑", 10)
        )
        self.save_path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        browse_button = tk.Button(
            save_path_frame, 
            text="浏览...",
            command=self.browse_save_location,
            bg=self.accent_color,
            fg="white",
            font=("微软雅黑", 9),
            relief=tk.FLAT,
            padx=10
        )
        browse_button.pack(side=tk.LEFT)
        
        # ===== 高级设置选项卡内容 =====
        # 超时设置
        timeout_frame = tk.Frame(advanced_tab, bg=self.bg_color)
        timeout_frame.pack(fill=tk.X, padx=10, pady=10)
        
        timeout_label = tk.Label(
            timeout_frame, 
            text="请求超时(秒):", 
            font=("微软雅黑", 10),
            bg=self.bg_color,
            fg=self.text_color
        )
        timeout_label.pack(side=tk.LEFT, padx=(0, 5))
        
        self.timeout_var = tk.StringVar()
        self.timeout_var.set("30")
        self.timeout_entry = tk.Entry(
            timeout_frame, 
            textvariable=self.timeout_var,
            font=("微软雅黑", 10),
            width=10
        )
        self.timeout_entry.pack(side=tk.LEFT, padx=(0, 10))
        
        # 请求头设置
        headers_frame = tk.LabelFrame(
            advanced_tab, 
            text="请求头设置", 
            font=("微软雅黑", 11),
            fg=self.text_color,
            bg=self.bg_color
        )
        headers_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 显示默认请求头
        self.headers_text = scrolledtext.ScrolledText(
            headers_frame, 
            font=("微软雅黑", 9),
            bg="white",
            fg=self.text_color,
            height=12
        )
        self.headers_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 将默认请求头转为格式化的JSON
        default_headers_json = json.dumps(self.default_headers, indent=4)
        self.headers_text.insert(tk.END, default_headers_json)
        
        # 提示信息
        headers_hint = tk.Label(
            headers_frame, 
            text="请使用JSON格式设置请求头，修改或添加需要的键值对",
            font=("微软雅黑", 9),
            fg="#666666",
            bg=self.bg_color
        )
        headers_hint.pack(padx=10, pady=(0, 10), anchor="w")
        
        # 恢复默认按钮
        reset_headers_btn = tk.Button(
            headers_frame, 
            text="恢复默认请求头",
            command=self.reset_default_headers,
            bg="#cccccc",
            fg=self.text_color,
            font=("微软雅黑", 9),
            relief=tk.FLAT,
            padx=10
        )
        reset_headers_btn.pack(pady=(0, 10))
        
        # 按钮区域 (放在主框架)
        button_frame = tk.Frame(main_frame, bg=self.bg_color)
        button_frame.pack(fill=tk.X, pady=10)
        
        self.start_button = tk.Button(
            button_frame, 
            text="开始下载",
            command=self.start_crawling,
            bg=self.accent_color,
            fg="white",
            font=("微软雅黑", 11, "bold"),
            relief=tk.FLAT,
            padx=20,
            pady=8
        )
        self.start_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.stop_button = tk.Button(
            button_frame, 
            text="停止下载",
            command=self.stop_crawling,
            bg="#e74c3c",
            fg="white",
            font=("微软雅黑", 11),
            relief=tk.FLAT,
            padx=20,
            pady=8,
            state=tk.DISABLED
        )
        self.stop_button.pack(side=tk.LEFT)
        
        # 日志区域
        log_frame = tk.LabelFrame(
            main_frame, 
            text="下载日志", 
            font=("微软雅黑", 12),
            fg=self.text_color,
            bg=self.bg_color
        )
        log_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        
        self.log_text = scrolledtext.ScrolledText(
            log_frame, 
            font=("微软雅黑", 9),
            bg="white",
            fg=self.text_color
        )
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 状态栏
        self.status_var = tk.StringVar()
        self.status_var.set("准备就绪")
        
        status_bar = tk.Label(
            self.root, 
            textvariable=self.status_var,
            font=("微软雅黑", 9),
            bd=1,
            relief=tk.SUNKEN,
            anchor=tk.W,
            padx=10,
            pady=5
        )
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # 进度条
        self.progress_var = tk.DoubleVar()
        self.progress = ttk.Progressbar(
            main_frame, 
            variable=self.progress_var,
            maximum=100
        )
        self.progress.pack(fill=tk.X, pady=(10, 0))
        
        # 线程控制变量
        self.crawling = False
        self.current_thread = None
    
    def preview_webpage(self):
        """预览网页功能"""
        url = self.url_entry.get().strip()
        if not url:
            self.log("错误: 请输入网页地址")
            return
        
        if not (url.startswith('http://') or url.startswith('https://')):
            url = 'http://' + url
            self.url_entry.delete(0, tk.END)
            self.url_entry.insert(0, url)
        
        try:
            # 获取请求头
            headers = self.get_headers()
            
            # 获取超时设置
            try:
                timeout = int(self.timeout_var.get())
                if timeout <= 0:
                    timeout = 30
            except ValueError:
                timeout = 30
            
            self.log(f"正在预览网页: {url}")
            self.update_status(f"正在加载网页预览...")
            
            # 使用系统默认浏览器打开URL
            webbrowser.open(url)
            self.update_status("网页已在浏览器中打开")
            
        except Exception as e:
            self.log(f"预览网页时出错: {str(e)}")
            self.update_status("准备就绪")
    
    def reset_default_headers(self):
        self.headers_text.delete(1.0, tk.END)
        default_headers_json = json.dumps(self.default_headers, indent=4)
        self.headers_text.insert(tk.END, default_headers_json)
        
    def browse_save_location(self):
        folder_path = filedialog.askdirectory()
        if folder_path:
            self.save_path_var.set(folder_path)
    
    def log(self, message):
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
    
    def update_status(self, message):
        self.status_var.set(message)
    
    def get_headers(self):
        try:
            headers_text = self.headers_text.get(1.0, tk.END).strip()
            if headers_text:
                return json.loads(headers_text)
            return {}
        except json.JSONDecodeError:
            self.log("错误: 请求头格式不正确，请检查JSON格式")
            return self.default_headers
    
    def start_crawling(self):
        url = self.url_entry.get().strip()
        if not url:
            self.log("错误: 请输入网页地址")
            return
        
        if not (url.startswith('http://') or url.startswith('https://')):
            url = 'http://' + url
            self.url_entry.delete(0, tk.END)
            self.url_entry.insert(0, url)
        
        file_types_input = self.file_type_entry.get().strip()
        if file_types_input:
            target_file_types = [t.strip() for t in file_types_input.split(',')]
        else:
            target_file_types = ["ALL"]
        
        save_path = self.save_path_var.get()
        if not os.path.exists(save_path):
            try:
                os.makedirs(save_path)
            except Exception as e:
                self.log(f"错误: 创建保存目录失败 - {e}")
                return
        
        # 获取请求头
        headers = self.get_headers()
        
        # 获取超时设置
        try:
            timeout = int(self.timeout_var.get())
            if timeout <= 0:
                self.log("警告: 超时设置无效，使用默认值30秒")
                timeout = 30
        except ValueError:
            self.log("警告: 超时设置无效，使用默认值30秒")
            timeout = 30
        
        self.crawling = True
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.progress_var.set(0)
        self.log_text.delete(1.0, tk.END)
        self.log(f"开始下载任务...\n目标网址: {url}\n文件类型: {', '.join(target_file_types) if target_file_types != ['ALL'] else '所有文件'}\n保存位置: {save_path}\n")
        self.log(f"请求头: {json.dumps(headers, indent=2, ensure_ascii=False)}")
        self.log(f"超时设置: {timeout}秒\n")
        
        # 在新线程中运行爬取任务
        self.current_thread = threading.Thread(
            target=self.crawl_website,
            args=(url, target_file_types, save_path, headers, timeout)
        )
        self.current_thread.daemon = True
        self.current_thread.start()
    
    def stop_crawling(self):
        if self.crawling:
            self.crawling = False
            self.update_status("正在停止下载...")
            self.log("正在停止下载任务...")
    
    def crawl_website(self, url, target_file_types, save_path, headers, timeout):
        try:
            self.update_status(f"正在获取网页内容: {url}")
            self.log(f"正在获取网页内容...")
            
            response = requests.get(url, headers=headers, timeout=timeout)
            if response.status_code != 200:
                self.log(f"请求失败，状态码: {response.status_code}")
                self.finish_crawling()
                return
            
            soup = BeautifulSoup(response.text, 'html.parser')
            links = soup.find_all('a')
            valid_links = []
            
            for link in links:
                href = link.get('href')
                if href and not href.startswith('#') and not href.startswith('javascript:'):
                    # 将相对URL转换为绝对URL
                    full_url = urljoin(url, href)
                    if target_file_types == ["ALL"] or any(full_url.lower().endswith(file_type.lower()) for file_type in target_file_types):
                        valid_links.append(full_url)
            
            total_files = len(valid_links)
            if total_files == 0:
                self.log("未找到符合条件的文件链接")
                self.finish_crawling()
                return
            
            self.log(f"找到 {total_files} 个文件链接")
            downloaded = 0
            
            for i, file_url in enumerate(valid_links):
                if not self.crawling:
                    break
                
                try:
                    # 获取文件名
                    file_name = file_url.split('/')[-1]
                    # 处理URL中的查询参数
                    if '?' in file_name:
                        file_name = file_name.split('?')[0]
                    # 净化文件名，移除非法字符
                    file_name = re.sub(r'[\\/*?:"<>|]', "", file_name)
                    if not file_name:
                        file_name = f"file_{i+1}"
                    
                    self.update_status(f"正在下载: {file_name} ({i+1}/{total_files})")
                    self.log(f"下载中: {file_name}")
                    
                    file_response = requests.get(file_url, headers=headers, timeout=timeout)
                    if file_response.status_code == 200:
                        file_path = os.path.join(save_path, file_name)
                        with open(file_path, 'wb') as f:
                            f.write(file_response.content)
                        downloaded += 1
                        self.log(f"✓ 已成功下载: {file_name}")
                    else:
                        self.log(f"✗ 下载失败: {file_name} - 状态码: {file_response.status_code}")
                
                except Exception as e:
                    self.log(f"✗ 下载 {file_url} 时出错: {str(e)}")
                
                # 更新进度条
                progress = (i + 1) / total_files * 100
                self.progress_var.set(progress)
            
            if not self.crawling:
                self.log("\n下载任务已手动停止")
            else:
                self.log(f"\n下载任务完成: 共成功下载 {downloaded}/{total_files} 个文件")
            
            self.finish_crawling()
            
        except Exception as e:
            self.log(f"爬取过程中出错: {str(e)}")
            self.finish_crawling()
    
    def finish_crawling(self):
        self.crawling = False
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.update_status("准备就绪")

if __name__ == "__main__":
    root = tk.Tk()
    app = WebCrawlerApp(root)
    root.mainloop()