import cv2
import numpy as np

def distance(t1, t2):
    return (t1[0] - t2[0]) ** 2 + (t1[1] - t2[1]) ** 2

# 将BT_1,RT_1和BT_2,RT_2互换
def change_sr(ts):
    ts[0][2] = 'BT_1'
    ts[1][2] = 'RT_1'
    ts[2][2] = 'RT_2'
    ts[3][2] = 'BT_2'

def adjust_sr(pos):
    ts = [0, 0, 0, 0]
    for t in pos:
        if t[2] == 'BT_1':
            if ts[0] == 0:
                ts[0] = t
            else:
                ts[3] = t
        elif ts[1] == 0:
            ts[1] = t
        else:
            ts[2] = t
    # 判断红黑接线柱的数量是否各为2
    for j in ts:
        if j == 0:
            # print(f'{i[4]}红黑接线柱数量有误')
            return -1
    # 将离得近的两个红黑接线柱变为BT_2和RT_2
    ts[3][2] = 'BT_2'
    if distance(ts[0], ts[1]) < distance(ts[0], ts[2]):
        ts[2][2] = 'RT_2'
    else:
        ts[1][2] = 'RT_2'
        ts[1], ts[2] = ts[2], ts[1]
    # 接下来正式进行判断，将正面姿态下滑动变阻器左边的红黑接线柱统一命名为BT_1和RT_1
    b1 = ts[0]
    r1 = ts[1]
    r2 = ts[2]
    b2 = ts[3]
    if b1[0] < r1[0]:
        if b1[1] < r1[1]:
            if b1[1] < b2[1]:
                ts = ts[::-1]
                change_sr(ts)
        else:
            if b1[0] < b2[0]:
                ts = ts[::-1]
                change_sr(ts)
    else:
        if b1[1] < r1[1]:
            if b1[0] > b2[0]:
                ts = ts[::-1]
                change_sr(ts)
        else:
            if b1[1] > b2[1]:
                ts = ts[::-1]
                change_sr(ts)
    return ts


def change_name(components, tmns):
    for i in components:
        # 判断电流表和电压表
        if i[4] == 'Ammeter' or i[4] == 'Voltmeter':
            if len(i) != 8:
                # print(f'{i[4]}接线柱数量为{len(i)-5}，不为3')
                return -1
            ts = [0, 0, 0]
            for j in i[5:]:
                t = tmns[j]            # t:[x1,x2,'BT_1', 'Ammeter']
                if t[2] == 'BT_1':
                    ts[0] = t
                elif ts[1] == 0:
                    ts[1] = t
                else:
                    ts[2] = t
            for j in ts:
                if j == 0:
                    # print(f'{i[4]}红黑接线柱数量有误')
                    return -1
            if distance(ts[0], ts[1]) < distance(ts[0], ts[2]):
                ts[2][2] = 'RT_2'
            else:
                ts[1][2] = 'RT_2'
        # 判断滑动变阻器
        elif i[4] == 'Sliding Rheostat':
            if len(i) != 9:
                # print(f'{i[4]}接线柱数量为{len(i)-5}，不为4')
                return -1
            # 重命名滑动变阻器的名称
            pos = []
            # 先将接线柱存入ts列表
            for j in i[5:]:
                t = tmns[j]  # t:[x1,x2,'BT_1', 'Sliding Rheostat']
                pos.append(t)
            # 修改滑动变阻器接线柱名称
            ts = adjust_sr(pos)
            if ts == -1:
                return -1
        # 判断其他元器件
        elif i[4] != 'Battery' and i[4] != 'Slide':
            if len(i) != 7:
                # print(f'{i[4]}接线柱数量为{len(i) - 5}，不为2')
                return -1

    return 0



def change_battery_color(img, position):
    arr = img.copy()
    # 设置图片修改后图片颜色  这里设置为白色
    colorl = [255, 255, 255]
    # 依次遍历我们需要修改颜色的图片区域
    cx = (position[0] + position[2]) // 2
    cy = (position[1] + position[3]) // 2
    for col in range(cx - 32, cx + 32):
        for row in range(cy - 32, cy + 32):
            arr[row, col] = colorl
    return arr

def segmentation(img):
    Img = img.copy()
    segs = []
    for c in ['red','red2','black']:#判断图片是否读入
        HSV = cv2.cvtColor(Img, cv2.COLOR_BGR2HSV)#把BGR图像转换为HSV格式
        # 以下是红色的
        if c == 'red':
            # 红色有两个区间
            Lower = np.array([146, 43, 46])#要识别颜色的下限
            Upper = np.array([180, 255, 255])#要识别的颜色的上限
            mask = cv2.inRange(HSV, Lower, Upper)
            # red1 = mask
        elif c == 'red2':
            # 区间2
            Lower1 = np.array([0, 43, 46])  # 要识别颜色的下限
            Upper1 = np.array([10, 255, 255])  # 要识别的颜色的上限
            mask = cv2.inRange(HSV, Lower1, Upper1)
            # 跟red1合并
            # for i in range(red1.shape[0]):
            #     for j in range(red1.shape[1]):
            #         if mask[i][j] < red1[i][j]:
            #             mask[i][j] = red1[i][j]


        # 下面是黑色的
        elif c == 'black':
            Lower = np.array([0, 0, 0])#要识别颜色的下限
            Upper = np.array([180,255, 46])#要识别的颜色的上限
            mask = cv2.inRange(HSV, Lower, Upper)
        kernel = np.ones((5,5), np.uint8)
        #图像膨胀处理
        dil = cv2.dilate(mask, kernel,iterations=1)  #iterations未出现时表示此时为1，即一次腐蚀
        #设置卷积核
        kernel2 = np.ones((5,5), np.uint8)
        #图像腐蚀处理
        erosion = cv2.erode(dil, kernel2,iterations=1)  #iterations未出现时表示此时为1，即一次腐蚀
        mask = erosion
        # cv2.imwrite('b_w_img/' + c + 'fname.png', mask)
        # 缩小16倍
        mask1 = cv2.resize(mask, (mask.shape[1] // 2, mask.shape[0] // 2))
        mask1 = cv2.resize(mask1, (mask1.shape[1] // 2, mask1.shape[0] // 2))
        mask1 = cv2.resize(mask1, (mask1.shape[1] // 2, mask1.shape[0] // 2))
        mask2 = cv2.resize(mask1, (mask1.shape[1] // 2, mask1.shape[0] // 2))
        # cv2.imwrite('b_w_img/' + c + 'fname1.png', mask2)
        # 将数值为255的像素点去掉
        for i in range(mask2.shape[0]):
            for j in range(mask2.shape[1]):
                if mask2[i][j] == 255:
                    mask2[i][j] = 0
        # row = mask2.shape[0]
        # col = mask2.shape[1]
        # for i in range(1, row-1):
        #     for j in range(1, col-1):
        #         if mask2[i-1][j] and mask2[i][j-1] and mask2[i+1][j] and mask2[i][j+1]\
        #         and mask2[i-1][j-1] and mask2[i-1][j+1] and mask2[i+1][j-1] and mask2[i+1][j+1]:
        #             mask2[i][j] = 0

        # cv2.imwrite('b_w_img/' + c + 'fname2.png', mask2)
        segs.append(mask2)

    # 将红色区间的图像加在一起
    red1 = segs[0]
    red2 = segs[1]
    for i in range(red1.shape[0]):
        for j in range(red1.shape[1]):
            if red2[i][j] < red1[i][j]:
                red2[i][j] = red1[i][j]
            # else:
            #     red2[i][j] = red1[i][j]
            # if red1[i][j] < mask2[i][j]:
            #     red1[i][j] = mask2[i][j]
    # cv2.imwrite('b_w_img/' + 'total.png', segs[0])
    # cv2.imwrite('b_w_img/' + 'red.png', segs[1])
    # cv2.imwrite('b_w_img/' + 'black.png', segs[2])

    # return [red1, red2, mask2]  # 三张图片分别是整体导线区间，红色导线区间，黑色导线区间
    return segs[1:]

def change_post_color(img, points):
    arr = img.copy()
    # 设置图片修改后图片颜色  这里设置为白色
    rows = len(arr)
    cols = len(arr[0])
    colorl = [255, 255, 255]

    # 依次遍历我们需要修改颜色的图片区域
    for i in points:
        for col in range(max(0, i[0] - 16), min(i[0] + 16, rows + 260)):
            for row in range(max(0, i[1] - 16), min(i[1] + 16, cols + 260)):
                arr[row, col] = colorl
    return arr

# 得到附近九宫格的值，存入列表，下标顺序如下
# 0 1 2
# 3 4 5
# 6 7 8
def get_near_value(row, col, image, r):
    values = []
    one_grid = [-1, 0, 1]
    two_grid = [-2,-1,0,1,2]
    if r == 1:
        for i in one_grid:
            for j in one_grid:
                if 0 <= row+i < image.shape[0] and 0 <= col+j < image.shape[1]:
                    values.append(image[row+i, col+j])
                else:
                    values.append(0)                    # 如果超出边界，则将该位置的值置为0
    elif r == 2:
        for i in two_grid:
            for j in two_grid:
                if i in one_grid and j in one_grid:
                    continue
                if 0 <= row + i < image.shape[0] and 0 <= col + j < image.shape[1]:
                    values.append(image[row+i, col+j])
                else:
                    values.append(0)

    return values

def move(row, col, direction, r):
    k = 0
    one_grid = [-1,0,1]
    two_grid = [-2,-1,0,1,2]
    if r == 1:
        for i in one_grid:
            for j in one_grid:
                if direction == k:
                    return row+i, col+j
                k += 1
    elif r == 2:
        for i in two_grid:
            for j in two_grid:
                if i in one_grid and j in one_grid:
                    continue
                if direction == k:
                    return row+i, col+j
                k += 1



def match(row, col, ts, image):
    one_grid = [0, -1, 1]
    two_grid = [0, -1, 1, -2, 2]
    # 先看附近一格是否有匹配的接线柱
    for i in one_grid:
        for j in one_grid:
            if 0 <= row + i < image.shape[0] and 0 <= col + j < image.shape[1]:  # 未过界才需判断
                if [row+i, col+j] in ts:
                    return ts.index([row+i, col+j])
            else:
                continue
    # 再看附近两格是否有匹配的接线柱
    for i in two_grid:
        for j in two_grid:
            if i in one_grid and j in one_grid:
                continue
            if 0 <= row + i < image.shape[0] and 0 <= col + j < image.shape[1]:
                if [row+i, col+j] in ts:
                    return ts.index([row+i, col+j])
            else:
                continue

    return -1


def find_end(row0, col0, image, ts):
    img = image  # 如果操作完需要将image还原，则需要加上.copy()
    d_min = 20  # 线的最短长度，设为15，每走一步加1或者1.5
    d_max = 40
    d = 0
    row = row0
    col = col0
    # mask用来将来过的方向去掉，比如从0方向来的，则下一步不考虑5，7，8方向
    mask = {0: [5, 7, 8], 1: [6, 7, 8], 2: [3, 6, 7], 3: [2, 5, 8], 4: [4, 4, 4],
            5: [0, 3, 6], 6: [1, 2, 5], 7: [0, 1, 2], 8: [0, 1, 3]}
    # 一开始没有移动，所以初始的方向是4
    direction = 4
    while True:
        img[row, col] = 0
        # 如果线的长度大于给定阈值，判断是否在接线柱附近，如果是则返回接线柱索引值
        if d >= d_min:
            t1_id = match(row, col, ts, img)
            if t1_id >= 0:
                return t1_id
        if d >= d_max:
            break
        # 查找附近九宫格的值，找出前进方向最大的一个
        values = get_near_value(row, col, img, 1)
        if max(values) == 0:
            break
        for i in mask[direction]:
            values[i] = 0
        direction = values.index(max(values))
        if direction % 2 == 0:   # 偶数说明是向斜方向移动，加1.5
            d += 1.5
        else:
            d += 1
        row, col = move(row, col, direction, 1)

    return -1


def find_end1(row, col, image, ts, d):
    img = image  # 如果操作完需要将image还原，则需要加上.copy()
    d_min = 15  # 线的最短长度，设为15，每走一步加1或者1.5
    d_max = 35  # 线的最长长度，设为40，如果超过则返回False
    img[row, col] = 0
    if d > d_max:
        return -1
    if d >= d_min:
        t1_id = match(row, col, ts, image)
        if t1_id >= 0:
            return t1_id
    while True:
        values = get_near_value(row, col, img, 1)
        if max(values) == 0:
            return -1
        direction = values.index(max(values))
        if direction % 2 == 0:   # 偶数说明是向斜方向移动，加1.5
            d1 = d + 1.5
        else:
            d1 = d + 1
        row1, col1 = move(row, col, direction, 1)
        t1_id = find_end1(row1, col1, img, ts, d1)
        if t1_id >= 0:
            return t1_id


def find(tmns, seg_images):
    position = []
    ts = []
    # 将缩小16倍的接线柱坐标按[row, col]的方式存入ts列表
    for i in tmns:
        ts.append([i[1]//16, i[0]//16])
        # seg_images[0][i[1]//16, i[0]//16] = 0
        # seg_images[1][i[1]//16, i[0]//16] = 0
    # 先从接线柱9宫格位置找，再扩大一倍范围找
    for r in range(1, 3):
        # 先从红线开始找，再从黑线开始找
        for image in seg_images:
            for t in ts:
                image[t[0], t[1]] = 0
                # 从附近8个点找线的起始点
                values = get_near_value(t[0], t[1], image, r)
                for i in range(len(values)):
                    if values[i] > 0:
                        row0, col0 = move(t[0], t[1], i, r)  # 将初始点向i方向移动
                        t1_id = find_end1(row0, col0, image, ts, 0)
                        if t1_id >= 0:
                            t_id = ts.index(t)
                            new_pos = [[tmns[t_id][3], tmns[t_id][2]], [tmns[t1_id][3], tmns[t1_id][2]]]
                            if new_pos not in position and new_pos[::-1] not in position and new_pos[0][0] != new_pos[1][0]:
                                position.append(new_pos)   # ep:[['Ammeter','BT_1'],['Resistant','RT_1']
                            if len(position) == 7:
                                return position


    return position


# 将接线柱列表中指定元器件放置于数组前列，优先处理的函数
def sort_priority(values, group):
	def helper(x):
		if x[3] in group:
			return (0,x)
		return(1,x)
	values.sort(key=helper)


def get_info(testpos):
    # testpos, images = RE(image_path)  # testpos:[x1,x2,y1,y2,cops_name]  images:[iamge_path1, image_path2, ...]
    tmns = []
    components = []
    cops = []
    # image = images.copy()        # 图片路径
    batterynum = 0               # 存储电池数量
    key = 0                      # 存储开关状态，1为闭合，-1为断开，初始为0
    for j in testpos:
        centre_x = (j[0] + j[2]) // 2
        centre_y = (j[1] + j[3]) // 2
        if j[4] == 'RT' or j[4] == 'BT':
            tmns.append([centre_x, centre_y, j[4]+'_1']) # 接线柱存入列表，ep:[xt,yt,'RT_1']
        # elif j[4] == 'Slide':
        #     continue
        else:
            if j[4] == 'Battery':
                batterynum += 1
            if j[4] == 'Switch open':
                j[4] = 'Switch'
                key = -1
            if j[4] == 'Switch closed':
                j[4] = 'Switch'
                key = 1
            cops.append([centre_x, centre_y, j[4]])
            components.append(j)   # 元器件存入列表，ep:[x1,x2,y1,y2,'Ammeter']

    return cops, key, batterynum, components, tmns


def check_tmn(components, tmns):
    new_tmns = []
    for j in tmns:
        for k in components:
            if k[0] <= j[0] < k[2] and k[1] <= j[1] <= k[3]:
                new_tmns.append([*j, k[4]])     # j:[xt,yt,'RT_1'],k:[x1,x2,y1,y2,'Ammeter']
                k.append(len(new_tmns)-1)       # k:[x1,x2,y1,y2,'Ammeter',t1_index,t2_index,...]
                break              # 一个接线柱只能判断为一个元器件所有，如果元器件挨得近可能存在误判情况，如果出现误判则在后面逻辑判断的时候丢掉这一帧
    # 检查接线柱是否正确并将接线柱重命名
    ret = change_name(components, new_tmns)
    if ret == -1:
        return None
    return new_tmns

    # 元器件数量不为6则识别错误
    # if len(components) != 6:
    #     print('元器件个数不为6')
    #     return False


def wire_matching(image, tmns):
    # 将接线柱与元器件对应起来, 存放在new_tmns里用于后面的导线两端判断
    # new_tmns = []
    # for j in tmns:
    #     for k in components:
    #         if k[0] <= j[0] < k[2] and k[1] <= j[1] <= k[3]:
    #             new_tmns.append([*j, k[4]])     # j:[xt,yt,'RT_1'],k:[x1,x2,y1,y2,'Ammeter']
    #             k.append(len(new_tmns)-1)  # k:[x1,x2,y1,y2,'Ammeter',t1_index,t2_index,...]
    #             break              # 一个接线柱只能判断为一个元器件所有，如果元器件挨得近可能存在误判情况，如果出现误判则在后面逻辑判断的时候丢掉这一帧
    # # 检查接线柱是否正确并将接线柱重命名
    # ret = change_name(components, new_tmns)
    # if ret == -1:
    #     return False

    # img = cv2.imread(image)

    img = image.copy()
    # 将接线柱涂成白色
    img = change_post_color(img, tmns)
    # 将电池涂成白色
    # for j in components:
    #     if j[4] == 'Battery':
    #         img = change_battery_color(img, j[:4])
    # cv2.imwrite('123124.png', img)
    # 从图片中提取线
    seg_images = segmentation(img)
    # 将电流表和电压表的接线柱置于列表前列，优先处理
    # priority = {'Ammeter', 'Voltmeter'}
    # priority = {'Resistance'}
    # sort_priority(new_tmns, priority)
    # 找出线对应的端点接线柱
    position = find(tmns, seg_images)
    return position


if __name__ == '__main__':
    image_path = 'video/exp_f12.mp4'
    # main(image_path)
    from deal import init_status
    cops_status = init_status()
    from detect import RE
    RE(image_path)
