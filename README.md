# **使用手册**

### ***- Part A -***

1. URL填写要爬取的网站页面

2. 点击 'Download' 下载；'stop' 终止
    - 访问频率可调，默认0.3秒
    - User-Agent：随机生成和选取一行作为请求头
    - 浏览器打开 https://httpbin.org/user-agent 获取你的User-Agent

### ***- Part B -***

1. 在输入要合成PDF的文件夹路径（例：要删除第2页和第9页）
    - 文件完整路径：E:\download\sample-1.pdf
    - 删除页码：2 9  （页码之间用空格。留空则不删）

2. 合并PDFs：点击 'Merge' 按钮开始合并文件
    - All：全部文件夹的图片合成到一个PDF
    - Single：全部文件夹分别合成各自的PDF

3. 输出设置：
    - 滑动条调整输出PDF的质量
    - 'Pack to folder' 是保存PDF同时是否保存一个合并的文件夹

### ***- 注意事项 -***
- release下载erohon-collector-windows-amd64.zip，解压运行.exe
- 403的话就是被网站拒绝了，请晚点再试吧
- 有时候要登网站验证一下，一般来说浏览器能登了那也就可以爬，验证之后也不行那也没办法了，哪个能用就用哪个吧，有时候用自己的User-Agent容易爬点

### **- 界面 -**
![tips](https://raw.githubusercontent.com/raindrop213/erohon-collector/main/resources/image/preview1.jpg)

![tips](https://raw.githubusercontent.com/raindrop213/erohon-collector/main/resources/image/preview2.jng)

## 你问我具体爬的是什么网站？
在项目主页上src/pic_collector源码里找找吧，不方便多说了o(￣ε￣*) 

# ***to be continue...***