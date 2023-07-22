import os
import re
from PIL import Image

class PDFMerger:
    def __init__(self, paths, file_path, merge_all=True):
        self.paths = paths
        self.file_path = file_path
        self.merge_all = merge_all

    def sort_key(self, s):
        return int(re.findall(r'\d+', s)[0])

    def merge(self):
        try:
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
                all_images[0].save(os.path.join(self.file_path,'merge.pdf'),  quality=95, resolution=100, save_all=True, append_images=all_images[1:])
        except Exception as e:
            print(f"Error: {e}")


if __name__ == '__main__':

    # 测试功能

    paths = [
        {"file_path": "download\[Silver.M]1", "pages_to_delete": []},
        {"file_path": "download\[Silver.M]2", "pages_to_delete": []},
        {"file_path": "download\[Silver.M]3", "pages_to_delete": []}
    ]
    file_path = 'download'
    
    merger = PDFMerger(paths, file_path, merge_all=True)
    merger.merge()


# def joinimages(images, quality, resolution):
#     return images[0].save(os.path.join(file_path, f'q{quality} r{resolution}.pdf'),  quality=quality, resolution=resolution, save_all=True, append_images=images[1:])

# all_images[0].save(os.path.join(file_path, 'q95 r-.pdf'), quality=95, save_all=True, append_images=all_images[1:])
# joinimages(all_images, 95, 100)
# joinimages(all_images, 95, 200)
# joinimages(all_images, 95, 300)






