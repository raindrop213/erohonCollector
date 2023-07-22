import customtkinter
import threading
from PIL import Image, ImageTk
from pdf_editior import PDFMerger
from pic_collector import BasicCrawler
import sys
import os


class WebsiteEntry(customtkinter.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.configure(border_width=1)
        self.grid_columnconfigure((0, 2, 4), weight=0)  # buttons don't expand
        self.grid_columnconfigure(1, weight=1)  # entry expands

        self.label = customtkinter.CTkLabel(self, text="URL")
        self.label.grid(row=0, column=0, padx=(5, 0), pady=5, sticky="w")

        self.entry = customtkinter.CTkEntry(self, border_width=0)
        self.entry.grid(row=0, column=1, columnspan=1, padx=5, pady=5, sticky="ew")

        self.add_button = customtkinter.CTkButton(self, text="+", width=25, command=self.add_entry)
        self.add_button.grid(row=0, column=2, padx=(0, 3), pady=5)

        self.remove_button = customtkinter.CTkButton(self, text="-", width=25, command=self.remove_entry)
        self.remove_button.grid(row=0, column=3, padx=(0, 5), pady=5)

    def get(self):
        return self.entry.get()

    def set(self, value):
        self.entry.delete(0, "end")
        self.entry.insert(0, value)

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


class PathEntry(customtkinter.CTkFrame):
    def __init__(self, master, command_add=None, command_remove=None, **kwargs):
        super().__init__(master, **kwargs)
        self.configure(border_width=1)
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
        for _ in range(2):
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


class DirectoryWebsiteEntry(customtkinter.CTkFrame):
    def __init__(self, master, label_text, **kwargs):
        super().__init__(master, **kwargs)
        self.grid_columnconfigure(1, weight=1)  # entry expands

        self.label = customtkinter.CTkLabel(self, text=label_text)
        self.label.grid(row=0, column=0, padx=5, pady=(5, 0), sticky="e")

        self.entry = customtkinter.CTkEntry(self, border_width=0)
        self.entry.grid(row=1, column=0, columnspan=2, padx=5, pady=(0,5), sticky="ew")
        self.entry.insert(0, "download")

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

class DirectoryPathEntry(customtkinter.CTkFrame):
    def __init__(self, master, label_text, **kwargs):
        super().__init__(master, **kwargs)
        self.grid_columnconfigure(1, weight=1)

        # 用于选择文件或文件夹的按钮
        self.select_button = customtkinter.CTkButton(self, text="...", width=25)
        self.select_button.grid(row=1, column=2, padx=(0, 5), pady=(0,5), sticky="ew")

        # 切换选择文件或文件夹的按钮
        self.segmented_button = customtkinter.CTkSegmentedButton(self, values=["All", "Single"], command=self.segmented_button_callback)
        self.segmented_button.grid(row=0, column=1, padx=(0, 5), pady=5, sticky="ew")
        self.segmented_button.set("All")

        self.label = customtkinter.CTkLabel(self, text=label_text)
        self.label.grid(row=0, column=0, padx=5, pady=(5, 0), sticky="e")

        self.entry = customtkinter.CTkEntry(self, border_width=0)
        self.entry.grid(row=1, column=0, columnspan=2, padx=5, pady=(0,5), sticky="ew")
        self.entry.insert(0, "download/merge.pdf")

    def segmented_button_callback(self, value):
        value_dict = {"All": 'file', "Single": 'dir'}
        selet = value_dict.get(value, "Unknown value")
        print("segmented button clicked:", value_dict.get(value, "Unknown value"))

        if selet == 'file':
            self.entry.delete(0, "end")  # delete all text
            self.entry.insert(0, "download/merge.pdf")
            self.select_button.configure(command=self.select_file)

        if selet == 'dir':
            self.entry.delete(0, "end")  # delete all text
            self.entry.insert(0, "download")
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
        self.geometry("900x1000")

        self.grid_columnconfigure(2, weight=1)
        self.grid_rowconfigure((0, 2, 4), weight=1)

        
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
        
        self.download_path_entry = DirectoryWebsiteEntry(self, label_text="Download Path")
        self.download_path_entry.grid(row=1, column=0, padx=(10, 5), pady=(5, 10), sticky="ew")

        self.download_button = customtkinter.CTkButton(self, text="Download", command=self.download_images)
        self.download_button.grid(row=1, column=1, padx=(5, 10), pady=(5, 10), sticky="nse")


        # Merge PDFs
        self.path_entry_frame = BlockPathEntry(self, title="Merge PDFs")
        self.path_entry_frame.grid(row=2, column=0, padx=10, pady=(10, 5), sticky="nsew", columnspan=2)

        self.output_path_entry = DirectoryPathEntry(self, label_text="Output File")
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
            print(url_list)
            # self.crawler.batch_process(url_list, download_path)
        else:
            print("Please set Download path and URL")
        self.download_button.configure(text="Download")
        self.text_1.insert("end", '\n- Download Images finished-\n\n')
        
    def merge_pdf_in_background(self):
        self.merge_button.configure(text="Running...")
        print('\033[31m' + '- Running merge PDFs... -' + '\033[0m')
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
        print(paths)
        output_file = "merged.pdf"
        output_path = os.path.join(self.output_path_entry.get().strip(), output_file)
        
        # merger = PDFMerger(paths, output_path, merge_all=True)
        # merger.merge()
        self.merge_button.configure(text="Merge")
        self.text_1.insert("end", '\n- Merge PDFs finished -\n\n')


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
        self.download_button.configure(text="Running...")
        self.text_1.insert("end", '\n- Resume download -\n\n')

    def stop_download(self):
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
