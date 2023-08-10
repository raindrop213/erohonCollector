# **使用手册**

### ***- Part A -***

1. URL填写要爬取的网站页面

2. 点击 'Download' 下载；'stop' 终止

    访问频率可调，默认0.3秒

    User-Agent随机选取一行作请求头（不懂勿改）

    浏览器打开 https://httpbin.org/user-agent 获取你的User-Agent

### ***- Part B -***

1. 在输入要合成PDF的文件夹路径：
    - 文件夹：输入你想要合并成PDF的图片文件夹路径
    - 删除页码：每个文件夹要删掉的页码，页码之间用空格。留空则不删

    例：PDF文件路径 'E:\download\sample-1.pdf' 要删除第2页和第9页
    - 文件名：path/to/your/sample-1.pdf
    - 删除页码：2 9

2. 合并PDFs：点击 'Merge' 按钮开始合并文件
    - All：全部文件夹的图片合成到一个PDF
    - Single：全部文件夹分别合成各自的PDF

### ***- 注意事项 -***
release下载exe，打开可能有点久，要等差不多5-7秒，正在寻找解决办法。
现在的下载图片有点问题，不要点暂停和停止，等程序跑完吧，不然需要重新打开gui才可以继续下。

如果显示：Error: 'NoneType' object has no attribute 'find_all'。那就是被判断为机器人了，要登网站验证一下，验证之后也不行那也没办法了，只能去爬好爬的网站

### **- 界面 -**
![tips](https://raw.githubusercontent.com/raindrop213/erohon-collector/main/resources/image/preview.png)

## 你问我具体爬的是什么网站？
在src/pic_collector代码里找找吧，不方便多说了o(￣ε￣*) 
 
# ***to be continue...***