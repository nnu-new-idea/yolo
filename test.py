import cv2
import numpy as np
import math
import os
from reading import reading

# 工具函数，用于坐标转换
def yolo2box(oneline,Pwidth,Pheight):
    xmin = int(((float(oneline[1])) * Pwidth + 1) - (float(oneline[3])) * 0.5 * Pwidth)
    ymin = int(((float(oneline[2])) * Pheight + 1) - (float(oneline[4])) * 0.5 * Pheight)
    xmax = int(((float(oneline[1])) * Pwidth + 1) + (float(oneline[3])) * 0.5 * Pwidth)
    ymax = int(((float(oneline[2])) * Pheight + 1) + (float(oneline[4])) * 0.5 * Pheight)
    return (xmin,ymin,xmax,ymax)

# 工具函数，判断小框是否在大框内
def belong2(small_box,big_box):
    if small_box[0]>big_box[0] and small_box[1]>big_box[1] and small_box[2]<big_box[2] and small_box[3]<big_box[3]:
        return True
    else:
        return False

# 从txt文件中获取电流表和电压表以及对应接线柱框的坐标
def getbox(name, img, txtPath, category):
    global d,dic
    dic = {'0': "Battery",
           '1': "Switch open",
           '2': "Switch closed",
           '3': "Sliding Rheostat",
           '4': "Resistance",
           '5': "Ammeter",
           '6': "Voltmeter",
           '7': "RT",
           '8': "BT",
           '9': "Slide",
           '10': "A",
           '11': "V"
           }

    Pheight, Pwidth, Pdepth = img.shape
    # 读取图片对应的txt文件
    txtFile = open(txtPath + name[0:-4] + ".txt")
    # 读取txt文件的每行信息
    txtList = txtFile.readlines()
    box_list = []
    # 遍历txt文件每行信息
    for txt in txtList:
        oneline = txt.strip().split(" ")
        # 先找到电流表或者电压表的框
        if dic[oneline[0]] == category:
            e_box = yolo2box(oneline, Pwidth, Pheight)
            r_flag = False
            b_flag = False
            # 再找红黑接线柱的框
            boxes = []
            for j in txtList:
                line = j.strip().split(" ")
                # 寻找黑色接线柱框
                if not b_flag and dic[line[0]] == 'BT':
                    b_box = yolo2box(line, Pwidth, Pheight)
                    # 如果接线柱属于电表，则保存
                    if belong2(b_box, e_box):
                        b_flag = True
                        boxes.append(b_box)

                # 寻找红色接线柱框
                if not r_flag and dic[line[0]] == 'RT':
                    r_box = yolo2box(line, Pwidth, Pheight)
                    if belong2(r_box, e_box):
                        r_flag = True
                        boxes.append(r_box)

            if b_flag and r_flag:
                box_list = [e_box, b_box, r_box]
            boxes.sort()
            if len(boxes) != 3:
                print('电表接线柱数目不足')
            else:
                #d 相邻接线柱距离，dic旋转前中间接线柱坐标
                d = math.sqrt(((boxes[2][0]+boxes[2][2])//2-(boxes[0][0]+boxes[0][2])//2)**2+((boxes[2][1]+boxes[2][3])//2-(boxes[0][1]+boxes[0][3])//2)**2)//2
                dic = [(boxes[1][0]+boxes[1][2])//2,(boxes[1][1]+boxes[1][3])//2]

    return box_list


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
def adjust_save(image, name, box_list, savePath, category, size):
    e_box, b_box, r_box = box_list[0], box_list[1], box_list[2]
    ex, ey, w, h = calc_center(e_box[0], e_box[1], e_box[2], e_box[3])
    bx, by, _, _ = calc_center(b_box[0], b_box[1], b_box[2], b_box[3])
    rx, ry, _, _ = calc_center(r_box[0], r_box[1], r_box[2], r_box[3])
    print(e_box)
    print(b_box)
    print(r_box)
    if size != (0, 0):
        w, h = size

    # 算出需要旋转的角度
    theta = angle(bx, by, rx, ry)
    print(theta)

    srx = (dic[0]-ex)*math.cos(angle) + (dic[1]-ey)*math.sin(angle)+ex
    sry = (dic[1]-ey)*math.cos(angle) - (dic[0]-ex)*math.sin(angle)+ey
    new_x = srx-ex+83
    new_y = sry-ey+83
    dic = [new_x,new_y]
    # 将图片旋转后裁剪成电流表或者电压表的图片
    image = subimage(image, center=(ex, ey), theta=theta, width=w, height=h)
    # 保存在目录中
    cv2.imwrite(savePath + category + name[:-4]+'.jpg', image)



def deal(picPath, txtPath, savePath, category, size=(0,0)):

    files = os.listdir(picPath)
    for i, name in enumerate(files):
        print(i,": ",name)
        image = cv2.imread(picPath + name)

        for j in category:
            # 寻找电流表或电压表的框的坐标以及红黑接线柱的坐标，返回值：[e_box, b_box, r_box]
            box = getbox(name, image, txtPath, j)
            # 旋转并保存电流表和电压表的框
            adjust_save(image, name, box, savePath, j, size)


if __name__ == '__main__':
    picPath = "image/ammeter/"  # 图片所在文件夹路径，后面的/一定要带上
    txtPath = "label/ammeter/"  # txt所在文件夹路径，后面的/一定要带上
    savePath = "result/" # 保存路径，后面的/一定要带上，文件夹需要存在
    category = ["Ammeter","Voltmeter"] # 要查找电压表还是电流表的框，电压表则为category[1:]，电流表则为category[:1]
    # 最后一个参数是输出图片的尺寸大小，默认为按照框的大小来，ep：size=(150,150)
    deal(picPath, txtPath, savePath, category[:], size=(166, 166))

