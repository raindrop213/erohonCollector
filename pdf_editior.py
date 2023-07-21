import os
import re
from io import BytesIO
from PIL import Image
from pypdf import PdfWriter, PdfReader


class PDFEditor:

    def __init__(self):
        pass

    @staticmethod
    def extract_number(filename):
        '''
        识别文件名前面的数字排序
        '''
        number = re.search(r'\d+', filename)
        return int(number.group()) if number else None

    def sort_files(self, image_folder, pic_ext=['.jpg', '.png']):
        '''
        一般扒下来的图片命名和格式都是数字名加jpg或者png，报告不是标准格式的文件列表
        然后把符合格式的图片文件给排序，得到一个列表。

        non_digit_files：用非数字字符标识文件（不排除掉）
        invalid_format_files：非对应格式的文件（排除掉）
        '''
        tuple_list = [os.path.splitext(file) for file in os.listdir(image_folder)]  # 拆分文件名和扩展名
        valid_files = []  
        invalid_format_files = []
        for file in tuple_list:
            if file[1] in pic_ext:
                valid_files.append(file)
            else:
                invalid_format_files.append(file)

        valid_files_sorted = sorted(valid_files, key=lambda x: self.extract_number(x[0]))
        non_digit_files = [file for file in valid_files if not file[0].isdigit()]
        valid_files_sorted = ["".join(file) for file in valid_files_sorted]
        non_digit_files = ["".join(file) for file in non_digit_files]
        invalid_format_files = ["".join(file) for file in invalid_format_files]

        if non_digit_files != []:
            print('\033[31m', "Files with non-digit characters:", non_digit_files, '\033[31m')
        if invalid_format_files != []:
            print('\033[31m',"Files with non-picture formats:", invalid_format_files, '\033[31m')

        return valid_files_sorted

    def merge_images_to_pdf(self, image_folder):
        '''
        文件夹内的图片合并成PDF
        '''
        imgs = []
        for i in self.sort_files(image_folder):
            images = Image.open(os.path.join(image_folder, i))
            images = images.convert("RGB")
            imgs.append(images)

        output = BytesIO()
        imgs[0].save(output,format='PDF', save_all=True, append_images=imgs[1:], quality=95)
        output.seek(0)
        return PdfReader(output)
        

    def delete_pages(self, file_info):
        '''
        定义一个函数来删除PDF中的特定页
        '''
        file_path = file_info["file_path"]
        pages_to_delete = file_info["pages_to_delete"]
        reader = PdfReader(file_path)
        writer = PdfWriter()

        for page_number in range(len(reader.pages)):
            if page_number not in pages_to_delete:
                writer.add_page(reader.pages[page_number])

        return writer

    def merge_pdfs(self, readers, output):
        '''
        定义一个函数来合并多个PDF
        '''
        writer = PdfWriter()

        for reader in readers:
            for page_number in range(len(reader.pages)):
                writer.add_page(reader.pages[page_number])

        with open(output, 'wb') as out:
            writer.write(out)
    def merge_pdfs(self, readers, output):
        '''
        定义一个函数来合并多个PDF
        '''
        writer = PdfWriter()

        for reader in readers:
            for page_number in range(len(reader.pages)):
                writer.add_page(reader.pages[page_number])

        with open(output, 'wb') as out:
            writer.write(out)


if __name__ == '__main__':

    # 测试功能
    
    pdf_editor = PDFEditor()

    image_folder = "download\[Silver.M]"
    pdf_editor.merge_images_to_pdf(image_folder)

    paths = [
        {"file_path": "download\[Silver.M] - 副本 - 副本.pdf", "pages_to_delete": [0, 4]},
        {"file_path": "download\[Silver.M] - 副本.pdf", "pages_to_delete": [1]},
        {"file_path": "download\[Silver.M].pdf", "pages_to_delete": [2]}
    ]
    pdf_editor.merge_pdfs(paths, output="merged.pdf")
