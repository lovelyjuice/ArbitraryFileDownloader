这是一个任意文件下载漏洞的批量利用脚本，在批量下载网站源码的同时能够保持源码的目录结构，使用方法如下：

1. 寻找到一个任意文件下载漏洞，例如 `http://www.test.com/admin/down.php?file=../index.php`，其中 *index.php* 是网站首页php文件。
2. 在`config.py`文件中添加配置，具体配置信息在`config.py`中有说明。
3. 使用BurpSuite爬取网站，在SiteMap中复制网站的所有URL（右键 - *Copy URLs in this host*），并把这些网址粘贴到`urls.txt`文件中，脚本运行时会自动对这些URL去参数去重。
4. 运行`download.py`，会在该文件的上级目录（注意是**上级目录**不是**同级目录**）生成以网站名命名的文件夹，下载的网站源码就在这个文件夹里面。

## FAQ
### 如何利用文件包含漏洞下载php源码？如果服务器返回的源码包含在网页中该怎么办？
> 实现`download.py`中的`request_handler`和`response_handler`方法。
