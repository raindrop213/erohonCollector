import os
import re
from PIL import Image, ImageTk
from pypdf import PdfWriter, PdfReader
import tkinter as tk
from tkinter import filedialog


############
## 输出PDF ##
#############

def extract_number(s):  # 识别文件名前面的数字排序
    number = re.search(r'\d+', s)
    return int(number.group()) if number else None


def list_sort(image_folder, pic_ext=['.jpg', '.png']):  # 选取对应格式并且排序

    '''
    一般扒下来的图片命名和格式都是数字名加jpg或者png，所以出现错误的文件需要报告出来！
    然后把图片文件给排序，得到一个列表。
    '''

    # 拆分文件名和扩展名
    tuple_list = [os.path.splitext(file) for file in os.listdir(image_folder)]

    # 非对应格式的文件
    valid_files = []
    invalid_format_files = []
    for file in tuple_list:
        if file[1] in pic_ext:
            valid_files.append(file)
        else:
            invalid_format_files.append(file)

    # 从文件名中提取第一个数字并排序
    valid_files_sorted = sorted(valid_files, key=lambda x: extract_number(x[0]))

    # 用非数字字符标识文件
    non_digit_files = [file for file in valid_files if not file[0].isdigit()]

    # 组合文件名和扩展名
    valid_files_sorted = ["".join(file) for file in valid_files_sorted]
    non_digit_files = ["".join(file) for file in non_digit_files]
    invalid_format_files = ["".join(file) for file in invalid_format_files]

    # 报告不符合格式的文件
    if non_digit_files != []:
        print('\033[31m', "Files with non-digit characters:", non_digit_files, '\033[31m')
    if invalid_format_files != []:
        print('\033[31m',"Files with non-picture formats:", invalid_format_files, '\033[31m')

    return valid_files_sorted


def merge_pic(image_folder):  # 文件夹内的图片合并成PDF

    # 统一转换成RGB
    imgs = []
    for i in list_sort(image_folder):
        images = Image.open(os.path.join(image_folder,i))
        images = images.convert("RGB")
        imgs.append(images)

    # 保存为多页 PDF
    imgs[0].save(image_folder + '.pdf', save_all=True, append_images=imgs[1:], quality=95)



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
        self.merge_button = tk.Button(self.entries_frame, text="Merge PDFs", command=self.merge_pdfs)
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

    def merge_pdfs(self):
        output = PdfWriter()
        for _, filename_entry, pages_entry in self.entries:
            filename = filename_entry.get()
            pages = list(map(int, pages_entry.get().split()))
            input_pdf = PdfReader(open(filename, "rb"))
            for i in range(input_pdf.getNumPages()):
                if i not in pages:
                    output.addPage(input_pdf.getPage(i))
        with open("merged.pdf", "wb") as output_pdf:
            output.write(output_pdf)

if __name__ == '__main__':
    bg = r'E:\tinytools\erohon\resources\image\bg.png'
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

    # image_folder = r"E:\tinytools\erohon\1111\Silver.M个人汉化"
    # merge_pdf(image_folder)