# JetinMediaPipe
一个用谷歌机器学习算法MediaPipe识别人体姿势并用来控制GTA：SA鹞式战斗机飞行的代码
----
> Author：`尹思博`

> E-mail：`2080768380@qq.com`

> Date：`2022-11-13`

> Description：use the camera on the Laptop Computer to control jet in *GTA: San Andreas* on windows

## 写在前面
本项目是 (https://github.com/DIYer22/jetInKinect) 的翻新版。由于python2.7已停止维护且Kinect xbox 360停产，所以原来的代码已经过时。原项目的语音控制部分日后有时间会更新。

## 操作说明

### 身体骨骼控制部分

MediaPipe Pose中的地标模型预测了33个Pose地标的位置

![](../img/Snipaste_2022-11-15_18-41-21.png)

节点与节点间生成以下向量
> * shoulderElhowLeft:左大臂向量
> * shoulderElhowRight:右大臂向量
> * elbowWristleft:左小臂向量
> * elbowWristRight:右小臂向量
> * shoulderVector:肩膀向量
> * elbowVector:两肘关节相连的向量
> * hipKneeLeft:左大腿向量
> * hipKneeRight:右大腿向量



1. 默认状态
> ![](../img/null.jpg)
> * `动作`：人面向电脑镜头竖直战立，两大臂自然贴身，小臂提到腰间，略微张开
> * `原理`：无
>* `映射按键`：无
>* `功能`：默认状态

2. 垂直起飞
> ![](../img/w.jpg)
> * `动作`：两臂抬起，使之尽量与肩膀齐平
> * `原理`：计算shoulderElhowLeft 和 shoulderElhowRight的夹角 大于100°则垂直起飞
>* `映射按键`：`W`
>* `功能`：缓慢垂直向上升空

3. 垂直下降
> ![](../img/s.jpg)
> * `动作`：上半身与默认状态保持一致，左腿抬起
> * `原理`：hipKneeLeft与向量(0,0,1)的夹角若大于130°则激发
>* `映射按键`：`S`
>* `功能`：缓慢垂直降落

4. 左倾斜/右倾斜
> ![](../img/a.jpg)
> ![](../img/d.jpg)
> * `动作`：保持左右手肘有较大高度落差
> * `原理`：elbowVector 和 向量(0,1,0)的角度小于75° or 大于105° 则激发
>* `映射按键`：`A/D`
>* `功能`：飞机左倾斜/右倾斜

5. 前倾斜/后倾斜
> ![](../img/up.jpg)
> ![](../img/down.jpg)
> * `动作`：两拳的高度在鼻子以上（同时两大臂的角度不应大于100度）或者髋以下
> * `原理`：拳的纵坐标小于鼻子的或者大于髋的
>* `映射按键`：`up array/down array`
>* `功能`：飞机前倾斜/后倾斜

6. 左旋转/右旋转
> ![](../img/q.jpg)
> ![](../img/e.jpg)
> * `动作`：一个拳的位置不变，另一个放在胸前
> * `原理`：Q(横坐标:左肩>左拳>右肩>右拳)  E(横坐标:左拳>左肩>右拳>右肩)
>* `映射按键`：`Q/E`
>* `功能`：飞机的方向在水平左旋转/右旋转

7. 加速/减速
> ![](../img/8.jpg)
> ![](../img/2.jpg)
> * `动作`：双臂交叉放于胸前/双臂不交叉放于胸前
> * `原理`：8(横坐标:左肩>右拳>左拳>右肩)  2(横坐标:左肩>左拳>右拳>右肩)
>* `映射按键`：`Num8/Num2`
>* `功能`：飞机向前加速/减速

8. 收放起落架
> ![](../img/wheel.jpg)
> * `动作`：上半身与默认状态保持一致，右腿抬起
> * `原理`：hipKneeRight与向量(0,0,1)的夹角若大于130°则激发
>* `映射按键`：`2`
>* `功能`：飞机收放起落架


## 一些方法

### 1. 利用三维向量的角度进行体感控制
原理：

求角度公式

![](https://wikimedia.org/api/rest_v1/media/math/render/svg/aa297bd1bcfe5341f8ecf0a69b90984bd9e353d0)

代码：
```python
def degreeOfVictor(a, b):  
    dotab = a.x * b.x + a.y * b.y + a.z * b.z
    modulea = (a.x ** 2 + a.y ** 2 + a.z ** 2) ** 0.5
    moduleb = (b.x ** 2 + b.y ** 2 + b.z ** 2) ** 0.5
    cosab = dotab / modulea / moduleb
    degree = math.degrees(math.acos(cosab))
    return degree
 ```



## 安装指导

1. 一个自带摄像头的电脑
2. 使用命令 `pip install -r requirements.txt` 安装所需要的包
3. 由于pykeyboard 库是跨跨跨平台支持的，需要同时安装多个附加库才能够使用。参照这篇文章再下载几个轮子。https://juejin.cn/post/7107436185433636877
4. 安装游戏*GTA: San Andreas*
5. 运行游戏 `gta_sa.exe`  在设置中的载具按键设置处 设置一下按键映射
原按键与新按键的映射为
```
{
        'up':'T',
        'down':'U',
        '2':Num1
}
```
 结果如下图
![](../img/GTA_%20San%20Andreas%202022_11_15%2019_38_02.png)

最后，使用命令 `python eye.py` 等待电脑摄像头亮起即可开始操作飞机


## 注意事项

1. 对于新手来说 就算用手柄来控制GTA中的鹞式战斗机也非常困难，所以 用身体来控制需要一定的适应期(而且有时候按W键飞机并不是垂直起飞，原因暂时不明)

2. 还有就是键盘问题。一定要下载一个英文键盘，这样进入游戏就不会收到shift键的困扰了。（之前用中文键盘的英文模式时进入游戏人物会经常跳）


## 参考
1. [MediaPipe Pose] (https://google.github.io/mediapipe/solutions/pose#python-solution-api)
2. [Pykeyboard库的使用] (https://blog.csdn.net/weixin_51802807/article/details/121179861?ops_request_misc=&request_id=&biz_id=102&utm_term=pykeyboard%E6%A3%80%E6%B5%8B%E9%94%AE%E7%9B%98%E8%BE%93%E5%85%A5&utm_medium=distribute.pc_search_result.none-task-blog-2~all~sobaiduweb~default-7-121179861.142^v63^control,201^v3^add_ask,213^v2^t3_control1&spm=1018.2226.3001.4187)
