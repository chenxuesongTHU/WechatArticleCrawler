# WechatArticleCrawler

**通过搜狗搜索对微信公众号文章爬取**
**可能是目前（20200701）对微信公众号文章爬取较少的可行方案**


```python
  python3 sougou_wx_crawler.py --query='搜狗'
```


## 技术路线
1. 扫码登陆微信
2. 通过selenium模拟用户浏览行为点击搜狗微信搜索的每个结果页面
3. 当点击次数过多时会出现验证码，此时将此[验证码识别工具](https://github.com/wkunzhi/Spider-Tools)部署在win server上，进行验证码识别。


## 关键点
1. 理论上可在搜索过程中更改IP proxy来防止触发反爬机制，但是selenium+chorme的组合在更换代理时需要新建一个浏览器（session），就会导致扫码登陆的session失效。保留登录状态浏览器中的cookies来保持登陆状态的方法好像并不可行。或许可以尝试selenium+其他浏览器的方式在爬取过程中动态修改ip代理。如果有系统ip代理的话，可并行执行另一个脚本来动态地修改系统的ip从而避免触发反爬机制。
2. 当爬取数量达到几千条时，会被禁止浏览器访问微信文章，需更换IP或等待IP解封。
3. 如果将[验证码识别工具](https://github.com/wkunzhi/Spider-Tools)部署在server上有大概率会出现网络传输问题，因此尽量爬取代码和[验证码识别工具](https://github.com/wkunzhi/Spider-Tools)在同一台机器上运行可提高效率。
4. 爬取代码对鼠标键盘进行操作，如果在PC上运行，应注意冲突。建议单台电脑运行3个及以下线程。


作者微信: chenxuesong1128
