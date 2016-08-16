# 休息吧，程序员
项目的详细分析请移步我的博客交流：http://blog.csdn.net/Jacketinsysu/article/details/52226229

## 功能介绍
relax_please.py（中文意思是，休息吧！程序猿），是一个运行在**ubuntu**上（其它平台还没测试过，估计只要能装nofity-send的都行）的提醒脚本，根据你设定的参数，利用nofity-send这个库来向桌面发送消息提醒你应该休息了！目前有两部分的逻辑：
1. 持续工作超过1小时（默认），则会提醒要停下来休息；
2. 晚睡，超过23点（默认）还没睡，就会提示你要早点睡。


## 实现逻辑
这个功能主要有四大块：
1. 监测使用者的工作状态，是通过监测按键输入来判断持续工作的时间的，值得注意的是，我在程序里认为，如果没有休息够最少的休息时间，就认为是在持续工作；
2. 监测模块发生事件（比如发现你过度工作了），需要有一个机制来使得通知模块能够获知这个事件，这是经典的观察者模型，所以我用简单的观察者模式来实现了，将接口抽象为一个Listener基类，观察者类和监听者类都依赖接口，这样可以减少整体的耦合性；
3. 通知模块如何向桌面发送通知？简单通过python里的os模块发出shell调用就可以了；
4. 有两个监听功能，而每个监听器都是阻塞的，如果同时启动多个监听器？多线程或多进程都行。


## 使用
python脚本得有人去运行，但是如果每次开机都要自己手动去启动的话，那也太失礼了。至于怎么自动化呢，我觉得可以采用将执行脚本的命令加入开机启动。

在ubuntu里可以将脚本放到/etc/init.d/下边，比如写这样一个脚本start_relax.sh：

```sh
sudo python /usr/local/relax_please/relax_please.py
```

使用方法是：
```sh
sudo cp start_relax.sh /etc/init.d/start_relax
sudo update-rc.d start_relax defaults 95
```

卸载开机自启动的指令是：
```sh
sudo update-rc.d -f start_relax remove
```

但是，由于开机自启的原因，nofity-send发送的泡泡弹窗没有被发送到桌面来。。

试了在shell调用、python调用的时候设置环境变量DISPLAY=:0.0，但是都没有用，而从每次发通知写文件来观察，进程确实是有在运行的，只是没能把通知发到桌面而已。

也就是现在的做法还是只能手动在shell里开启脚本：

```sh
sudo python relax_please.py
```