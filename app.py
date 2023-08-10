import customtkinter
import threading
import sys
import json
from PIL import Image
from fake_useragent import UserAgent
from src.pdf_merge import PDFMerger
from src.pic_collector import BasicCrawler
import os

# 下载框
class WebsiteEntry(customtkinter.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.configure(border_width=1.2)
        self.grid_columnconfigure(1, weight=1)  # entry expands

        self.label = customtkinter.CTkLabel(self, text="URL")
        self.label.grid(row=0, column=0, padx=(5, 0), pady=5, sticky="w")

        self.entry = customtkinter.CTkEntry(self, border_width=0)
        self.entry.grid(row=0, column=1, columnspan=1, padx=5, pady=5, sticky="ew")

        self.add_button = customtkinter.CTkButton(self, text="+", width=25, command=self.add_entry)
        self.add_button.grid(row=0, column=2, padx=(0, 3), pady=5)

        self.remove_button = customtkinter.CTkButton(self, text="-", width=25, command=self.remove_entry)
        self.remove_button.grid(row=0, column=3, padx=(0, 5), pady=5)

        self.progressbar = customtkinter.CTkProgressBar(self)
        self.progressbar.grid(row=1, column=1, padx=5, pady=(0,5), columnspan=3, sticky="ew")
        self.progressbar.set(0)

    def get(self):
        return self.entry.get()

    def set(self, value):
        self.entry.delete(0, "end")
        self.entry.insert(0, value)
    
    def set_progress(self, value):
        self.progressbar.set(value)
    
    def reset_progress(self):
        self.progressbar.set(0)

    def add_entry(self):
        self.master.add_entry_after(self)

    def remove_entry(self):
        self.master.remove_entry(self)

class BlockWebsiteEntry(customtkinter.CTkScrollableFrame):
    def __init__(self, master, title):
        super().__init__(master, label_text=title, scrollbar_button_color="gray50")
        self.grid_columnconfigure(0, weight=1)

        self.entries = []
        for _ in range(3):
            self.add_entry(None)

    def add_entry(self, after=None):
        new_entry = WebsiteEntry(self)
        if after is not None:
            index = self.entries.index(after) + 1
            self.entries.insert(index, new_entry)
        else:
            self.entries.append(new_entry)
        self.rearrange_entries()

    def add_entry_after(self, website_entry):
        self.add_entry(website_entry)

    def remove_entry(self, website_entry):
        if len(self.entries) > 1 and website_entry in self.entries:
            website_entry.grid_forget()
            self.entries.remove(website_entry)
            self.rearrange_entries()

    def rearrange_entries(self):
        for i, entry in enumerate(self.entries):
            entry.grid(row=i, column=0, padx=(0,3), pady=(0,6), sticky="ew")
    
    def reset_progress(self):
        for entry in self.entries:
            entry.reset_progress()

# 合并成PDF或者文件夹
class PathEntry(customtkinter.CTkFrame):
    def __init__(self, master, command_add=None, command_remove=None, **kwargs):
        super().__init__(master, **kwargs)
        self.configure(border_width=1.2)
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(1, weight=1)

        self.label = customtkinter.CTkLabel(self, text="Path")
        self.label.grid(row=0, column=0, padx=(5, 0), pady=5, sticky="w")

        self.entry = customtkinter.CTkEntry(self, border_width=0)
        self.entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew", columnspan=2)

        def select_dir():
            download_dir = customtkinter.filedialog.askdirectory()
            self.entry.delete(0, customtkinter.END)
            self.entry.insert(0, download_dir)

        self.select_dir_button = customtkinter.CTkButton(self, text="...", width=25, command=select_dir)
        self.select_dir_button.grid(row=0, column=3, padx=(0, 5), pady=5, sticky="ew")

        self.del_label = customtkinter.CTkLabel(self, text="Delete")
        self.del_label.grid(row=1, column=0, padx=(5, 0), pady=(0, 5), sticky="w")

        self.del_entry = customtkinter.CTkEntry(self, border_width=0)
        self.del_entry.grid(row=1, column=1, padx=5, pady=(0, 5), sticky="ew")

        self.add_button = customtkinter.CTkButton(self, text="+", width=25, command=lambda: command_add(self))
        self.add_button.grid(row=1, column=2, padx=(0, 3), pady=(0, 5))

        self.remove_button = customtkinter.CTkButton(self, text="-", width=25, command=lambda: command_remove(self))
        self.remove_button.grid(row=1, column=3, padx=(0, 5), pady=(0, 5))

    def get_path(self):
        return self.entry.get()

    def set_path(self, value):
        self.entry.delete(0, "end")
        self.entry.insert(0, value)

    def get_del(self):
        return self.del_entry.get()

    def set_del(self, value):
        self.del_entry.delete(0, "end")
        self.del_entry.insert(0, value)

class BlockPathEntry(customtkinter.CTkScrollableFrame):
    def __init__(self, master, title):
        super().__init__(master, label_text=title, scrollbar_button_color="gray50")
        self.grid_columnconfigure(0, weight=1)

        self.entries = []
        for _ in range(3):
            self.add_entry()

    def add_entry(self, path_entry=None):
        if not path_entry:
            path_entry = PathEntry(self, command_add=self.add_entry, command_remove=self.remove_entry)
            self.entries.append(path_entry)
        else:
            idx = self.entries.index(path_entry) + 1
            new_path_entry = PathEntry(self, command_add=self.add_entry, command_remove=self.remove_entry)
            self.entries.insert(idx, new_path_entry)
        
        self.rearrange_entries()

    def remove_entry(self, path_entry):
        if len(self.entries) > 1:
            path_entry.grid_forget()
            self.entries.remove(path_entry)
            self.rearrange_entries()

    def rearrange_entries(self):
        for i, entry in enumerate(self.entries):
            entry.grid(row=i, column=0, padx=(0,3), pady=(0,6), sticky="ew")


# 下载路径
class DirectoryWebsiteEntry(customtkinter.CTkFrame):
    def __init__(self, master, label_text, **kwargs):
        super().__init__(master, **kwargs)
        self.grid_columnconfigure(1, weight=1)  # entry expands

        self.label = customtkinter.CTkLabel(self, text=label_text)
        self.label.grid(row=0, column=0, padx=5, pady=(5, 0), sticky="e")

        self.entry = customtkinter.CTkEntry(self, border_width=0)
        self.entry.grid(row=1, column=0, columnspan=2, padx=5, pady=(0,5), sticky="ew")

        def select_dir():
            directory = customtkinter.filedialog.askdirectory()
            self.entry.delete(0, customtkinter.END)
            self.entry.insert(0, directory)
        self.select_dir_button = customtkinter.CTkButton(self, text="...", width=25, command=select_dir)
        self.select_dir_button.grid(row=1, column=2, padx=(0, 5), pady=(0,5), sticky="ew")

    def get(self):
        return self.entry.get()

    def set(self, value):
        self.entry.delete(0, "end")
        self.entry.insert(0, value)

# PDF或者文件夹储存路径
class DirectoryPathEntry(customtkinter.CTkFrame):
    def __init__(self, master, label_text, **kwargs):
        super().__init__(master, **kwargs)
        self.grid_columnconfigure((0,1), weight=1)


        # 切换选择文件或文件夹的按钮
        self.segmented_button = customtkinter.CTkSegmentedButton(self, values=["All", "Single"], command=self.segmented_button_callback)
        self.segmented_button.grid(row=0, column=1, columnspan=2, padx=5, pady=5, sticky="ew")
        self.segmented_button.set("All")

        # 用于选择文件或文件夹的按钮
        self.select_button = customtkinter.CTkButton(self, text="...", width=25)
        self.select_button.grid(row=1, column=2, padx=(0, 5), pady=(0,5), sticky="ew")
        self.select_button.configure(command=self.select_file)

        self.label = customtkinter.CTkLabel(self, text=label_text)
        self.label.grid(row=0, column=0, padx=(5,0), pady=5, sticky="w")

        self.entry = customtkinter.CTkEntry(self, border_width=0)
        self.entry.grid(row=1, column=0, columnspan=2, padx=5, pady=(0,5), sticky="ew")
        # self.entry.insert(0, "download/merge.pdf")

    def segmented_button_callback(self, value):
        value_dict = {"All": 'file', "Single": 'dir'}
        selet = value_dict.get(value, "Unknown value")

        if selet == 'file':
            self.entry.delete(0, "end")  # delete all text
            # self.entry.insert(0, "download/merge.pdf")
            self.select_button.configure(command=self.select_file)

        if selet == 'dir':
            self.entry.delete(0, "end")  # delete all text
            # self.entry.insert(0, "download")
            self.select_button.configure(command=self.select_dir)

    def select_file(self):
        filename = customtkinter.filedialog.asksaveasfilename(defaultextension=".pdf")
        self.entry.delete(0, customtkinter.END)
        self.entry.insert(0, filename)
        
    def select_dir(self):
        directory = customtkinter.filedialog.askdirectory()
        self.entry.delete(0, customtkinter.END)
        self.entry.insert(0, directory)

    def get(self):
        return self.entry.get()

    def set(self, value):
        self.entry.delete(0, "end")
        self.entry.insert(0, value)
    
    def get_segmented_button(self):
        if self.segmented_button.get() == 'All':
            return True
        if self.segmented_button.get() == 'Single':
            return False

# 捕获并且输出消息到消息框
class TextRedirector(object):
    def __init__(self, widget):
        self.widget = widget

    def write(self, str):
        self.widget.insert("end", str)
        self.widget.see("end")

    def flush(self):
        pass

# GUI主程序
class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        self.stop_event = threading.Event()
        self.downloading = False
        self.crawler = None

        bg = 'resources\\image\\bg.png'
        image_path = 'resources\\icon'
        data_path = 'resources\\data'

        self.title("Erohon Collector")
        self.geometry("710x700")

        with open(os.path.join(data_path, 'guide.txt'), "r", encoding="utf-8") as file:
            tips = file.read()  # 加载使用指南

        self.history_path = os.path.join(data_path, "history.json")
        with open(self.history_path, 'r')  as file:
            self.history = json.load(file)  # 加载历史记录

        purple_theme = os.path.join(data_path, 'purple_theme.json')
        if os.path.exists(purple_theme):  # 自定义主题
            customtkinter.set_default_color_theme(purple_theme)  # custom theme
        else:
            customtkinter.set_default_color_theme("blue")  # blue dark-blue green


        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)


        # 加载icon图片
        self.github = customtkinter.CTkImage(light_image=Image.open(os.path.join(image_path, "GitHub-Logo.wine-light.png")), 
                                                 dark_image=Image.open(os.path.join(image_path, "GitHub-Logo.wine-dark.png")), size=(26, 26))
        self.Download = customtkinter.CTkImage(light_image=Image.open(os.path.join(image_path, "download.png")),
                                                 dark_image=Image.open(os.path.join(image_path, "download-dark.png")), size=(20, 20))
        self.Merge = customtkinter.CTkImage(light_image=Image.open(os.path.join(image_path, "book-open.png")),
                                                 dark_image=Image.open(os.path.join(image_path, "book-open-dark.png")), size=(20, 20))
        self.Guide = customtkinter.CTkImage(light_image=Image.open(os.path.join(image_path, "help-circle.png")),
                                                     dark_image=Image.open(os.path.join(image_path, "help-circle-dark.png")), size=(20, 20))


        # 创建导航栏
        self.navigation_frame = customtkinter.CTkFrame(self, corner_radius=0)
        self.navigation_frame.grid(row=0, column=0, sticky="nsew")
        self.navigation_frame.grid_rowconfigure(4, weight=1)
        self.navigation_frame_label = customtkinter.CTkButton(self.navigation_frame, text=" RAINDROP213", image=self.github, 
                                                              height=80, corner_radius=0,fg_color="transparent", text_color=("gray10", "gray90"),
                                                              command=self.open_url, compound="left", font=customtkinter.CTkFont(size=15, weight="bold"))
        self.navigation_frame_label.grid(row=0, column=0, sticky='nsew')

        self.frame_1_button = customtkinter.CTkButton(self.navigation_frame, corner_radius=0, height=40, border_spacing=10, text=" Download",
                                                   fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"),
                                                   image=self.Download, anchor="w", command=self.frame_1_button_event)
        self.frame_1_button.grid(row=1, column=0, sticky="ew")

        self.frame_2_button = customtkinter.CTkButton(self.navigation_frame, corner_radius=0, height=40, border_spacing=10, text=" Merge",
                                                      fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"),
                                                      image=self.Merge, anchor="w", command=self.frame_2_button_event)
        self.frame_2_button.grid(row=2, column=0, sticky="ew")

        self.frame_3_button = customtkinter.CTkButton(self.navigation_frame, corner_radius=0, height=40, border_spacing=10, text=" Guide",
                                                      fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"),
                                                      image=self.Guide, anchor="w", command=self.frame_3_button_event)
        self.frame_3_button.grid(row=3, column=0, sticky="ew")

        self.appearance_mode_menu = customtkinter.CTkOptionMenu(self.navigation_frame, values=["System", "Light", "Dark"],
                                                                command=self.change_appearance_mode_event)
        self.appearance_mode_menu.grid(row=6, column=0, padx=20, pady=20, sticky="s")
        self.appearance_mode_menu.set("Light")


        # 创建窗口1
        self.first_frame = customtkinter.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.first_frame.grid_columnconfigure(0, weight=1)
        self.first_frame.grid_rowconfigure(0, weight=1)

        # 下载窗口
        self.website_entry_frame = BlockWebsiteEntry(self.first_frame, title="Download Images")
        self.website_entry_frame.grid(row=0, column=0, padx=10, pady=(10, 5), sticky="nsew", columnspan=2)

        self.download_path_entry = DirectoryWebsiteEntry(self.first_frame, label_text="Download Path")
        self.download_path_entry.grid(row=1, column=0, padx=(10, 5), pady=5, sticky="ew")
        self.download_button = customtkinter.CTkButton(self.first_frame, text="Download", command=self.download_images)
        self.download_button.grid(row=1, column=1, padx=(5, 10), pady=5, sticky="nsew")
        self.stop_button = customtkinter.CTkButton(self.first_frame, text="Stop", fg_color='#af2700', hover_color='#C74D01', command=self.stop_download)

        self.header = customtkinter.CTkTextbox(self.first_frame, height=80, wrap='none')
        self.header.grid(row=2, column=0, padx=10, pady=(5, 5), sticky="nsew", columnspan=2)

        self.refresh_button = customtkinter.CTkButton(self.first_frame, text="Refresh User-Agent", command=self.refresh_callback)
        self.refresh_button.grid(row=3, column=0, padx=(10, 5), pady=5, sticky="we")
        self.combobox_1 = customtkinter.CTkComboBox(self.first_frame, values=["0.2", "0.5", "1.0"])
        self.combobox_1.grid(row=3, column=1, padx=(5, 10), pady=5, sticky="we") 
        self.refresh_callback()  # 初始化请求头

        # 消息框-logs
        self.text_1 = customtkinter.CTkTextbox(self.first_frame, wrap='none')
        self.text_1.grid(row=4, column=0, padx=10, pady=(10, 5), sticky="nsew", columnspan=2)
        self.text_1.insert("0.0", "Logs\n\n\n")
        self.button_1 = customtkinter.CTkButton(self.first_frame, text="clear message", command=self.button_clear_callback_1)
        self.button_1.grid(row=5, column=1, padx=10, pady=(5, 10), sticky="we")

        # 创建窗口2
        self.second_frame = customtkinter.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.second_frame.grid_columnconfigure(0, weight=1)
        self.second_frame.grid_rowconfigure((0,3), weight=1)

        # 文件合并处理窗口
        self.path_entry_frame = BlockPathEntry(self.second_frame, title="Merge PDFs")
        self.path_entry_frame.grid(row=0, column=0, padx=10, pady=(10, 5), sticky="nsew", columnspan=2)

        self.output_path_entry = DirectoryPathEntry(self.second_frame, label_text="Output File")
        self.output_path_entry.grid(row=1, column=0, padx=(10, 5), pady=5, sticky="ew")
        self.merge_button = customtkinter.CTkButton(self.second_frame, text="Merge", command=self.merge_pdf)
        self.merge_button.grid(row=1, column=1, padx=(5, 10), pady=5, sticky="nse")

        self.quality_bar = customtkinter.CTkSlider(self.second_frame, from_=55, to=95, number_of_steps=4)
        self.quality_bar.grid(row=2, column=0, padx=(10, 5), pady=(5, 10), sticky="we")
        self.option_save_image = customtkinter.CTkCheckBox(self.second_frame, text='Pack to folder')
        self.option_save_image.grid(row=2, column=1, padx=(9, 10), pady=(5, 10), sticky="w")

        # 消息框-logs
        self.text_2 = customtkinter.CTkTextbox(self.second_frame, wrap='none')
        self.text_2.grid(row=3, column=0, padx=10, pady=(10, 5), sticky="nsew", columnspan=2)
        self.text_2.insert("0.0", "Logs\n\n\n\n")
        self.button_2 = customtkinter.CTkButton(self.second_frame, text="clear message", command=self.button_clear_callback_2)
        self.button_2.grid(row=4, column=1, padx=10, pady=(5, 10), sticky="e")


        # 创建窗口3
        self.third_frame = customtkinter.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.third_frame.grid_rowconfigure(0, weight=1)
        self.third_frame.grid_columnconfigure(0, weight=1)

        # 添加背景图像
        image = Image.open(bg)
        image = image.convert("RGBA")
        image_light = Image.blend(Image.new("RGBA", image.size), image, alpha=0.78)
        image_dark = Image.blend(Image.new("RGBA", image.size), image, alpha=0.5)
        self.background_image = customtkinter.CTkImage(light_image=image_light, dark_image=image_dark, size=image.size)

        self.background_label = customtkinter.CTkLabel(self.third_frame, text=tips, image=self.background_image, text_color=("gray0", "#DCE4EE"))
        self.background_label.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        # GUI基础设置
        self.select_frame_by_name("frame_1")  # 默认在窗口1
        self.download_path_entry.set(self.history["download_path"])  # 默认上一次的下载路径
        self.quality_bar.set(95)  # 默认合并质量
        sys.stdout = TextRedirector(self.text_1)  # 重定向 stdout / stderr
        self.protocol("WM_DELETE_WINDOW", self.close_event)  # 关闭GUI前结束所有任务

    def update_progress_bars(self):
        if not self.crawler:
            return  # 如果爬虫还没创建，直接返回

        progress_dict = self.crawler.get_progress()  # 从爬虫中获取进度字典
        for entry in self.website_entry_frame.entries:
            url = entry.get()
            progress = progress_dict.get(url, 0)
            entry.set_progress(progress)  # 更新进度条

        if self.downloading:  # 如果仍在下载中，则继续周期性检查进度
            self.after(200, self.update_progress_bars)

    def download_images_in_background(self):
        headers = self.header.get("0.0", "end").strip()
        sleep_time = float(self.combobox_1.get())
        self.crawler = BasicCrawler(headers_string=headers, sleep_time=sleep_time)
        download_path = self.download_path_entry.get().strip()
        url_list = [entry.get() for entry in self.website_entry_frame.entries if entry.get().strip()]

        if download_path and url_list:
            try:
                self.download_button.grid_remove()  # 隐藏Download按钮
                self.stop_button.grid(row=1, column=1, padx=(5, 10), pady=5, sticky="nsew")  # 显示Stop按钮
                self.downloading = True  # 设置下载标志
                self.website_entry_frame.reset_progress()  # 重置进度条
                self.update_progress_bars()  # 开始周期性检查进度
                self.crawler.batch_process(url_list, download_path)
            except Exception as e:
                self.text_1.insert("end", f'Error: {e}\n')
            finally:
                self.downloading = False  # 清除下载标志
                self.website_entry_frame.reset_progress()  # 重置进度条
        else:
            self.text_1.insert("end", 'Please enter URL and download path\n')
        # Show the Download button, hide the Pause and Stop buttons
        self.download_button.grid(row=1, column=1, padx=(5, 10), pady=5, sticky="nsew")
        self.stop_button.grid_remove()
        self.text_1.insert("end", '--------------------------\n\n')

    def merge_pdf_in_background(self):
        paths = []
        for entry in self.path_entry_frame.entries:
            filepath = entry.get_path().strip()
            if filepath:
                pages = entry.get_del().strip()
                if pages:
                    pages = list(map(int, pages.split()))
                else:
                    pages = []
                paths.append({"file_path": filepath, "pages_to_delete": pages})
        try:
            merger = PDFMerger(paths, self.output_path_entry.get().strip(),
                               merge_all=self.output_path_entry.get_segmented_button(),
                               quality=int(self.quality_bar.get()),
                               save_images=self.option_save_image.get(),
                               )
            merger.merge()
            self.text_2.insert("end", 'Completed all missions!\n')
        except Exception as e:
            self.text_2.insert("end", f'Error: {e}\n')
        self.text_2.insert("end", '--------------------------\n\n')

    def download_images(self):
        self.stop_event.clear()
        self.download_thread = threading.Thread(target=self.download_images_in_background, daemon=True)
        self.download_thread.start()

    def merge_pdf(self):
        self.stop_event.clear()
        self.merge_thread = threading.Thread(target=self.merge_pdf_in_background)
        self.merge_thread.start()

    def refresh_callback(self):
        self.header.delete("0.0", "end")
        for _ in range(5):
            ua = UserAgent().random
            self.header.insert("0.0", str(ua) + '\n')

    def button_clear_callback_1(self):
        self.text_1.delete("0.0", "end")
        # 清空logs记录
    
    def button_clear_callback_2(self):
        self.text_2.delete("0.0", "end")
        # 清空logs记录

    def stop_download(self):
        self.crawler.stop_requested = True
        self.downloading = False  # 清除下载标志
        self.download_button.configure(text="Download")
        self.text_1.insert("end", '\n*** Stop download ***\n\n')
        # Hide Stop buttons, show the Download button
        self.stop_button.grid_remove()
        self.download_button.grid(row=1, column=1, padx=(5, 10), pady=5, sticky="nsew")

    def close_event(self):
        # 先保存历史记录
        self.history['download_path'] = self.download_path_entry.get().strip()
        with open( self.history_path, 'w') as file:
            json.dump(self.history, file, indent=4)

        # 检查线程是否结束
        if hasattr(self, 'download_thread'):
            self.download_thread.join(timeout=1)
        elif hasattr(self, 'merge_thread'):
            self.merge_thread.join(timeout=1)
        self.destroy()


    def select_frame_by_name(self, name):
        # set button color for selected button
        self.frame_1_button.configure(fg_color=("gray75", "gray25") if name == "frame_1" else "transparent")
        self.frame_2_button.configure(fg_color=("gray75", "gray25") if name == "frame_2" else "transparent")
        self.frame_3_button.configure(fg_color=("gray75", "gray25") if name == "frame_3" else "transparent")

        # show selected frame
        if name == "frame_1":
            self.first_frame.grid(row=0, column=1, sticky="nsew")
        else:
            self.first_frame.grid_forget()
        if name == "frame_2":
            self.second_frame.grid(row=0, column=1, sticky="nsew")
        else:
            self.second_frame.grid_forget()
        if name == "frame_3":
            self.third_frame.grid(row=0, column=1, sticky="nsew")
        else:
            self.third_frame.grid_forget()

    def frame_1_button_event(self):
        self.select_frame_by_name("frame_1")

    def frame_2_button_event(self):
        self.select_frame_by_name("frame_2")

    def frame_3_button_event(self):
        self.select_frame_by_name("frame_3")

    def change_appearance_mode_event(self, new_appearance_mode):
        customtkinter.set_appearance_mode(new_appearance_mode)

    @staticmethod
    def open_url():
        url = "https://github.com/raindrop213/erohon-collector"
        import webbrowser
        webbrowser.open(url)


app = App()
app.mainloop()
