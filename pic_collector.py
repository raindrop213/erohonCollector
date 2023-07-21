import os
import json
import time
import random
import requests
import threading
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from fake_useragent import UserAgent


class BasicCrawler:
    def __init__(self,
                 headers_num: int = 7,
                 retries: int = 5,
                 sleep_time: float = 1,
                 random_time: float = 0.5,
                 **kwargs):

        self.headers_list = []
        self.headers_num = headers_num
        self.retries = retries
        self.ua = UserAgent()
        self.sleep_time = sleep_time
        self.random_time = random_time

        self.stop_requested = threading.Event()  # 用于停止线程的标志位
        self.pause_requested = threading.Event()  # 用于暂停线程的标志位

    def generate_headers(self):  # 生成一组headers，偶尔换一换吧
        self.headers_list = [self.ua.random for _ in range(self.headers_num)]
        with open('headers_list.json', 'w') as f:
            json.dump(self.headers_list, f)
        print('Generate headers_list.json')

    def chosen_headers(self):  # 随机选个headers
        with open('headers_list.json', 'r') as f:
            headers_list = json.load(f)
        headers = {'User-Agent': random.choice(headers_list)}
        return headers
    
    def get_lxml(self, url):  # 最多request几次？
        retries = self.retries
        while retries > 0:
            if self.stop_requested.is_set():
                print("Stopping as requested.")
                return
            while self.pause_requested.is_set():
                # 等待暂停请求被取消
                time.sleep(1)
            try:
                headers = self.chosen_headers()
                res = requests.get(url, headers=headers)
                time.sleep(self.sleep_time + random.uniform(0, self.random_time))
                break
            except Exception as e:
                print(f"{url} Error: {e}")
                retries -= 1
                continue
        if retries == 0:
            print(f"Failed to request {url}, giving up.")
        return res

    def download(self, src, filepath):  # 下载对应文件
        try:
            filename = src.split("/")[-1]
            fullpath = os.path.join(filepath, filename)
            if not os.path.exists(filepath):
                os.makedirs(filepath)
            if not os.path.exists(fullpath) or os.path.getsize(fullpath)<1:
                with open(fullpath, "wb") as f:
                    res = self.get_lxml(src)
                    f.write(res.content)
                    print(f"{filename} has been downloaded")
            else:
                print(f"{filename} exists")
        except Exception as e:
            print(f"Failed to download image {filename}. Error: {e}")

    def sanitize_filename(self, filename):  # 文件命名非法字符用空格替换掉
        invalid_chars = '\\/:*?"<>|'
        # 创建一个映射表，该表指定所有非法字符都应被空字符替换
        trans_table = str.maketrans(invalid_chars, ' '*len(invalid_chars))
        # 使用映射表替换非法字符，然后去除额外的空格
        return filename.translate(trans_table).strip()


    # 以下方法针对具体网站爬取

    def get_nhentai(self, url, download_path):  # 爬 nhentai.net 后端图源

        '''
        https://nhentai.net/g/435035/ 【本子主页】
        https://t3.nhentai.net/galleries/2422457/1t.jpg 【预览图】

        https://nhentai.net/g/435035/1/ 【点进去】
        https://i7.nhentai.net/galleries/2422457/1.jpg 【图源】

        思路：
        1.【预览图】文件名 （去掉t）
        2.【图源】的域名
        3. 拼接域名和文件名得到下载链接
        '''
        print(f"[{url}] - strat")
        res = self.get_lxml(url)
        html = res.text
        soup = BeautifulSoup(html, 'lxml')

        # 文件名
        title_elements = soup.find('h1', class_='title').find_all('span')  
        title = ''.join(span.text for span in title_elements)
        title = self.sanitize_filename(title)
        download = os.path.join(download_path, title)

        # 获取文件存储的地址路径
        all_list = soup.find(attrs={"class": "container", "id": "thumbnail-container"})
        href = all_list.find_all("a")
        first_href = urljoin(url, href[0]['href'])
        res = self.get_lxml(first_href)
        html = res.text
        soup = BeautifulSoup(html, 'lxml')
        section = soup.find('section', id='image-container', class_='fit-both')
        image_tag = section.find('img')
        src = image_tag['src']
        src_l = src.rsplit('/', 1)[0]

        # 获取文件名
        all_img = all_list.find_all('img', class_='lazyload')
        for i in all_img:
                src_1 = i['data-src']
                src_2 = "".join(src_1.rsplit("t", 1))
                src_r = src_2.rsplit('/', 1)[-1]
                # 合并成完整地址并下载
                imgurl = src_l + '/' + src_r
                self.download(imgurl, download)

        print(f"[{url}] - done\n")

    def get_ehentai(self, url, download_path):  # 爬 ehentai.to 后端图源

        '''
        https://ehentai.to/g/397083 【本子主页】
        https://cdn.dogehls.xyz/galleries/2176760/1t.jpg 【预览图】

        https://ehentai.to/g/397083/1 【点进去】
        https://cdn.dogehls.xyz/galleries/2176760/1.jpg 【图源】

        思路：
        【预览图】的域名去掉后面的第一个“t”就是【图源】了
        '''
        print(f"[{url}] - strat")
        res = self.get_lxml(url)
        html = res.text
        soup = BeautifulSoup(html, 'lxml')

        # 文件名
        title = soup.find('h1').text
        title = self.sanitize_filename(title)
        download = os.path.join(download_path, title)

        # 获取预览图链接并改成图源链接
        all_list = soup.find(attrs={"class": "container", "id": "thumbnail-container"})
        all_img = all_list.find_all("img")
        for i in all_img:
            src_1 = i['data-src']
            src_2 = src_1.rsplit("t", 1)
            src_3 = "".join(src_2)
            self.download(src_3, download)
        print(f"[{url}] - done\n")

    def batch_process(self, url_list, download_path):  # 批量处理多个链接
        for url in url_list:
            if 'nhentai.net' in url:
                self.get_nhentai(url, download_path)
            elif 'ehentai.to' in url:
                self.get_ehentai(url, download_path)
            else:
                print('Link Error!?')
        print('Completed all missions!')


if __name__ == '__main__':

    # 测试功能

    download_path = r'download'
    url_list = [
        'https://nhentai.net/g/311968',
        'https://ehentai.to/g/397083',
    ]

    manager = BasicCrawler()

    # manager.generate_headers()
    manager.batch_process(url_list, download_path)
    