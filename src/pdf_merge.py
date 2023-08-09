import os
import re
from PIL import Image

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

    def _save_images(self, images):
        folder_name = os.path.splitext(self.file_path)[0]
        os.makedirs(folder_name, exist_ok=True)
        for i, img in enumerate(images):
            img_path = os.path.join(folder_name, f"{i+1}.jpg")
            # 转换图像为RGB模式，如果已经是RGB模式则不会有任何影响
            img = img.convert('RGB')
            img.save(img_path, 'JPEG')

    def merge(self):
        all_images = []
        for path in self.paths:
            foldername = path["file_path"]
            pages_to_delete = path["pages_to_delete"]
            if os.path.isdir(foldername):
                images = [img for i, img in enumerate(sorted(os.listdir(foldername), key=self.sort_key)) if (img.endswith('.jpg') or img.endswith('.png')) and i+1 not in pages_to_delete]
                images = [Image.open(os.path.join(foldername, img)) for img in images]
                if not self.merge_all:
                    images[0].save(os.path.join(self.file_path, f'{os.path.basename(foldername)}.pdf'),  quality=95, resolution=100, save_all=True, append_images=images[1:])
                all_images.extend(images)

        if self.merge_all:
            all_images[0].save(self.file_path,  quality=self.quality, resolution=100, save_all=True, append_images=all_images[1:])
            if self.save_images:
                self._save_images(all_images)


if __name__ == '__main__':

    # 测试功能

    paths = [
        {'file_path': 'E:/mypj/tinytools/erohon-collector/download/[Silver.M]1', 'pages_to_delete': [1,2,3,4]},
        {'file_path': 'E:/mypj/tinytools/erohon-collector/download/[Silver.M]2', 'pages_to_delete': [2]},
        {'file_path': 'E:/mypj/tinytools/erohon-collector/download/[Silver.M]3', 'pages_to_delete': []},
        ]
    merge_all = True
    file_path = 'download/merge.pdf'
    
    merger = PDFMerger(paths, file_path, merge_all=merge_all, save_images=True)
    merger.merge()




