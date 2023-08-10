import os
import re
from PIL import Image
import shutil

class PDFMerger:
    def __init__(self, 
                 paths: list, 
                 file_path: str, 
                 merge_all: bool = True, 
                 quality: int = 95,
                 save_images: bool = False):

        if paths is None or file_path is None:
            raise ValueError("paths and file_path are required parameters.")

        self.paths = paths
        self.file_path = file_path
        self.merge_all = merge_all
        self.quality = quality
        self.save_images = save_images

    def sort_key(self, s):
        return int(re.findall(r'\d+', s)[0])

    def _copy_images(self, images):
        folder_name = os.path.splitext(self.file_path)[0]
        os.makedirs(folder_name, exist_ok=True)
        for i, img_path in enumerate(images):
            new_path = os.path.join(folder_name, f"{i+1}.jpg")
            shutil.copy2(img_path, new_path)

    def merge(self):
        all_images = []
        image_paths = []  # 用于保存原始图像路径
        for path in self.paths:
            foldername = path["file_path"]
            pages_to_delete = path["pages_to_delete"]
            if os.path.isdir(foldername):
                images = [img for i, img in enumerate(sorted(os.listdir(foldername), key=self.sort_key)) if (img.endswith('.jpg') or img.endswith('.png')) and i+1 not in pages_to_delete]
                image_paths.extend([os.path.join(foldername, img) for img in images])
                images = [Image.open(img_path) for img_path in image_paths]
                if not self.merge_all:
                    images[0].save(os.path.join(self.file_path, f'{os.path.basename(foldername)}.pdf'),  quality=self.quality, save_all=True, append_images=images[1:])
                all_images.extend(images)

        if self.merge_all:
            all_images[0].save(self.file_path, quality=self.quality, save_all=True, append_images=all_images[1:])
            if self.save_images:
                self._copy_images(image_paths)  # 使用复制方法

if __name__ == '__main__':  # 测试功能

    paths = [
        {'file_path': r'E:/mypj/tinytools/erohon-collector/download/sample_1', 'pages_to_delete': [1,2,3,4]},
        {'file_path': r'E:/mypj/tinytools/erohon-collector/download/sample_2', 'pages_to_delete': [2]},
        {'file_path': r'E:/mypj/tinytools/erohon-collector/download/sample_3', 'pages_to_delete': []},
        ]
    merge_all = True
    file_path = 'download/merge.pdf'
    
    merger = PDFMerger(paths, file_path, merge_all=merge_all, quality=95, save_images=True)
    merger.merge()
