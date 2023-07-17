import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
from pdf_editior import PDFEditor


class App:
    def __init__(self, root, bg, tips):
        self.entries = []
        self.root = root
        self.root.minsize(780, 780)  # 设置窗口的最小大小
        self.bg = bg
        self.tips = tips

        # 创建一个Frame来放置左侧的内容
        self.left_frame = tk.Frame(root)
        self.left_frame.pack(side="left", fill="both")

        # 创建一个Frame来放置右侧的内容
        self.right_frame = tk.Frame(root)
        self.right_frame.pack(side="right", fill="both", expand=True)

        # 将所有输入框和按钮放在一个单独的Frame中
        self.entries_frame = tk.Frame(self.left_frame)
        self.entries_frame.pack(side="top")
        
        # 在新的Frame中添加按钮
        self.add_entry_button = tk.Button(self.entries_frame, text="Add PDF", command=self.add_entry)
        self.merge_button = tk.Button(self.entries_frame, text="Merge PDFs", command=self.merge_pdf)
        # 为按钮设置grid布局
        self.add_entry_button.grid(row=0, column=0)
        self.merge_button.grid(row=1000, column=0)  # 为合并按钮设置一个大的行号，这样无论有多少输入框，它都会在最下面


        # 添加半透明的背景图像
        image = Image.open(bg)  # 使用你的背景图像文件名替换"background.jpg"
        image = image.convert("RGBA")
        image = Image.blend(Image.new("RGBA", image.size), image, alpha=0.5)
        self.background_image = ImageTk.PhotoImage(image)
        self.background_label = tk.Label(self.right_frame, image=self.background_image)
        self.background_label.place(x=0, y=0, relwidth=1, relheight=1)

        self.manual_label = tk.Label(self.right_frame, text=tips, image=self.background_image, compound=tk.CENTER, justify=tk.LEFT)  # 设置justify和wraplength
        self.manual_label.place(x=0, y=0, relwidth=1, relheight=1)

        self.add_entry()
        self.add_entry()

    def add_entry(self):
        frame = tk.Frame(self.left_frame)
        frame.pack(side="top")
        tk.Label(frame, text="File Path").grid(row=0, column=0)
        filename_entry = tk.Entry(frame, width=30)
        filename_entry.grid(row=0, column=1, columnspan=2)
        tk.Label(frame, text="Pages Del").grid(row=1, column=0)
        pages_entry = tk.Entry(frame, width=26)
        pages_entry.grid(row=1, column=1)
        delete_button = tk.Button(frame, text=" x ", command=lambda: self.delete_entry(frame))
        delete_button.grid(row=1, column=2)
        self.entries.append((frame, filename_entry, pages_entry))
        # 将新的输入框放在所有已有的输入框的下面
        frame.grid(in_=self.entries_frame, row=len(self.entries), column=0)
        self.root.geometry("")  # 重置窗口大小以适应新的内容

    def delete_entry(self, frame):
        self.entries = [(f, fn, pd) for f, fn, pd in self.entries if f != frame]
        frame.destroy()
        self.root.geometry("")  # 重置窗口大小以适应新的内容

    def merge_pdf(self):
        pdf_editor = PDFEditor()
        paths = []
        for frame, file_entry, pages_entry in self.entries:
            filepath = file_entry.get().strip()
            if filepath:
                pages = pages_entry.get().strip()
                if pages:
                    pages = list(map(int, pages.split()))
                else:
                    pages = []
                paths.append({"file_path": filepath, "pages_to_delete": pages})
        output_file = "merged.pdf"
        pdf_editor.merge_pdfs(paths, output_file)



if __name__ == '__main__':

    bg = r'resources\image\bg.png'
    tips = '''
    使用手册

    1. 添加PDF：点击 '添加PDF' 
       增加一个新的PDF文件输入框，
       你可以根据需要添加任意多个。

    2. 在每个PDF文件输入框中：
        - 文件名：输入你想要合并的PDF文件的完整路径
        - 删除页码：输入该PDF文件中想删掉的页码，页码之间用空格分开

    例：PDF文件路径 'E:\download\erohon\sample.pdf' ，共有10页，要删除第2页和第9页
    - 文件名：path/to/your/sample.pdf
    - 删除页码：2 9

    3. 合并PDFs：点击 '合并PDFs' 按钮开始合并文件，
       合并后的PDF文件会被命名为 'merged.pdf'，并保存在和此脚本相同的目录下。

    4. 如果你想要删除一个PDF文件输入框，点击页码删除字段旁边的 'x' 按钮。
    '''
    root = tk.Tk()
    app = App(root, bg, tips)
    root.mainloop()