import customtkinter
import tkinter
import threading
from PIL import Image, ImageTk
from pdf_editior import PDFEditor
from pic_collector import BasicCrawler
import sys
import os


class WebsiteEntry(customtkinter.CTkFrame):
    def __init__(self, master, command_add=None, command_remove=None, **kwargs):
        super().__init__(master, **kwargs)
        self.configure(fg_color="gray82")  # set frame color
        self.grid_columnconfigure((0, 2, 4), weight=0)  # buttons don't expand
        self.grid_columnconfigure(1, weight=1)  # entry expands

        self.label = customtkinter.CTkLabel(self, text="URL")
        self.label.grid(row=0, column=0, padx=(5, 0), pady=5, sticky="w")

        self.entry = customtkinter.CTkEntry(self, border_width=0)
        self.entry.grid(row=0, column=1, columnspan=1, padx=5, pady=5, sticky="ew")

        self.add_button = customtkinter.CTkButton(self, text="+", width=25, command=command_add)
        self.add_button.grid(row=0, column=2, padx=(0, 3), pady=5)

        self.remove_button = customtkinter.CTkButton(self, text="-", width=25, command=command_remove)
        self.remove_button.grid(row=0, column=3, padx=(0, 5), pady=5)

    def get(self):
        return self.entry.get()

    def set(self, value):
        self.entry.delete(0, "end")
        self.entry.insert(0, value)


class PathEntry(customtkinter.CTkFrame):
    def __init__(self, master, command_add=None, command_remove=None, **kwargs):
        super().__init__(master, **kwargs)
        self.configure(fg_color="gray82")  # set frame color
        self.grid_columnconfigure((0, 2, 4), weight=0)  # buttons don't expand
        self.grid_columnconfigure(1, weight=1)  # entry expands

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

        self.del_label = customtkinter.CTkLabel(self, text="Delet")
        self.del_label.grid(row=1, column=0, padx=(5, 0), pady=(0, 5), sticky="w")

        self.del_entry = customtkinter.CTkEntry(self, border_width=0)
        self.del_entry.grid(row=1, column=1, padx=5, pady=(0, 5), sticky="ew")

        self.add_button = customtkinter.CTkButton(self, text="+", width=25, command=command_add)
        self.add_button.grid(row=1, column=2, padx=(0, 3), pady=(0, 5))

        self.remove_button = customtkinter.CTkButton(self, text="-", width=25, command=command_remove)
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


class BlockWebsiteEntry(customtkinter.CTkScrollableFrame):
    def __init__(self, master, title):
        super().__init__(master, label_text=title, scrollbar_button_color="gray65")
        self.grid_columnconfigure(0, weight=1)

        self.entries = []
        for _ in range(3):
            self.add_entry()

    def add_entry(self):
        entry_row = len(self.entries) + 1

        website_entry = WebsiteEntry(self, command_add=self.add_entry, command_remove=self.remove_entry)
        website_entry.grid(row=entry_row, column=0, padx=(0,3), pady=(0,6), sticky="ew")

        self.entries.append(website_entry)

    def remove_entry(self):
        if len(self.entries) > 1:
            entry_to_remove = self.entries[-1]
            entry_to_remove.grid_forget()
            self.entries.remove(entry_to_remove)


class BlockPathEntry(customtkinter.CTkScrollableFrame):
    def __init__(self, master, title):
        super().__init__(master, label_text=title, scrollbar_button_color="gray65")
        self.grid_columnconfigure(0, weight=1)

        self.entries = []
        for _ in range(2):
            self.add_entry()

    def add_entry(self):
        entry_row = len(self.entries) + 1

        path_entry = PathEntry(self, command_add=self.add_entry, command_remove=self.remove_entry)
        path_entry.grid(row=entry_row, column=0, padx=(0,3), pady=(0,6), sticky="ew")

        self.entries.append(path_entry)

    def remove_entry(self):
        if len(self.entries) > 1:
            entry_to_remove = self.entries[-1]
            entry_to_remove.grid_forget()
            self.entries.remove(entry_to_remove)


class DirectoryEntry(customtkinter.CTkFrame):
    def __init__(self, master, label_text, selet, **kwargs):
        super().__init__(master, **kwargs)
        self.grid_columnconfigure(1, weight=1)  # entry expands

        self.label = customtkinter.CTkLabel(self, text=label_text)
        self.label.grid(row=0, column=0, padx=5, pady=(5, 0), sticky="e")

        self.entry = customtkinter.CTkEntry(self, border_width=0)
        self.entry.grid(row=1, column=0, columnspan=2, padx=5, pady=(0,5), sticky="ew")
        self.entry.insert(0, "download")

        self.selet = selet
        
        if self.selet == 'dir':
            def select_dir():
                directory = customtkinter.filedialog.askdirectory()
                self.entry.delete(0, customtkinter.END)
                self.entry.insert(0, directory)
            self.select_dir_button = customtkinter.CTkButton(self, text="...", width=25, command=select_dir)
            self.select_dir_button.grid(row=1, column=2, padx=(0, 5), pady=(0,5), sticky="ew")

        elif self.selet == 'file':
            def select_flie():
                fliename = customtkinter.filedialog.asksaveasfilename(defaultextension=".pdf")
                self.entry.delete(0, customtkinter.END)
                self.entry.insert(0, fliename)
            self.select_flie_button = customtkinter.CTkButton(self, text="...", width=25, command=select_flie)
            self.select_flie_button.grid(row=1, column=2, padx=(0, 5), pady=(0,5), sticky="ew")


    def get(self):
        return self.entry.get()

    def set(self, value):
        self.entry.delete(0, "end")
        self.entry.insert(0, value)


class TextRedirector(object):
    def __init__(self, widget, original_out):
        self.widget = widget
        self.original_out = original_out

    def write(self, str):
        self.widget.insert("end", str)
        self.widget.see("end")
        self.original_out.write(str)

    def flush(self):
        self.original_out.flush()


class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        self.stop_event = threading.Event()
        
        customtkinter.set_default_color_theme("blue")  # blue dark-blue green
        customtkinter.set_appearance_mode("system")  # dark light system

        self.title("my app")
        self.geometry("900x900")

        self.grid_columnconfigure(2, weight=1)
        self.grid_rowconfigure(4, weight=1)

        
        # 添加半透明的背景图像
        image = Image.open(bg)  # 使用你的背景图像文件名替换"background.jpg"
        image = image.convert("RGBA")
        image_light = Image.blend(Image.new("RGBA", image.size), image, alpha=0.4)
        image_dark = Image.blend(Image.new("RGBA", image.size), image, alpha=0.9)

        self.background_image = ImageTk.PhotoImage(image_light)
        # self.background_image = customtkinter.CTkImage(light_image=image_light, dark_image=image_dark, size=image.size)

        self.background_label = customtkinter.CTkLabel(self, text=tips, image=self.background_image)
        self.background_label.grid(row=0, column=2, padx=10, pady=(10, 5), sticky="nsew", rowspan=5)
        


        # Download Images
        self.website_entry_frame = BlockWebsiteEntry(self, title="Download Images")
        self.website_entry_frame.grid(row=0, column=0, padx=10, pady=(10, 5), sticky="nsew", columnspan=2)
        
        self.download_path_entry = DirectoryEntry(self, label_text="Download Path", selet='dir')
        self.download_path_entry.grid(row=1, column=0, padx=(10, 5), pady=(5, 10), sticky="ew")

        self.download_button = customtkinter.CTkButton(self, text="Download", command=self.download_images)
        self.download_button.grid(row=1, column=1, padx=(5, 10), pady=(5, 10), sticky="nse")


        # Merge PDFs
        self.path_entry_frame = BlockPathEntry(self, title="Merge PDFs")
        self.path_entry_frame.grid(row=2, column=0, padx=10, pady=(10, 5), sticky="nsew", columnspan=2)

        self.output_path_entry = DirectoryEntry(self, label_text="Output File", selet='file')
        self.output_path_entry.grid(row=3, column=0, padx=(10, 5), pady=(5, 10), sticky="ew")

        self.merge_button = customtkinter.CTkButton(self, text="Merge", command=self.merge_pdf)
        self.merge_button.grid(row=3, column=1, padx=(5, 10), pady=(5, 10), sticky="nse")

        # logs
        self.text_1 = customtkinter.CTkTextbox(self)
        self.text_1.grid(row=4, column=0, padx=(10, 5), pady=(10, 5), sticky="nsew", columnspan=2)
        self.text_1.insert("0.0", "Logs\n\n\n\n")

        self.button = customtkinter.CTkButton(self, text="test message", command=self.button_callback)
        self.button.grid(row=5, column=0, padx=(10, 5), pady=(5, 10), sticky="w")

        self.button = customtkinter.CTkButton(self, text="clear message", command=self.button_clear_callback)
        self.button.grid(row=5, column=1, padx=(5, 10), pady=(5, 10), sticky="e")

        # 开始\暂停\结束 按钮
        self.crawler = BasicCrawler()
        self.pause_button = customtkinter.CTkButton(self, text="Pause", command=self.pause_download)
        self.pause_button.grid(row=6, column=0, padx=(5, 10), pady=(5, 10), sticky="w")

        self.resume_button = customtkinter.CTkButton(self, text="Resume", command=self.resume_download)
        self.resume_button.grid(row=6, column=1, padx=(10, 5), pady=(5, 10), sticky="e")

        self.stop_button = customtkinter.CTkButton(self, text="Stop", command=self.stop_download)
        self.stop_button.grid(row=6, column=2, padx=(10, 5), pady=(5, 10), sticky="e")

        # 重定向 stdout 和 stderr
        sys.stdout = TextRedirector(self.text_1, sys.stdout)
        sys.stderr = TextRedirector(self.text_1, sys.stderr)


    def button_callback(self):
        print('You clicked the button!')
        # 引发一个错误，以便演示 stderr 的重定向
        1 / 0

    def button_clear_callback(self):
        self.text_1.delete("0.0", "end")
        # 清空logs记录


    def download_images_in_background(self):
        self.download_button.configure(text="Running...")
        print('\033[31m' + '- Running download... -' + '\033[0m')
        download_path = self.download_path_entry.get().strip()
        url_list = [entry.get() for entry in self.website_entry_frame.entries if entry.get().strip()]
        if download_path and url_list:
            self.crawler.batch_process(url_list, download_path)
        else:
            print("Please set Download path and URL")
        self.download_button.configure(text="Download")
        self.text_1.insert("end", '\n- Download Images finished-\n\n')
        
    def merge_pdf_in_background(self):
        self.merge_button.configure(text="Running...")
        print('\033[31m' + '- Running merge PDFs... -' + '\033[0m')
        pdf_editor = PDFEditor()
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
        output_file = "merged.pdf"
        output_path = os.path.join(self.output_path_entry.get().strip(), output_file)
        pdf_editor.merge_pdfs(paths, output_path)
        self.merge_button.configure(text="Merge")
        self.text_1.insert("end", '\n- Merge PDFs finished-\n\n')


    def download_images(self):
        self.stop_event.clear()
        self.current_thread = threading.Thread(target=self.download_images_in_background)
        self.current_thread.start()

    def merge_pdf(self):
        self.stop_event.clear()
        self.current_thread = threading.Thread(target=self.merge_pdf_in_background)
        self.current_thread.start()


    def pause_download(self):
        self.crawler.pause_requested.set()
        self.download_button.configure(text="Download")
        self.text_1.insert("end", '\n- Pause download -\n\n')

    def resume_download(self):
        self.crawler.pause_requested.clear()
        self.crawler.pause_requested.clear()
        self.download_button.configure(text="Running...")
        self.text_1.insert("end", '\n- Resume download -\n\n')

    def stop_download(self):
        self.crawler.stop_requested.set()
        self.crawler.stop_requested.set()
        self.download_button.configure(text="Download")
        self.text_1.insert("end", '\n- Stop download -\n\n')
        


bg = r'resources\image\bg.png'
tips = r'''
┏━━━━━┓
┃ 使用  指南 ┃
┗━━━━━┛
'''

app = App()
app.mainloop()

# tips = r'''
# ┏━━━━━┓
# ┃ 使用  指南 ┃
# ┗━━━━━┛

# 【图片爬取】

# 1. 填入下载路径

# 2. 填入链接（预览图界面！！！）


# 【PDF编辑】

# 1. 添加PDF：点击 '添加PDF' 
#     增加一个新的PDF文件输入框
#     你可以根据需要添加任意多个

# 2. 在每个PDF文件输入框中：
#     - 文件名：输入你想要合并的PDF文件的完整路径
#     - 删除页码：输入该PDF文件中想删掉的页码，页码之间用空格分开

# 例：PDF文件路径 'E:\download\erohon\sample.pdf'，要删除第2页和第9页
# - 文件名：path/to/your/sample.pdf
# - 删除页码：2 9

# 3. 合并PDFs：点击 '合并PDFs' 按钮开始合并文件，
#     合并后的PDF文件会被命名为 'merged.pdf'，并保存在和此脚本相同的目录下

# 4. 如果你想要删除一个PDF文件输入框，点击页码删除字段旁边的 'x' 按钮
# '''