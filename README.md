# JumpAutoJoin

## 说明

本脚本的目的是每天自动登录`jump`APP,同时检查所有抽奖活动，自动参加活动领取抽奖券。

## 使用

### 1. 提取cookie

使用`charle`抓包APP, IOS和Android均可。

选择任意一个请求，查看cookie，如下图所示。保存备用

![image-20210521161217621](https://cdn.jsdelivr.net/gh/zytomorrowPic/PicBed@latest/image-20210521161217621.png)

### 2. 使用脚本 

#### 2.1 本地使用

下载脚本后，可以直接执行脚本使用。

```shell
python run.py --cookie=xxxxxxxxxxxxx
# xxxxxxx 替换为cookie

python run.py --cookie=xxxxxxxxxxxxx --serverKey=zzzzz
# xxxxxxx 替换为cookie,zzzzz替换为server酱的key,可实现自动推送
```

![执行效果](https://cdn.jsdelivr.net/gh/zytomorrowPic/PicBed@latest/image-20210521163008490.png)

![执行结果](https://cdn.jsdelivr.net/gh/zytomorrowPic/PicBed@latest/image-20210521163139898.png)

#### 2.2 github actions自动运行

脚本配置了github actions，配置好`setting/Secrets`后自动在每天晚上凌晨2点运行。

`变量名需要保持和下图一致。`

![image-20210521162418432](https://cdn.jsdelivr.net/gh/zytomorrowPic/PicBed@latest/image-20210521162418432.png)

![server酱推送效果](https://cdn.jsdelivr.net/gh/zytomorrowPic/PicBed@latest/image-20210521163353244.png)