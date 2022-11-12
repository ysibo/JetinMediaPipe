import cv2
import mediapipe as mp
import math
import numpy as np
import time
from pykeyboard import PyKeyboard


class vector:  # 向量类
    x = 0
    y = 0
    z = 0

    def __init__(self, xx, yy, zz):
        self.x = xx
        self.y = yy
        self.z = zz

#预置一些向量
v0_1_1 = vector(0, -1, -1)
v01_1 = vector(0, 1, -1)
v10_1 = vector(1, 0, -1)
v_10_1 = vector(-1, 0, -1)
v100 = vector(1, 0, 0)
v_100 = vector(-1, 0, 0)
v010 = vector(0, 1, 0)
v001 = vector(0, 0, 1)
v0_10 = vector(0, -1, 0)
v_1_10 = vector(-1, -1, 0)
v1_10 = vector(1, -1, 0)


def degreeOfVictor(a, b):  # 求两向量的夹角
    dotab = a.x * b.x + a.y * b.y + a.z * b.z
    modulea = (a.x ** 2 + a.y ** 2 + a.z ** 2) ** 0.5
    moduleb = (b.x ** 2 + b.y ** 2 + b.z ** 2) ** 0.5
    cosab = dotab / modulea / moduleb
    degree = math.degrees(math.acos(cosab))
    return degree

# 下面的代码主要都是从 https://google.github.io/mediapipe/solutions/pose.html 粘贴过来的，我只做了将获取到的数据保存并使用的工作
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_pose = mp.solutions.pose

# For static images:
IMAGE_FILES = []
BG_COLOR = (192, 192, 192)  # gray
with mp_pose.Pose(
        static_image_mode=True,
        model_complexity=2,
        enable_segmentation=True,
        min_detection_confidence=0.5) as pose:
    for idx, file in enumerate(IMAGE_FILES):
        image = cv2.imread(file)
        image_height, image_width, _ = image.shape
        # Convert the BGR image to RGB before processing.
        results = pose.process(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))

        if not results.pose_landmarks:
            continue
        print(
            f'Nose coordinates: ('
            f'{results.pose_landmarks.landmark[mp_pose.PoseLandmark.NOSE].x * image_width}, '
            f'{results.pose_landmarks.landmark[mp_pose.PoseLandmark.NOSE].y * image_height})'
        )

        annotated_image = image.copy()
        # Draw segmentation on the image.
        # To improve segmentation around boundaries, consider applying a joint
        # bilateral filter to "results.segmentation_mask" with "image".
        condition = np.stack((results.segmentation_mask,) * 3, axis=-1) > 0.1
        bg_image = np.zeros(image.shape, dtype=np.uint8)
        bg_image[:] = BG_COLOR
        annotated_image = np.where(condition, annotated_image, bg_image)
        # Draw pose landmarks on the image.
        mp_drawing.draw_landmarks(
            annotated_image,
            results.pose_landmarks,
            mp_pose.POSE_CONNECTIONS,
            landmark_drawing_spec=mp_drawing_styles.get_default_pose_landmarks_style())
        cv2.imwrite('/tmp/annotated_image' + str(idx) + '.png', annotated_image)
        # Plot pose world landmarks.
        mp_drawing.plot_landmarks(
            results.pose_world_landmarks, mp_pose.POSE_CONNECTIONS)

k = PyKeyboard()

# For webcam input:
cap = cv2.VideoCapture(0)
with mp_pose.Pose(
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5) as pose:
    while cap.isOpened():
        success, image = cap.read()
        if not success:
            print("Ignoring empty camera frame.")
            # If loading a video, use 'break' instead of 'continue'.
            continue

        # To improve performance, optionally mark the image as not writeable to
        # pass by reference.
        image.flags.writeable = False
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = pose.process(image)

        # Draw the pose annotation on the image.
        image.flags.writeable = True
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        mp_drawing.draw_landmarks(
            image,
            results.pose_landmarks,
            mp_pose.POSE_CONNECTIONS,
            landmark_drawing_spec=mp_drawing_styles.get_default_pose_landmarks_style())

        if results.pose_landmarks:
            # 将pose_landmarks中的数据都保存到字典d中
            d = {}
            for index, landmarks in enumerate(results.pose_landmarks.landmark):
                l = [landmarks.x, landmarks.y, landmarks.z]
                d[index] = l

            time.sleep(0.05)
            # 求各个向量及其夹角
            shoulderElhowLeft = vector(d[13][0] - d[11][0], d[13][1] - d[11][1], d[13][2] - d[11][2])   # 左大臂向量
            shoulderElhowRight = vector(d[14][0] - d[12][0], d[14][1] - d[12][1], d[14][2] - d[12][2])  # 右大臂向量
            elbowWristleft = vector(d[15][0] - d[13][0], d[15][1] - d[13][1], d[15][2] - d[13][2])      # 左小臂向量
            elbowWristRight = vector(d[16][0] - d[14][0], d[16][1] - d[14][1], d[16][2] - d[14][2])     # 右小臂向量
            shoulderVector = vector(d[12][0] - d[11][0], d[12][1] - d[11][1], d[12][2] - d[11][2])      # 肩膀向量
            if (degreeOfVictor(shoulderElhowLeft, shoulderElhowRight) >= 100 and d[17][1] >= d[0][1]):
                k.press_key('W')
            else:
                k.release_key('W')

            elbowVector = vector(d[13][0] - d[14][0], d[13][1] - d[14][1], d[13][2] - d[14][2])  # 两肘关节相连的向量
            if (degreeOfVictor(elbowVector, v010) < 75):
                k.press_key('D')
            elif (degreeOfVictor(elbowVector, v010) > 105):
                k.press_key('A')
            else:
                k.release_key('A')
                k.release_key('D')

            hipKneeLeft = vector(d[25][0] - d[23][0], d[25][1] - d[23][1], d[25][2] - d[23][2])     # 左大腿向量
            hipKneeRight = vector(d[26][0] - d[24][0], d[26][1] - d[24][1], d[26][2] - d[24][2])    # 右大腿向量
            if ((degreeOfVictor(hipKneeLeft, v001)) > 130):
                k.press_key('S')
            else:
                k.release_key('S')

            if (d[17][0] > d[11][0] and d[11][0] > d[18][0] and d[18][0] > d[12][0]):
                k.press_key('E')
            else:
                k.release_key('E')

            if (d[11][0] > d[17][0] and d[17][0] > d[12][0] and d[12][0] > d[18][0]):
                k.press_key('Q')
            else:
                k.release_key('Q')

            if (d[11][0] > d[18][0] and d[18][0] > d[17][0] and d[17][0] > d[12][0]):
                k.press_key(k.numpad_keys[8])
            else:
                k.release_key(k.numpad_keys[8])

            if (d[11][0] > d[17][0] and d[17][0] > d[18][0] and d[18][0] > d[12][0]):
                k.press_key(k.numpad_keys[2])
            else:
                k.release_key(k.numpad_keys[2])

            if (d[17][1] < d[0][1]):
                k.press_key('T')
            else:
                k.release_key('T')

            if (d[17][1] > d[23][1] and d[17][1] < d[25][1]):
                k.press_key('U')
            else:
                k.release_key('U')

            if ((degreeOfVictor(hipKneeRight, v001)) > 140):
                k.press_key(k.numpad_keys[1])
            else:
                k.release_key(k.numpad_keys[1])

        # Flip the image horizontally for a selfie-view display.
        cv2.imshow('MediaPipe Pose', cv2.flip(image, 1))
        if cv2.waitKey(5) & 0xFF == 27:
            break
cap.release()
