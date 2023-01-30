#打包用pyinstaller test.py --add-data="E:\Anaconda\envs\gesture\Lib\site-packages\mediapipe\modules;\mediapipe\modules" -F -w
import cv2
import mediapipe as mp
from ctypes import cast,POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities,IAudioEndpointVolume
import math
import numpy as np

class volume:
    #初始化mediapipe
    def __init__(self):
        self.mphands = mp.solutions.hands #mediapipe手部关键点检测的方法
        self.hands = self.mphands.Hands()
        self.mpDraw = mp.solutions.drawing_utils #绘制手部关键点的连线的方法
        self.pointStyle = self.mpDraw.DrawingSpec(color=(0, 0, 255), thickness=3)  # 点的样式
        self.lineStyle = self.mpDraw.DrawingSpec(color=(0, 255, 0), thickness=4)  # 线的样式
        #获得电脑的音量,(反正就这么写)
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(
            IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        self.volume = cast(interface, POINTER(IAudioEndpointVolume))
        self.volume.SetMute(0,None)
        self.volRange = self.volume.GetVolumeRange()

     #主函数
    def gesture(self):
        cap = cv2.VideoCapture(0)
        resize_w = 640
        resize_h = 480
        while cap.isOpened():
            red,img = cap.read()
            if red:
                imgRGB = cv2.cvtColor(img,cv2.COLOR_BGR2RGB) #把BGR转换为RGB
                result = self.hands.process(imgRGB)
                if result.multi_hand_landmarks:  #判断是否检测到手
                    for handLms in result.multi_hand_landmarks:  # 获得手的坐标，线，画出来
                        self.mpDraw.draw_landmarks(img, handLms, self.mphands.HAND_CONNECTIONS, self.pointStyle, self.lineStyle) #把关键点连起来
                        #拇指的坐标
                        p4_x = math.ceil(handLms.landmark[4].x * resize_w) #向上取整
                        p4_y = math.ceil(handLms.landmark[4].y * resize_h)
                        landmarks_p4 = (p4_x,p4_y)
                        #食指的坐标
                        p8_x = math.ceil(handLms.landmark[8].x * resize_w)
                        p8_y = math.ceil(handLms.landmark[8].y * resize_h)
                        landmarks_p8 = (p8_x,p8_y)
                        #中间点
                        middle_point_x = ((p4_x+p8_x)//2)
                        middle_point_y = ((p4_y+p8_y)//2)
                        landmarks_middle = (middle_point_x,middle_point_y)
                        #拇指和食指的样式
                        img = cv2.circle(img,landmarks_p4,10,(255,0,255),cv2.FILLED)
                        img = cv2.circle(img,landmarks_p8,10,(255,0,255),cv2.FILLED)
                        img = cv2.circle(img,landmarks_middle,10,(255,0,255),cv2.FILLED)
                        #拇指和食指连线
                        img = cv2.line(img,landmarks_p4,landmarks_p8,(255,0,255),5)
                        #计算长度
                        line_len = pow(pow(p4_x-p8_x,2)+pow(p4_y-p8_y,2),0.5)
                        print(line_len)
                        #获得电脑音量
                        min_volume = self.volRange[0]
                        max_volume = self.volRange[1]
                        #把长度映射到音量上
                        vol = np.interp(line_len,[10,200],[min_volume,max_volume])
                        #设置电脑音量
                        self.volume.SetMasterVolumeLevel(vol,None)

                frame = cv2.flip(img, 1)  # 把镜头翻转
                cv2.imshow("video", frame)

            if cv2.waitKey(1) == 27:
                break
control = volume()
control.gesture()


