import cv2
import numpy as np
import math
def angle(v1, v2):
    dx1 = v1[0]
    dy1 = v1[1]
    dx2 = v2[0]
    dy2 = v2[1]
    angle1 = math.atan2(dy1, dx1)
    angle1 = int(angle1 * 180/math.pi)
    # print(angle1)
    angle2 = math.atan2(dy2, dx2)
    angle2 = int(angle2 * 180/math.pi)
    # print(angle2)
    if angle1*angle2 >= 0:
        included_angle = abs(angle1-angle2)
    else:
        included_angle = abs(angle1) + abs(angle2)
        if included_angle > 180:
            included_angle = 360 - included_angle
    return included_angle

def reading(d,dic,image,ran):
    '''d表示相邻接线柱的像素距离，dic表示中间接线柱的坐标，img表示图片的相对路径，ran表示量程'''
    Lower = np.array([210, 120, 120])#要识别颜色的下限
    Upper = np.array([255, 255, 255])#要识别的颜色的上限
    img = image
    img = cv2.inRange(img, Lower, Upper)
    cv2.imwrite('1.jpg',img)
    num = fun(d,dic,img)
    return (num-10)*(ran/30)

def fun(d,dic,img):
    loc = [dic[0],dic[1]-d]
    l = int(d*1.3)
    datas = [0]*42
    for i in range(dic[0]-d,dic[0]+d):
        for j in range(loc[1]-l,loc[1]):
            if loc[1]-d<j<loc[1]-0.67*d and loc[0]-0.12*d<i<loc[0]+0.12*d:
                continue
            if (j-loc[1])**2+(i-loc[0])**2<(0.7*d)**2 or (j-loc[1])**2+(i-loc[0])**2>d**2:
                continue
            r = img[j][i]
            if r < 10:
                
                ang = angle((i-loc[0],j-loc[1]),(-1,0))
                if 45<=ang<=135:
                    #print(i,j)
                    datas[int((ang-45+1.25)/2.25)]+=1
    print(datas)
    m = datas.index(max(datas))
    for i in range(len(datas)):
        if i>m and datas[i] == datas[m]:
            return i
    return m+1
