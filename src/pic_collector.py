import os
import time
import random
import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from urllib.parse import urljoin


class BasicCrawler:
    def __init__(self,
                 headers_num: int = 7,
                 retries: int = 5,
                 sleep_time: float = 0.5,
                 random_time: float = 0.5,
                 headers_string: str = UserAgent().random,
                 **kwargs):
        self.headers_num = headers_num
        self.retries = retries
        self.sleep_time = sleep_time
        self.random_time = random_time
        self.headers_string = headers_string
        self.progress = {}  # 初始化进度字典
        self.stop_requested = False  # 用于停止线程的标志位

    def get_progress(self):  # 获取进度信息
        return self.progress

    def chosen_headers(self):  # 选择随机的User-Agent
        user_agents_list = [ua.strip() for ua in self.headers_string.strip().split('\n') if ua.strip()]
        headers = {'User-Agent': random.choice(user_agents_list)}
        return headers

    def get_lxml(self, url):
        """发送GET请求到给定的URL，并返回响应。

        :param url: 请求的URL。
        :return: 成功时返回响应对象，失败时返回None。
        """
        retries = self.retries
        while retries > 0:
            if self.stop_requested:
                raise Exception("Already Over!")
            try:
                headers = self.chosen_headers()
                time.sleep(self.sleep_time + random.uniform(0, self.random_time))
                res = requests.get(url, headers=headers)
                if res.status_code != 200:
                    raise Exception(f"Failed to request {url}, status code: {res.status_code}")
                return res
            except Exception as e:
                print(e)
                retries -= 1
        raise Exception(f"Failed to request {url}, giving up.")

    def download(self, src, filepath):
        # 下载对应文件
        filename = src.split("/")[-1]
        fullpath = os.path.join(filepath, filename)
        if not os.path.exists(filepath):
            os.makedirs(filepath)
        if not os.path.exists(fullpath) or os.path.getsize(fullpath) < 1:
            with open(fullpath, "wb") as f:
                res = self.get_lxml(src)
                f.write(res.content)
                print(f"{filename} has been downloaded")
        else:
            print(f"{filename} exists")

    def sanitize_filename(self, filename):
        # 文件命名非法字符用空格替换掉
        invalid_chars = '\\/:*?"<>|'
        # 创建一个映射表，该表指定所有非法字符都应被空字符替换
        trans_table = str.maketrans(invalid_chars, ' ' * len(invalid_chars))
        # 使用映射表替换非法字符，然后去除额外的空格
        return filename.translate(trans_table).strip()


    # 以下提供了针对三个具体网站的爬取方法
    def get_hanime1(self, url, download_path):  # 爬 hanime1.me 后端图源

        '''
        https://hanime1.me/comic/71275 【本子主页】
        https://t.nhentai.net/galleries/2157410/1t.jpg 【预览图】

        https://hanime1.me/comic/71275/1 【点进去】
        https://i.nhentai.net/galleries/2157410/1.jpg 【图源】

        思路：
        1.【预览图】文件名获取（去掉t）
        2.【图源】的域名获取
        3. 拼接域名和文件名得到下载链接
        '''
        res = self.get_lxml(url)
        html = res.text
        soup = BeautifulSoup(html, 'lxml')
        
        # 文件名
        title_elements = soup.find('h3', class_='title comics-metadata-top-row').find_all('span')
        title = ''.join(span.text for span in title_elements)
        title = self.sanitize_filename(title)
        download_full_path = os.path.join(download_path, title)
        print(f"[{title}] - strat\n{download_path}")

        # 获取文件存储的地址路径
        all_list = soup.find(attrs={"class": "comics-panel-margin comics-panel-margin-top comics-panel-padding comics-thumbnail-wrapper comic-rows-wrapper"})
        href = all_list.find_all("a")
        first_html = href[0]['href']
        res = self.get_lxml(first_html)
        html = res.text
        soup = BeautifulSoup(html, 'lxml')
        section = soup.find('img', id='current-page-image')
        src = section['src']
        src_l = src.rsplit('/', 1)[0]

        # 获取文件名
        all_img = all_list.find_all('img')
        for i, img in enumerate(all_img):
            src_1 = img['data-srcset']
            src_2 = "".join(src_1.rsplit("t", 1))
            src_r = src_2.rsplit('/', 1)[-1]
            imgurl = src_l + '/' + src_r  # 合并成完整地址并下载
            self.download(imgurl, download_full_path)
            self.progress[url] = (i + 1) / len(all_img)  # 更新特定 URL 的进度
            print(int(self.progress[url] * 100), end='% | ', flush=True)
        
        print(f"[{title}] - done\n")

    def get_ehentai(self, url, download_path):  # 爬 ehentai.to 后端图源
        '''
        https://ehentai.to/g/397083 【本子主页】
        https://cdn.dogehls.xyz/galleries/2176760/1t.jpg 【预览图】

        https://ehentai.to/g/397083/1 【点进去】
        https://cdn.dogehls.xyz/galleries/2176760/1.jpg 【图源】

        思路：
        【预览图】的域名去掉后面的第一个“t”就是【图源】了
        '''
        res = self.get_lxml(url)
        html = res.text
        soup = BeautifulSoup(html, 'lxml')

        # 文件名
        title = soup.find('h1').text
        title = self.sanitize_filename(title)
        download_full_path = os.path.join(download_path, title)
        print(f"[{title}] - strat\n{download_path}")

        # 获取预览图链接并改成图源链接
        all_list = soup.find(attrs={"class": "container", "id": "thumbnail-container"})
        all_img = all_list.find_all("img")
        for i, img in enumerate(all_img):
            src_1 = img['data-src']
            src_2 = src_1.rsplit("t", 1)
            src_3 = "".join(src_2)
            self.download(src_3, download_full_path)
            self.progress[url] = (i + 1) / len(all_img)  # 更新特定 URL 的进度
            print(int(self.progress[url] * 100), end='% | ', flush=True)

        print(f"[{title}] - done\n")

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
        res = self.get_lxml(url)
        html = res.text
        soup = BeautifulSoup(html, 'lxml')

        # 文件名
        title_elements = soup.find('h1', class_='title').find_all('span')
        title = ''.join(span.text for span in title_elements)
        title = self.sanitize_filename(title)
        download_full_path = os.path.join(download_path, title)
        print(f"[{title}] - strat\n{download_path}")

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
        for i, img in enumerate(all_img):
            src_1 = img['data-src']
            src_2 = "".join(src_1.rsplit("t", 1))
            src_r = src_2.rsplit('/', 1)[-1]
            # 合并成完整地址并下载
            imgurl = src_l + '/' + src_r
            self.download(imgurl, download_full_path)
            self.progress[url] = (i + 1) / len(all_img)  # 更新特定 URL 的进度
            print(int(self.progress[url] * 100), end='% | ', flush=True)
            
        print(f"[{title}] - done\n")

    def batch_process(self, url_list, download_path):  # 批量处理多个链接
        for url in url_list:
            if 'hanime1' in url:
                self.get_hanime1(url, download_path)
            elif 'nhentai' in url:
                self.get_nhentai(url, download_path)
            elif 'ehentai' in url:
                self.get_ehentai(url, download_path)
            else:
                print('Link Error!?')
        print('Completed all missions!', self.progress)


if __name__ == '__main__':  # 测试功能

    '''
    推荐hanime1，比较全
    nhentai和hanime1有时候要验证，不行的话就用浏览器登一下网页，当浏览器能进了爬虫也就可以爬了，如果再不行，我也没办法
    ehentai也挺容易被ban
    如果有开代理的话就换换节点，挺管用的
    '''
    download_path = r'download'
    url_list = [
        'https://hanime1.me/comic/75999',
        'https://ehentai.to/g/397083',
        'https://nhentai.net/g/435035/',
    ]

    manager = BasicCrawler()
    manager.batch_process(url_list, download_path)
