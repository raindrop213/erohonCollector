import customtkinter
import threading
from PIL import Image, ImageTk
from pdf_editior import PDFEditor
from pic_collector import BasicCrawler
import sys


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
        for _ in range(2):
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


class TextRedirector(object):
    def __init__(self, widget):
        self.widget = widget

    def write(self, str):
        self.widget.insert("end", str)
        self.widget.see("end")

    def flush(self):
        pass


class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        customtkinter.set_default_color_theme("blue")  # blue dark-blue green
        customtkinter.set_appearance_mode("system")  # dark light system

        self.title("my app")
        self.geometry("400x1000")

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(4, weight=1)


        # Download Images
        self.website_entry_frame = BlockWebsiteEntry(self, title="Download Images")
        self.website_entry_frame.grid(row=0, column=0, padx=10, pady=(10, 5), sticky="nsew", columnspan=2)
        
        self.download_path_entry = DirectoryEntry(self, label_text="Download Path")
        self.download_path_entry.grid(row=1, column=0, padx=(10, 5), pady=(5, 10), sticky="ew")

        self.download_button = customtkinter.CTkButton(self, text="Download", command=self.download_images)
        self.download_button.grid(row=1, column=1, padx=(5, 10), pady=(5, 10), sticky="nse")
        

        # Merge PDFs
        self.path_entry_frame = BlockPathEntry(self, title="Merge PDFs")
        self.path_entry_frame.grid(row=2, column=0, padx=10, pady=(10, 5), sticky="nsew", columnspan=2)

        self.output_path_entry = DirectoryEntry(self, label_text="Output Path")
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

        # 重定向 stdout 和 stderr
        sys.stdout = TextRedirector(self.text_1)
        sys.stderr = TextRedirector(self.text_1)


    def button_callback(self):
        print('You clicked the button!')
        # 引发一个错误，以便演示 stderr 的重定向
        1 / 0

    def button_clear_callback(self):
        self.text_1.delete("0.0", "end")
        # 清空logs记录
    
    def download_images(self):
        self.download_button.configure(text="Running...")
        self.update()
        download_path = self.download_path_entry.get().strip()
        url_list = [entry.get() for entry in self.website_entry_frame.entries if entry.get().strip()]
        if download_path and url_list:
            crawler = BasicCrawler()
            crawler.batch_process(url_list, download_path)
        else:
            print("Please set Download path and URL")
        self.download_button.configure(text="Download")

    def merge_pdf(self):
        self.merge_button.configure(text="Running...")
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
        pdf_editor.merge_pdfs(paths, output_file)
        self.merge_button.configure(text="Merge")


app = App()


thread = threading.Thread(target=app.mainloop())

thread.start()
