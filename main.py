import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import qrcode
from PIL import Image, ImageTk
import textwrap
import os
import tempfile
import webbrowser


class QRCodeGeneratorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("长文本二维码生成器")
        self.root.geometry("900x900")
        self.root.resizable(True, True)

        # 设置应用主题色
        self.primary_color = "#2E86AB"  # 深蓝色
        self.secondary_color = "#A23B72"  # 紫红色
        self.accent_color = "#F18F01"  # 橙色
        self.bg_color = "#F8F9FA"  # 浅灰色背景
        self.text_color = "#2C3E50"  # 深灰色文字
        self.success_color = "#27AE60"  # 绿色
        self.warning_color = "#E74C3C"  # 红色

        self.root.configure(bg=self.bg_color)

        # 应用变量
        self.qr_codes = []  # 存储二维码图片
        self.current_index = 0  # 当前显示的二维码索引
        self.max_chars = 800  # 每个二维码最多包含的字符数

        # 创建UI
        self.create_widgets()

        # 居中显示主窗口
        self.center_window(self.root)

    def create_widgets(self):
        # 创建样式
        style = ttk.Style()
        style.theme_use('clam')  # 使用clam主题作为基础

        # 配置按钮样式
        style.configure("Primary.TButton",
                        padding=(15, 8),
                        font=("Microsoft YaHei UI", 10, "bold"),
                        background=self.primary_color,
                        foreground="white")

        style.configure("Secondary.TButton",
                        padding=(12, 6),
                        font=("Microsoft YaHei UI", 9),
                        background=self.secondary_color)

        style.configure("Success.TButton",
                        padding=(12, 6),
                        font=("Microsoft YaHei UI", 9),
                        background=self.success_color)

        # 配置框架样式
        style.configure("Card.TFrame",
                        background="white",
                        relief="solid",
                        borderwidth=1)

        # 配置标签样式
        style.configure("Title.TLabel",
                        font=("Microsoft YaHei UI", 14, "bold"),
                        foreground=self.primary_color,
                        background="white")

        style.configure("Subtitle.TLabel",
                        font=("Microsoft YaHei UI", 11),
                        foreground=self.text_color,
                        background="white")

        # 主容器
        main_container = tk.Frame(self.root, bg=self.bg_color, padx=20, pady=20)
        main_container.pack(fill=tk.BOTH, expand=True)

        # 标题区域
        title_frame = tk.Frame(main_container, bg=self.bg_color)
        title_frame.pack(fill=tk.X, pady=(0, 20))

        title_label = tk.Label(title_frame,
                               text="长文本二维码生成器",
                               font=("Microsoft YaHei UI", 20, "bold"),
                               fg=self.primary_color,
                               bg=self.bg_color)
        title_label.pack()

        subtitle_label = tk.Label(title_frame,
                                  text="将长文本分割成多个二维码，支持批量下载",
                                  font=("Microsoft YaHei UI", 11),
                                  fg=self.text_color,
                                  bg=self.bg_color)
        subtitle_label.pack(pady=(5, 0))

        # 输入区域卡片
        input_card = tk.Frame(main_container, bg="white", relief="solid", bd=1, padx=20, pady=8)
        input_card.pack(fill=tk.X, pady=(0, 10))

        input_title = tk.Label(input_card,
                               text="输入文本",
                               font=("Microsoft YaHei UI", 14, "bold"),
                               fg=self.primary_color,
                               bg="white")
        input_title.pack(anchor=tk.W, pady=(0, 10))

        # 文本输入框
        text_frame = tk.Frame(input_card, bg="white")
        text_frame.pack(fill=tk.BOTH, expand=True)

        self.text_input = tk.Text(text_frame,
                                  height=2,
                                  wrap=tk.WORD,
                                  font=("Microsoft YaHei UI", 10),
                                  relief="solid",
                                  bd=1,
                                  padx=10,
                                  pady=10,
                                  bg="#FAFAFA",
                                  fg=self.text_color,
                                  insertbackground=self.primary_color)
        self.text_input.pack(fill=tk.BOTH, expand=True)
        self.text_input.bind("<KeyRelease>", self.update_char_count)

        # 字符计数标签
        self.char_count = tk.Label(input_card,
                                   text="字符数: 0",
                                   font=("Microsoft YaHei UI", 9),
                                   fg=self.text_color,
                                   bg="white",
                                   anchor=tk.W)
        self.char_count.pack(fill=tk.X, pady=(10, 0))

        # 按钮区域
        button_frame = tk.Frame(input_card, bg="white")
        button_frame.pack(fill=tk.X, pady=(15, 0))

        self.generate_btn = tk.Button(button_frame,
                                      text="生成二维码",
                                      command=self.generate_qr_codes,
                                      state=tk.DISABLED,
                                      font=("Microsoft YaHei UI", 11, "bold"),
                                      bg=self.primary_color,
                                      fg="white",
                                      relief="flat",
                                      padx=20,
                                      pady=8,
                                      cursor="hand2")
        self.generate_btn.pack(side=tk.LEFT, padx=(0, 10))

        self.show_text_btn = tk.Button(button_frame,
                                       text="展示全部",
                                       command=self.show_full_text,
                                       font=("Microsoft YaHei UI", 10),
                                       bg=self.secondary_color,
                                       fg="white",
                                       relief="flat",
                                       padx=15,
                                       pady=6,
                                       cursor="hand2")
        self.show_text_btn.pack(side=tk.LEFT, padx=(0, 10))

        self.clear_btn = tk.Button(button_frame,
                                   text="清空内容",
                                   command=self.clear_content,
                                   font=("Microsoft YaHei UI", 10),
                                   bg="#6C757D",
                                   fg="white",
                                   relief="flat",
                                   padx=15,
                                   pady=6,
                                   cursor="hand2")
        self.clear_btn.pack(side=tk.LEFT)

        # 二维码显示区域卡片
        qr_card = tk.Frame(main_container, bg="white", relief="solid", bd=1, padx=10, pady=8)
        qr_card.pack(fill=tk.BOTH, expand=True)

        qr_title = tk.Label(qr_card,
                            text="二维码预览",
                            font=("Microsoft YaHei UI", 14, "bold"),
                            fg=self.primary_color,
                            bg="white")
        qr_title.pack(anchor=tk.W, pady=(0, 3))

        # 二维码显示容器
        self.qr_container = tk.Frame(qr_card, bg="white")
        self.qr_container.pack(fill=tk.BOTH, expand=True, padx=3, pady=3)

        # 默认占位符
        placeholder_frame = tk.Frame(self.qr_container, bg="white")
        placeholder_frame.pack(expand=True)

        placeholder_icon = tk.Label(placeholder_frame,
                                    text="QR",
                                    font=("Microsoft YaHei UI", 48),
                                    fg="#DEE2E6",
                                    bg="white")
        placeholder_icon.pack()

        placeholder = tk.Label(placeholder_frame,
                               text="请在上方输入文本并点击'生成二维码'按钮",
                               font=("Microsoft YaHei UI", 12),
                               fg="#6C757D",
                               bg="white")
        placeholder.pack(pady=(10, 0))

        # 导航控制区域
        nav_frame = tk.Frame(qr_card, bg="white")
        nav_frame.pack(fill=tk.X, pady=(10, 0))

        # 导航按钮
        nav_btn_frame = tk.Frame(nav_frame, bg="white")
        nav_btn_frame.pack(side=tk.LEFT)

        self.prev_btn = tk.Button(nav_btn_frame,
                                  text="上一张",
                                  command=self.show_prev,
                                  state=tk.DISABLED,
                                  font=("Microsoft YaHei UI", 9),
                                  bg=self.secondary_color,
                                  fg="white",
                                  relief="flat",
                                  padx=12,
                                  pady=4,
                                  cursor="hand2")
        self.prev_btn.pack(side=tk.LEFT, padx=(0, 5))

        self.page_label = tk.Label(nav_btn_frame,
                                   text="0/0",
                                   font=("Microsoft YaHei UI", 10, "bold"),
                                   fg=self.primary_color,
                                   bg="white",
                                   width=10)
        self.page_label.pack(side=tk.LEFT)

        self.next_btn = tk.Button(nav_btn_frame,
                                  text="下一张",
                                  command=self.show_next,
                                  state=tk.DISABLED,
                                  font=("Microsoft YaHei UI", 9),
                                  bg=self.secondary_color,
                                  fg="white",
                                  relief="flat",
                                  padx=12,
                                  pady=4,
                                  cursor="hand2")
        self.next_btn.pack(side=tk.LEFT, padx=(5, 20))

        # 下载按钮
        download_btn_frame = tk.Frame(nav_frame, bg="white")
        download_btn_frame.pack(side=tk.RIGHT)

        self.download_single_btn = tk.Button(download_btn_frame,
                                             text="下载当前",
                                             command=self.download_single_qr,
                                             state=tk.DISABLED,
                                             font=("Microsoft YaHei UI", 9),
                                             bg=self.success_color,
                                             fg="white",
                                             relief="flat",
                                             padx=12,
                                             pady=4,
                                             cursor="hand2")
        self.download_single_btn.pack(side=tk.LEFT, padx=(0, 5))

        self.download_all_btn = tk.Button(download_btn_frame,
                                          text="下载全部",
                                          command=self.download_all_qr,
                                          state=tk.DISABLED,
                                          font=("Microsoft YaHei UI", 9),
                                          bg=self.accent_color,
                                          fg="white",
                                          relief="flat",
                                          padx=12,
                                          pady=4,
                                          cursor="hand2")
        self.download_all_btn.pack(side=tk.LEFT)

        # 状态栏
        status_frame = tk.Frame(self.root, bg="#E9ECEF")
        status_frame.pack(side=tk.BOTTOM, fill=tk.X)

        self.status_bar = tk.Label(status_frame,
                                   text="就绪 - 请输入文本开始生成二维码",
                                   relief=tk.SUNKEN,
                                   anchor=tk.W,
                                   font=("Microsoft YaHei UI", 9),
                                   fg=self.text_color,
                                   bg="#E9ECEF",
                                   padx=10,
                                   pady=5)
        self.status_bar.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # 版权信息
        copyright_label = tk.Label(status_frame,
                                   text="© 2025 xuzhenkang",
                                   relief=tk.SUNKEN,
                                   anchor=tk.E,
                                   font=("Microsoft YaHei UI", 9),
                                   fg="#007ACC",  # 蓝色链接颜色
                                   bg="#E9ECEF",
                                   padx=10,
                                   pady=5,
                                   cursor="hand2")  # 鼠标悬停时显示手型光标
        copyright_label.pack(side=tk.RIGHT)

        # 绑定点击事件
        copyright_label.bind("<Button-1>", self.open_github)
        copyright_label.bind("<Enter>", lambda e: copyright_label.config(fg="#005A9E"))  # 悬停时变深蓝色
        copyright_label.bind("<Leave>", lambda e: copyright_label.config(fg="#007ACC"))  # 离开时恢复原色

    def update_char_count(self, event=None):
        """更新字符计数标签"""
        text = self.text_input.get("1.0", tk.END).strip()
        count = len(text)
        self.char_count.config(text=f"字符数: {count}")

        # 根据文本长度启用/禁用生成按钮
        if count > 0:
            self.generate_btn.config(state=tk.NORMAL)
        else:
            self.generate_btn.config(state=tk.DISABLED)

    def generate_qr_codes(self):
        """生成二维码"""
        text = self.text_input.get("1.0", tk.END).strip()
        if not text:
            messagebox.showwarning("输入错误", "请输入要生成二维码的文本内容")
            return

        self.status_bar.config(text="正在生成二维码...")
        self.root.update()

        try:
            # 清空现有二维码
            self.qr_codes = []
            self.current_index = 0

            # 分割长文本
            segments = self.split_text(text)

            # 为每个文本段生成二维码
            for i, segment in enumerate(segments):
                qr = qrcode.QRCode(
                    version=None,
                    error_correction=qrcode.constants.ERROR_CORRECT_M,
                    box_size=10,
                    border=4,
                )
                qr.add_data(segment)
                qr.make(fit=True)

                # 创建二维码图像并转换为PhotoImage
                img = qr.make_image(fill_color="black", back_color="white")
                original_img = img.copy()  # 保存原始图像用于下载
                img = img.resize((350, 350), Image.LANCZOS)
                photo = ImageTk.PhotoImage(img)

                # 存储二维码和相关信息
                self.qr_codes.append({
                    "photo": photo,
                    "original_image": original_img,  # 保存原始图像
                    "text": segment,
                    "index": i,
                    "total": len(segments)
                })

            # 显示第一个二维码
            if self.qr_codes:
                self.show_current_qr()
                self.update_nav_buttons()

            self.status_bar.config(text=f"已生成 {len(segments)} 个二维码")
        except Exception as e:
            messagebox.showerror("生成错误", f"生成二维码时出错:\n{str(e)}")
            self.status_bar.config(text="生成失败")

    def split_text(self, text):
        """将长文本分割为多个段落"""
        segments = []

        if len(text) <= self.max_chars:
            segments.append(text)
        else:
            # 使用textwrap分割文本，确保不会在单词中间分割
            segments = textwrap.wrap(text, width=self.max_chars,
                                     break_long_words=True,
                                     replace_whitespace=False)

        return segments

    def show_current_qr(self):
        """显示当前二维码"""
        # 清除容器中的所有小部件
        for widget in self.qr_container.winfo_children():
            widget.destroy()

        if not self.qr_codes:
            return

        # 获取当前二维码
        current_qr = self.qr_codes[self.current_index]

        # 显示二维码图像
        qr_label = tk.Label(self.qr_container, image=current_qr["photo"])
        qr_label.image = current_qr["photo"]  # 保持引用
        qr_label.pack(pady=10)

        # 显示页码信息
        self.page_label.config(text=f"{self.current_index + 1}/{len(self.qr_codes)}")

        # 显示当前段落的字符数
        char_info = tk.Label(self.qr_container,
                             text=f"当前二维码字符数: {len(current_qr['text'])}",
                             font=("Microsoft YaHei UI", 9),
                             fg=self.text_color,
                             bg="white")
        char_info.pack(pady=(0, 5))

    def show_next(self):
        """显示下一张二维码"""
        if self.current_index < len(self.qr_codes) - 1:
            self.current_index += 1
            self.show_current_qr()
            self.update_nav_buttons()

    def show_prev(self):
        """显示上一张二维码"""
        if self.current_index > 0:
            self.current_index -= 1
            self.show_current_qr()
            self.update_nav_buttons()

    def update_nav_buttons(self):
        """更新导航按钮状态"""
        if not self.qr_codes:
            self.prev_btn.config(state=tk.DISABLED)
            self.next_btn.config(state=tk.DISABLED)
            self.download_single_btn.config(state=tk.DISABLED)
            self.download_all_btn.config(state=tk.DISABLED)
            return

        self.prev_btn.config(state=tk.NORMAL if self.current_index > 0 else tk.DISABLED)
        self.next_btn.config(state=tk.NORMAL if self.current_index < len(self.qr_codes) - 1 else tk.DISABLED)
        self.download_single_btn.config(state=tk.NORMAL)
        self.download_all_btn.config(state=tk.NORMAL)

    def clear_content(self):
        """清空文本输入和二维码显示区域"""
        # 清空文本输入
        self.text_input.delete("1.0", tk.END)

        # 重置字符计数
        self.char_count.config(text="字符数: 0")

        # 禁用生成按钮
        self.generate_btn.config(state=tk.DISABLED)

        # 清空二维码数据
        self.qr_codes = []
        self.current_index = 0

        # 清除二维码显示区域并显示占位符
        for widget in self.qr_container.winfo_children():
            widget.destroy()

        placeholder_frame = tk.Frame(self.qr_container, bg="white")
        placeholder_frame.pack(expand=True)

        placeholder_icon = tk.Label(placeholder_frame,
                                    text="QR",
                                    font=("Microsoft YaHei UI", 48),
                                    fg="#DEE2E6",
                                    bg="white")
        placeholder_icon.pack()

        placeholder = tk.Label(placeholder_frame,
                               text="请在上方输入文本并点击'生成二维码'按钮",
                               font=("Microsoft YaHei UI", 12),
                               fg="#6C757D",
                               bg="white")
        placeholder.pack(pady=(10, 0))

        # 重置导航按钮和页码
        self.page_label.config(text="0/0")
        self.update_nav_buttons()

        # 更新状态栏
        self.status_bar.config(text="已清空内容")

    def download_single_qr(self):
        """下载当前显示的二维码"""
        if not self.qr_codes or self.current_index >= len(self.qr_codes):
            messagebox.showwarning("下载错误", "没有可下载的二维码")
            return

        current_qr = self.qr_codes[self.current_index]

        # 选择保存路径
        filename = f"二维码_{self.current_index + 1}_{len(self.qr_codes)}.png"
        file_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG 图片", "*.png"), ("所有文件", "*.*")],
            initialfile=filename
        )

        if file_path:
            try:
                # 保存当前二维码
                current_qr["original_image"].save(file_path, "PNG")
                self.status_bar.config(text=f"已保存: {os.path.basename(file_path)}")
                messagebox.showinfo("下载成功", f"二维码已保存到:\n{file_path}")
            except Exception as e:
                messagebox.showerror("保存错误", f"保存文件时出错:\n{str(e)}")
                self.status_bar.config(text="保存失败")

    def download_all_qr(self):
        """下载所有二维码"""
        if not self.qr_codes:
            messagebox.showwarning("下载错误", "没有可下载的二维码")
            return

        # 选择保存目录
        save_dir = filedialog.askdirectory(title="选择保存目录")
        if not save_dir:
            return

        try:
            saved_count = 0
            for i, qr_data in enumerate(self.qr_codes):
                filename = f"二维码_{i + 1}_{len(self.qr_codes)}.png"
                file_path = os.path.join(save_dir, filename)
                qr_data["original_image"].save(file_path, "PNG")
                saved_count += 1

            self.status_bar.config(text=f"已保存 {saved_count} 个二维码到: {save_dir}")
            messagebox.showinfo("下载成功", f"已成功保存 {saved_count} 个二维码到:\n{save_dir}")
        except Exception as e:
            messagebox.showerror("保存错误", f"保存文件时出错:\n{str(e)}")
            self.status_bar.config(text="保存失败")

    def show_full_text(self):
        """展示全部文本内容"""
        text = self.text_input.get("1.0", tk.END).strip()
        if not text:
            messagebox.showinfo("提示", "没有文本内容可展示")
            return

        # 创建新窗口
        text_window = tk.Toplevel(self.root)
        text_window.title("文本内容预览")
        text_window.geometry("650x800")
        text_window.resizable(True, True)
        text_window.configure(bg=self.bg_color)

        # 设置窗口图标和模态
        text_window.transient(self.root)
        text_window.grab_set()

        # 居中显示新窗口
        self.center_window(text_window)

        # 主容器
        main_frame = tk.Frame(text_window, bg=self.bg_color, padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # 标题
        title_label = tk.Label(main_frame,
                               text="文本内容预览",
                               font=("Microsoft YaHei UI", 16, "bold"),
                               fg=self.primary_color,
                               bg=self.bg_color)
        title_label.pack(pady=(0, 15))

        # 字符统计
        char_count_label = tk.Label(main_frame,
                                    text=f"字符数: {len(text)}",
                                    font=("Microsoft YaHei UI", 10),
                                    fg=self.text_color,
                                    bg=self.bg_color)
        char_count_label.pack(anchor=tk.W, pady=(0, 10))

        # 创建带滚动条的文本显示区域
        text_frame = tk.Frame(main_frame, bg="white", relief="solid", bd=1)
        text_frame.pack(fill=tk.BOTH, expand=True)

        # 创建文本框和滚动条
        text_display = tk.Text(text_frame,
                               wrap=tk.NONE,  # 改为NONE以支持水平滚动
                               font=("Microsoft YaHei UI", 11),
                               relief="flat",
                               padx=15,
                               pady=15,
                               bg="white",
                               fg=self.text_color,
                               state=tk.DISABLED)  # 设置为只读

        # 垂直滚动条
        v_scrollbar = tk.Scrollbar(text_frame, orient="vertical")
        v_scrollbar.config(command=text_display.yview)
        text_display.config(yscrollcommand=v_scrollbar.set)

        # 水平滚动条
        h_scrollbar = tk.Scrollbar(text_frame, orient="horizontal")
        h_scrollbar.config(command=text_display.xview)
        text_display.config(xscrollcommand=h_scrollbar.set)

        # 布局 - 使用grid布局确保滚动条正确显示
        text_display.grid(row=0, column=0, sticky="nsew")
        v_scrollbar.grid(row=0, column=1, sticky="ns")
        h_scrollbar.grid(row=1, column=0, sticky="ew")

        # 配置grid权重
        text_frame.grid_rowconfigure(0, weight=1)
        text_frame.grid_columnconfigure(0, weight=1)

        # 插入文本内容
        text_display.config(state=tk.NORMAL)
        text_display.insert("1.0", text)
        text_display.config(state=tk.DISABLED)

        # 更新滚动条
        text_display.update_idletasks()
        text_display.see("1.0")  # 滚动到顶部

        # 绑定鼠标滚轮事件
        text_display.bind("<MouseWheel>", lambda e: text_display.yview_scroll(-1 * (e.delta // 120), "units"))
        text_display.bind("<Button-4>", lambda e: text_display.yview_scroll(-1, "units"))
        text_display.bind("<Button-5>", lambda e: text_display.yview_scroll(1, "units"))

        # 绑定Shift+滚轮进行水平滚动
        text_display.bind("<Shift-MouseWheel>", lambda e: text_display.xview_scroll(-1 * (e.delta // 120), "units"))
        text_display.bind("<Shift-Button-4>", lambda e: text_display.xview_scroll(-1, "units"))
        text_display.bind("<Shift-Button-5>", lambda e: text_display.xview_scroll(1, "units"))

        # 按钮区域
        button_frame = tk.Frame(main_frame, bg=self.bg_color)
        button_frame.pack(fill=tk.X, pady=(15, 0))

        # 关闭按钮
        close_btn = tk.Button(button_frame,
                              text="关闭",
                              command=text_window.destroy,
                              font=("Microsoft YaHei UI", 10),
                              bg=self.primary_color,
                              fg="white",
                              relief="flat",
                              padx=20,
                              pady=6,
                              cursor="hand2")
        close_btn.pack(side=tk.RIGHT)

        # 复制按钮
        copy_btn = tk.Button(button_frame,
                             text="复制文本",
                             command=lambda: self.copy_text_to_clipboard(text),
                             font=("Microsoft YaHei UI", 10),
                             bg=self.success_color,
                             fg="white",
                             relief="flat",
                             padx=15,
                             pady=6,
                             cursor="hand2")
        copy_btn.pack(side=tk.RIGHT, padx=(0, 10))

        # 设置焦点到关闭按钮
        close_btn.focus_set()

        # 绑定回车键关闭窗口
        text_window.bind("<Return>", lambda e: text_window.destroy())
        text_window.bind("<Escape>", lambda e: text_window.destroy())

    def copy_text_to_clipboard(self, text):
        """复制文本到剪贴板"""
        try:
            self.root.clipboard_clear()
            self.root.clipboard_append(text)
            self.root.update()
            messagebox.showinfo("成功", "文本已复制到剪贴板")
        except Exception as e:
            messagebox.showerror("错误", f"复制失败: {str(e)}")

    def center_window(self, window):
        """居中显示窗口"""
        window.update_idletasks()
        width = window.winfo_width()
        height = window.winfo_height()
        x = (window.winfo_screenwidth() - width) // 2
        y = (window.winfo_screenheight() - height) // 2
        window.geometry(f"{width}x{height}+{x}+{y}")

    def open_github(self, event):
        """打开GitHub页面"""
        webbrowser.open("https://github.com/your-username/qr-code-generator")


if __name__ == "__main__":
    root = tk.Tk()
    app = QRCodeGeneratorApp(root)
    root.mainloop()
