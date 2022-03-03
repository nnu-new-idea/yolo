import cv2
import numpy as np
import math
import os
from reading import reading

# 工具函数，判断小框是否在大框内
def belong2(small_box,big_box):
    if small_box[0]>big_box[0] and small_box[1]>big_box[1] and small_box[2]<big_box[2] and small_box[3]<big_box[3]:
        return True
    else:
        return False

# 从txt文件中获取电流表和电压表以及对应接线柱框的坐标
def getbox(loc, pos):
    # 读取图片对应的txt文件
    box_list = [loc,0,0]
    boxes = []
    #print(pos)
    for i in pos:
        if i[4] in ['BT','RT']:
            if belong2(i[:4],loc):
                boxes.append(i[:4])
                if i[4] == 'RT':
                    box_list[2] = i[:4]
                else:
                    box_list[1] = i[:4]
    boxes.sort()
    #print(boxes)
    if len(boxes) != 3:
        print('电表接线柱数目不足')
    else:
        #d 相邻接线柱距离，dic旋转前中间接线柱坐标
        d = math.sqrt(((boxes[2][0]+boxes[2][2])//2-(boxes[0][0]+boxes[0][2])//2)**2+((boxes[2][1]+boxes[2][3])//2-(boxes[0][1]+boxes[0][3])//2)**2)//2
        dic = [(boxes[1][0]+boxes[1][2])//2,(boxes[1][1]+boxes[1][3])//2]
    return box_list,d,dic


# 旋转后提取图片
def subimage(image, center, theta, width, height):
    theta *= np.pi / 180  # convert to rad
    v_x = (np.cos(theta), np.sin(theta))
    v_y = (-np.sin(theta), np.cos(theta))
    s_x = center[0] - v_x[0] * (width / 2) - v_y[0] * (height / 2)
    s_y = center[1] - v_x[1] * (width / 2) - v_y[1] * (height / 2)
    mapping = np.array([[v_x[0], v_y[0], s_x],
                        [v_x[1], v_y[1], s_y]])
    return cv2.warpAffine(image, mapping, (width, height), flags=cv2.WARP_INVERSE_MAP, borderMode=cv2.BORDER_REPLICATE)


# 工具函数，用于坐标转换
def calc_center(xmin, ymin, xmax, ymax):
    tx = (xmin + xmax) / 2
    ty = (ymin + ymax) / 2
    w = xmax - xmin
    h = ymax - ymin
    return tx, ty, w, h


# 求角度
def angle(x1, y1, x2, y2):
    dx = x2 - x1
    dy = y2 - y1
    angle = math.atan2(dy, dx)
    angle = int(angle * 180 / math.pi)
    return angle


# 旋转图片并保存电表
def adjust_save(image, box_list, category, size,dic):
    e_box, b_box, r_box = box_list[0], box_list[1], box_list[2]
    ex, ey, w, h = calc_center(e_box[0], e_box[1], e_box[2], e_box[3])
    bx, by, _, _ = calc_center(b_box[0], b_box[1], b_box[2], b_box[3])
    rx, ry, _, _ = calc_center(r_box[0], r_box[1], r_box[2], r_box[3])
    if size != (0, 0):
        w, h = size

    # 算出需要旋转的角度
    theta = angle(bx, by, rx, ry)
    #print(theta)
    ang = theta*math.pi/180
    srx = (dic[0]-ex)*math.cos(ang) + (dic[1]-ey)*math.sin(ang)+ex
    sry = (dic[1]-ey)*math.cos(ang) - (dic[0]-ex)*math.sin(ang)+ey
    new_x = int(srx-ex+83)
    new_y = int(sry-ey+83)
    dic = [new_x,new_y]
    # 将图片旋转后裁剪成电流表或者电压表的图片
    image = subimage(image, center=(ex, ey), theta=theta, width=w, height=h)
    #cv2.imwrite(category+'.jpg',image)
    # 保存在目录中
    return image,dic



def deal(img, pos, category, size=(0,0), ran = [0.6,3]):
    for i in pos:
        if i[4] in category:
            image = img
            # 寻找电流表或电压表的框的坐标以及红黑接线柱的坐标，返回值：[e_box, b_box, r_box]
            box,d,dic = getbox(i[:4],pos)
            # 旋转并保存电流表和电压表的框
            image,dic = adjust_save(image, box[:3], i[4], size,dic)
            if i[4] == category[0]:
                k = 0
                unit = 'A'
            else:
                k = 1
                unit = 'V'
            print(str(reading(int(d+1),dic,image,ran[k]))+unit)

def function(pos,img,ran):
    #pos = [[1316, 548, 1520, 635, 'Switch closed'], [1020, 458, 1189, 630, 'Voltmeter'], [1459, 607, 1479, 627, 'BT'], [1315, 586, 1338, 609, 'RT'], [1395, 607, 1416, 628, 'RT'], [1226, 589, 1247, 609, 'BT'], [1150, 594, 1170, 614, 'RT'], [1449, 472, 1474, 496, 'BT'], [1051, 597, 1071, 617, 'BT'], [789, 596, 809, 618, 'BT'], [870, 597, 891, 617, 'BT'], [858, 459, 1007, 628, 'Ammeter'], [1244, 503, 1270, 528, 'RT'], [786, 479, 806, 500, 'RT'], [969, 596, 988, 616, 'RT'], [1305, 466, 1360, 511, 'Slide'], [1101, 595, 1120, 614, 'RT'], [1402, 504, 1426, 529, 'RT'], [919, 596, 939, 616, 'RT'], [1219, 580, 1343, 621, 'Resistance'], [781, 477, 831, 629, 'Battery']]
    #img = cv2.imread('1.png')
    category = ["Ammeter","Voltmeter"] # 要查找电压表还是电流表的框，电压表则为category[1:]，电流表则为category[:1]
    # 最后一个参数是输出图片的尺寸大小，默认为按照框的大小来，ep：size=(150,150)
    #ran = [0.6,3]
    deal(img,pos, category[:], size=(166, 166),ran = ran)

