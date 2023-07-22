
import customtkinter
import threading
from PIL import Image, ImageTk
from pdf_editior import PDFMerger
from pic_collector import BasicCrawler
import sys
import os


class EntryWithLabelAndButtons(customtkinter.CTkFrame):
    def __init__(self, master, label_text, command_add=None, command_remove=None, command_select=None, **kwargs):
        super().__init__(master, **kwargs)
        self.configure(border_width=1)
        self.grid_columnconfigure((0, 2, 4), weight=0)  # buttons don't expand
        self.grid_columnconfigure(1, weight=1)  # entry expands

        self.label = customtkinter.CTkLabel(self, text=label_text)
        self.label.grid(row=0, column=0, padx=(5, 0), pady=5, sticky="w")

        self.entry = customtkinter.CTkEntry(self, border_width=0)
        self.entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew", columnspan=2)

        if command_select:
            self.select_dir_button = customtkinter.CTkButton(self, text="...", width=25, command=command_select)
            self.select_dir_button.grid(row=0, column=2, padx=(0, 5), pady=5, sticky="ew")

        self.add_button = customtkinter.CTkButton(self, text="+", width=25, command=command_add)
        self.add_button.grid(row=0, column=3, padx=(0, 3), pady=5)

        self.remove_button = customtkinter.CTkButton(self, text="-", width=25, command=command_remove)
        self.remove_button.grid(row=0, column=4, padx=(0, 5), pady=5)

    def get(self):
        return self.entry.get()

    def set(self, value):
        self.entry.delete(0, "end")
        self.entry.insert(0, value)


class BlockEntry(customtkinter.CTkScrollableFrame):
    def __init__(self, master, title, create_entry_func):
        super().__init__(master, label_text=title, scrollbar_button_color="gray50")
        self.grid_columnconfigure(0, weight=1)

        self.entries = []
        self.create_entry_func = create_entry_func
        for _ in range(2):
            self.add_entry()

    def add_entry(self):
        entry_row = len(self.entries) + 1

        entry = self.create_entry_func(self, command_add=self.add_entry, command_remove=self.remove_entry)
        entry.grid(row=entry_row, column=0, padx=(0,3), pady=(0,6), sticky="ew")

        self.entries.append(entry)

    def remove_entry(self):
        if len(self.entries) > 1:
            entry_to_remove = self.entries[-1]
            entry_to_remove.grid_forget()
            self.entries.remove(entry_to_remove)

class MainWindow(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        # ... Unchanged code ...

        # Create BlockEntry for websites
        self.website_block = BlockEntry(self, "网址", self.create_website_entry)
        self.website_block.grid(row=0, column=0, padx=(10,5), pady=(10,5), sticky="nsew")

        # Create BlockEntry for paths
        self.path_block = BlockEntry(self, "路径", self.create_path_entry)
        self.path_block.grid(row=1, column=0, padx=(10,5), pady=(5,10), sticky="nsew")

        # ... Unchanged code ...

    def create_website_entry(self, master, **kwargs):
        return EntryWithLabelAndButtons(master, "网址", **kwargs)

    def create_path_entry(self, master, **kwargs):
        return EntryWithLabelAndButtons(master, "路径", command_select=self.select_directory, **kwargs)

    # ... Unchanged code ...

class MainWindow(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        # ... Unchanged code ...

        # Create BlockEntry for websites
        self.website_block = BlockEntry(self, "网址", self.create_website_entry)
        self.website_block.grid(row=0, column=0, padx=(10,5), pady=(10,5), sticky="nsew")

        # Create BlockEntry for paths
        self.path_block = BlockEntry(self, "路径", self.create_path_entry)
        self.path_block.grid(row=1, column=0, padx=(10,5), pady=(5,10), sticky="nsew")

        # ... Unchanged code ...

    # ... Unchanged code ...

    def _get_website(self):
        return [entry.get() for entry in self.website_block.entries]

    def _get_path(self):
        return [entry.get() for entry in self.path_block.entries]

    # ... Unchanged code ...

class MainWindow(customtkinter.CTkTk):
    def __init__(self):
        super().__init__()

        # ... Unchanged code ...

        # Create BlockEntry for websites
        self.website_block = BlockEntry(self, "网址", self.create_website_entry)
        self.website_block.grid(row=0, column=0, padx=(10,5), pady=(10,5), sticky="nsew")

        # Create BlockEntry for paths
        self.path_block = BlockEntry(self, "路径", self.create_path_entry)
        self.path_block.grid(row=1, column=0, padx=(10,5), pady=(5,10), sticky="nsew")

        # ... Unchanged code ...

    # ... Unchanged code ...

    def _get_website(self):
        return [entry.get() for entry in self.website_block.entries]

    def _get_path(self):
        return [entry.get() for entry in self.path_block.entries]

    def _collect_pic(self):
        websites = self._get_website()
        paths = self._get_path()

        # ... Unchanged code ...

    def _merge_pdf(self):
        paths = self._get_path()

        # ... Unchanged code ...
