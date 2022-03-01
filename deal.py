import circuitstoring
from recognize import get_info, wire_matching, check_tmn, adjust_sr
import series
import drawcircuit
import cv2
from status import *


# 将元器件恢复
def restore(c):
    if len(set(c)) < 2:
        return True
    else:
        return False

# 判断电路是否正确连接
def score_circuit(parallel, series):
    # 先判断并联是否正确
    right = {'Battery', 'Switch', 'Sliding Rheostat', 'Ammeter', '0'}
    if parallel == [[['Voltmeter'], ['Resistance']]] or parallel == [[['Resistance'], ['Voltmeter']]]:
        b = [i for i in series if i in right]
        if len(b) == len(right):
            print('电路连接正确，+10分')
            return 10

    print('电路连接错误')
    return 0

# 判断电流表、电压表是否接入正确
def score_av(sa_a, sa_v, at, vt):
    score = 0
    if at and sa_a == 0.6:
        score += 5
        res_a = '电流表连接正确，+5分'
    elif at is False:
        res_a = '电流表正负极连接错误'
    else:
        res_a = f'电流表量程有误，应为0.6A，实际为{sa_a}A'
    print(res_a)

    if vt and sa_v == 3:
        score += 5
        res_v = '电压表连接正确，+5分'
    elif vt is False:
        res_v = '电压表正负极连接错误'
    else:
        res_v = f'电压表量程有误，应为3V，实际为{sa_v}V'
    print(res_v)

    return score, '\t' + res_a + '\n' + '\t' + res_v + '\n'

# 判断滑动变阻器是否接入正确
def score_sr(sw, slide):
    score = 0
    if sw[0] == 1:
        res = '滑动变阻器接入正确，+5分'
        # 如果接入的是'RT_1'，则寻找'RT_2'的接线柱坐标
        if sw == [1, 0, 1] or sw == [1, 1, 3]:
            slide.near_tmn = 'RT_2'
        # 如果接入的是'RT_2'，则寻找'RT_1'的接线柱坐标
        elif sw == [1, 0, 2] or sw == [1, 2, 3]:
            slide.near_tmn = 'RT_1'
        score += 5
    elif sw[0] == 0:
        res = '滑动变阻器连接错误，短路连接'
    elif sw[0] == 2:
        res = '滑动变阻器连接错误，电阻全部接入'
    print(res)
    return score, '\t'+res+'\n'

# 记录滑变最大阻值位置的接线柱坐标
def record_sr(sw, tmns, slide):
    if sw[0] == 1:
        # 滑片接入阻值最大的位置为，滑动变阻器未接入的红色接线柱附近
        if sw == [1, 0, 1] or sw == [1, 1, 3]:
            # 如果接入的是'RT_1'，则寻找'RT_2'的接线柱坐标
            for t in tmns:
                if t[3] == 'Sliding Rheostat' and t[2] == 'RT_2':
                    slide.tmn_cord = t[:2]
                    break

        elif sw == [1, 0, 2] or sw == [1, 2, 3]:
            # 如果接入的是'RT_2'，则寻找'RT_1'的接线柱坐标
            for t in tmns:
                if t[3] == 'Sliding Rheostat' and t[2] == 'RT_1':
                    slide.tmn_cord = t[:2]
                    break

def near(cord1, cord2):
    if (cord1[0] - cord2[0]) ** 2 + (cord1[1] - cord2[1]) ** 2 <= 2000:
        return True
    else:
        return False

# 查找滑片的相对位置，1为最大，0为最小，-1为未识别
def find_slide_position(slide, components, tmns):
    pos = []
    # t:[xt,yt,'RT_1'], cop:[x1,x2,y1,y2,'Ammeter']
    for cop in components:
        if cop[4] == 'Sliding Rheostat':
            for t in tmns:
                if cop[0] <= t[0] < cop[2] and cop[1] <= t[1] <= cop[3]:
                    pos.append(t)

    tmn_cord = [0, 0]
    if len(pos) == 4:
        ts = adjust_sr(pos)
        if ts == -1:
            print('滑动变阻器红黑接线柱识别有误')
            return -1
        for t in ts:
            if t[2] == slide.near_tmn:
                tmn_cord = t[:2]
                break
        if near(tmn_cord, slide.cord):
            return 1

    return -1

# 判断滑变是否位于最大位置
def score_slide(slide, components, tmns):
    score = 0
    tmn_cord = [0, 0]
    find_slide_position(components, tmns)
    for t in tmns:
        if t[3] == 'Sliding Rheostat' and t[2] == slide.near_tmn:
            tmn_cord = t[:2]
    if near(tmn_cord, slide.cord):
        score += 5
        print('闭合开关前，滑动变阻器滑片位于最大阻值处，+5分')
    else:
        print('闭合开关前，滑动变阻器滑片未位于最大阻值处')

    return score


def score_slide1(slide_cord, position, new_tmns):
    # 滑片接入阻值最大的位置为，滑动变阻器未接入的红色接线柱附近
    rt = None
    tmn_cord = [0, 0]
    score = 0

    # 寻找滑动变阻器接入的红色接线柱
    for i in position:
        if i[0][0] == 'Sliding Rheostat':
            if i[0][1] == 'RT_1' or i[0][1] == 'RT_2':
                rt = i[0][1]
                break
        if i[1][0] == 'Sliding Rheostat':
            if i[1][1] == 'RT_1' or i[1][1] == 'RT_2':
                rt = i[1][1]
                break

    # 如果接入的是'RT_1'，则寻找'RT_2'的接线柱坐标
    if rt and rt == 'RT_1':
        for t in new_tmns:
            if t[3] == 'Sliding Rheostat' and t[2] == 'RT_2':
                tmn_cord = t[:2]
                break
        if near(tmn_cord, slide_cord):
            score += 5
            print('滑片位于电阻阻值最大位置，+5分')
        else:
            print('滑片没有位于电阻阻值最大位置')

    # 如果接入的是'RT_2'，则寻找'RT_1'的接线柱坐标
    elif rt and rt == 'RT_2':
        for t in new_tmns:
            if t[3] == 'Sliding Rheostat' and t[2] == 'RT_1':
                tmn_cord = t[:2]
                break
        if near(tmn_cord, slide_cord):
            score += 5
            print('滑片位于电阻阻值最大位置，+5分')
        else:
            print('滑片没有位于电阻阻值最大位置')

    else:
        print('滑动变阻器接入导线未识别到')

    return score


# 判断滑动变阻器是否接入正确，以及滑片是否处于阻值最大位置(暂时不用)
def score_slide2(sw, slide_cord, new_tmns):
    score = 0
    tmn_cord = [0, 0]
    if sw[0] == 1:
        print('滑动变阻器接入正确，+5分')
        score += 5
        # 滑片接入阻值最大的位置为，滑动变阻器未接入的红色接线柱附近
        if sw == [1, 0, 1] or sw == [1, 1, 3]:
            # 如果接入的是'RT_1'，则寻找'RT_2'的接线柱坐标
            for t in new_tmns:
                if t[3] == 'Sliding Rheostat' and t[2] == 'RT_2':
                    tmn_cord = t[:2]
                    break
            if near(tmn_cord, slide_cord):
                score += 5
                print('滑片位于电阻阻值最大位置，+5分')
            else:
                print('滑片没有位于电阻阻值最大位置')

        elif sw == [1, 0, 2] or sw == [1, 2, 3]:
            # 如果接入的是'RT_2'，则寻找'RT_1'的接线柱坐标
            for t in new_tmns:
                if t[3] == 'Sliding Rheostat' and t[2] == 'RT_1':
                    tmn_cord = t[:2]
                    break
            if near(tmn_cord, slide_cord):
                score += 5
                print('滑片位于电阻阻值最大位置，+5分')
            else:
                print('滑片没有位于电阻阻值最大位置')
    else:
        print('滑动变阻器接入错误')

    return score

grade = 0
step = 0
cops_status = []
move_slide_times = 0
cops_dict = {'Battery':0, 'Slide':1, 'Sliding Rheostat':2, 'Ammeter':3, 'Voltmeter':4, 'Resistance':5, 'Switch':6}
cops_name = ['Battery', 'Slide', 'Sliding Rheostat', 'Ammeter', 'Voltmeter', 'Resistance']

def init_status():
    global cops_status
    # 初始化其他元器件
    for name in cops_name:
        cops_status.append(Status(name))
    # 初始化开关
    cops_status.append(SwitchStatus())
    # 使滑片最大位置的红色接线柱坐标
    cops_status[cops_dict['Slide']].near_tmn = 0

    return cops_status


def save_image(image, s, save_dir):
    save_path = save_dir + '/' + s + '.jpg'
    cv2.imwrite(save_path, image)


def write_result(save_dir, img_name, record):
    filename = save_dir + '/' + img_name[:-4] + '实验记录.txt'
    with open(filename, mode='a', encoding='utf-8') as f:
        f.write(record)


# 假设设计的电路是正确的，加10分，保存记录
def design_circuit(save_dir, img_name):
    record = img_name + '实验打分记录：（总分100）\n'
    record += '一、实验准备：（共15分）\n'
    record += '1、正确设计电路图：\t+10分 / 10分\n'
    write_result(save_dir, img_name, record)
    return 10


def deal_result(im1, pos, img_name, frame, frames, save_dir):
    global grade
    global step
    global cops_status
    global move_slide_times

    cops_cord = [[0,0]] * len(cops_dict)
    # print()
    # print(img_name, frame, '/', frames)
    # cv2.imwrite('video_imgs/'+str(frame)+'.jpg', im1)
    # return
    # 第一步，先得到元器件的位置信息，以及电池个数，开关状态：key==-1为断开；key==1为闭合
    cops, key, batterynum, components, tmns = get_info(pos)

    c = []
    # print('识别的元器件个数为：', len(cops))
    for i in cops:
        c.append(i[2])
        # 得到每个元器件对应的坐标, i:[x1,x2,'Ammeter']
        idx = cops_dict[i[2]]
        cops_cord[idx] = i[:2]

    # 更新各个元器件当前状态
    for i in range(len(cops_status)):
        cops_status[i].update(cops_cord[i])

    # print(c)
    # 设计电路，检查元器件
    if step == 0:
        score = design_circuit(save_dir, img_name)
        if score:
            print('第一步: 设计电路图，+10分')
            # 保存图片
            s = 'step1:设计电路图+10'
            save_image(im1, s, save_dir)

            grade += score
            print('当前的分为: ', grade)
            step += 1
            print()
            print('第二步: 检查元器件: ')


    # 第一步，检查元器件
    if step == 1:
        check_num = 0
        if cops_status[cops_dict['Ammeter']].check_out(im1):
            check_num += 1
        if cops_status[cops_dict['Voltmeter']].check_out(im1):
            check_num += 1
        if check_num == 2:
            print('元器件检查无误，+5分')
            # 保存图片
            sA = 'step2:检查电流表'
            save_image(cops_status[cops_dict['Ammeter']].image, sA, save_dir)
            sV = 'step2:检查电压表'
            save_image(cops_status[cops_dict['Voltmeter']].image, sV, save_dir)
            s = 'step2:元器件检查完毕+5'
            save_image(im1, s, save_dir)
            # 保存结果
            record = '2、检查实验器材是否齐全、检查电压表、电流表的校准：\t+5分 / 5分\n'
            write_result(save_dir, img_name, record)

            grade += 5
            print('当前的分为: ', grade)
            print()
            step += 0.5
            print('第三步，判断连接是否正确(先判断是否所有元器件都被移动): ')
            record = '\n二、电路连接：（共30分）\n'
            write_result(save_dir, img_name, record)
            cops_status[cops_dict['Ammeter']].move_flag = False
            cops_status[cops_dict['Voltmeter']].move_flag = False

    if step == 1.5:
        for i in cops_status:
            if i.move_flag is False:
                break
        else:
            step += 0.5
            print('所有元器件都被移动了, 进行导线判断')

    # 第二步，判断连接是否正确
    if step == 2:
        # 检查元器件数量是否为7（6个元器件加滑片）
        if len(set(c)) == 7:
            # 检查接线柱是否全部匹配
            new_tmns = check_tmn(components, tmns)
            if new_tmns:
                position = wire_matching(im1, new_tmns)

                # 如果识别出7根导线，则判断电路连接状态，并绘制电路图
                if len(position) == 7:
                    # print('识别的导线数量：', len(position))
                    # for i in position:
                    #     print(i)
                    c_cops, c_tmns = circuitstoring.circuitstoring(position, batterynum, key)
                    pcop, pcop2, sw, sa_a, sa_v, sof, bn, vt, at = series.crete_series(c_cops, c_tmns)

                    # 判断电路是否连接正确，若是则加10分
                    score1 = score_circuit(pcop, pcop2)
                    # 保存结果
                    record = f'1、开关断开时正确连接电路：\t+{score1}分 / 10分\n'
                    write_result(save_dir, img_name, record)

                    # 判断电流表、电压表是否连接正确，共10分，接错一个扣5分
                    score2, res = score_av(sa_a, sa_v, at, vt)
                    # 保存结果
                    record = f'2、正确连接电流表、电压表：\t+{score2}分 / 10分\n'
                    record += res
                    write_result(save_dir, img_name, record)

                    # 开关闭合前判断滑动变阻器滑片
                    score3, res = score_sr(sw, cops_status[cops_dict['Slide']])
                    # 保存结果
                    record = f'3、正确连接滑动变阻器：\t+{score3}分 / 5分\n'
                    record += res
                    write_result(save_dir, img_name, record)

                    score = score1 + score2 + score3
                    # 绘制电路图
                    drawcircuit.draw_func(pcop, pcop2, sw, sa_a, sa_v, sof, bn, vt, at, save_dir + '/' +img_name[:-4])
                    s = 'step3:电流连接情况+'+str(score)
                    save_image(im1, s, save_dir)

                    grade += score
                    print('当前的分为: ', grade)
                    print()
                    step += 1
                    print('第四步，闭合开关: ')

    # 第三步，判断开关闭合
    if step == 3:
        if cops_status[cops_dict['Switch']].change_switch(key) == 1:
            if find_slide_position(cops_status[cops_dict['Slide']], components, tmns) == 1:
                print('闭合开关前，滑动变阻器滑片位于最大阻值处，+5分')
                s = 'step4:闭合开关，滑片位于阻值最大处+5'
                grade += 5
                record = '4、闭合电路前滑动变阻器滑片位于电阻最大位置：\t+5分 / 5分\n'
            else:
                print('闭合开关前，滑动变阻器滑片未位于最大阻值处')
                s = 'step4:闭合开关，滑片未位于阻值最大处+0'
                record = '4、闭合电路前滑动变阻器滑片位于电阻最大位置：\t+0分 / 5分\n'
            save_image(im1, s, save_dir)
            write_result(save_dir, img_name, record)
            # ret = wire_matching(im1, components, tmns)
            # if ret:
            #     position, new_tmns = ret
            #     grade += score_slide(slide_cord, position, new_tmns)
            # else:
            #     print('导线识别有误, 无法判断滑片位置')
            print('闭合开关')
            print('当前的分为: ', grade)
            record = '\n三、测量并处理数据：（共45分）：\n'
            write_result(save_dir, img_name, record)
            print()
            step += 1
            print('第五步，移动滑片，测量电流和电压: ')

    # 第四步，移动滑片，每移动一次加15分，最多三次
    if step == 4:
        if 3 <= cops_status[cops_dict['Slide']].move_state <= 4:
            if move_slide_times < 3:
                move_slide_times += 1
                print(f'第{move_slide_times}次移动滑片，测量阻值，+15分')
                s = 'step5:滑动变阻器第+' + str(move_slide_times) + '次移动+15'
                save_image(im1, s, save_dir)
                grade += 15

        # 如果开关断开，则
        if cops_status[cops_dict['Switch']].change_switch(key) == -1:
            record = f'1、闭合开关，通过移动滑动变阻器，从电压表和电流表中读出三组U、I值：\t+{15 * move_slide_times}分 / 45分\n'
            record += '\n四、整理器材：（共10分）\n'
            record += '1、实验完毕断开开关：\t+5分 / 5分\n'
            write_result(save_dir, img_name, record)

            print('开关已断开，+5分')
            s = 'step6:开关断开+5'
            save_image(im1, s, save_dir)
            grade += 5
            print('当前的分为: ', grade)
            print()
            step += 1
            print('第六步，实验结束，拆除电路，将元器件放回原位: ')

    # 第五步，整理电路
    if step == 5:
        reset_num = 0
        for i in cops_status:
            if i.reset():
                reset_num += 1
        if reset_num > 3:
            print('拆除电路，元器件整理完毕，+5分')
            s = 'step7:电路拆除完毕+5'
            save_image(im1, s, save_dir)

            record = '2、拆除电路，清点整理实验器材，恢复到实验的安放状态：\t+5分 / 5分\n'
            write_result(save_dir, img_name, record)
            grade += 5
            print('当前的分为: ', grade)
            print()
            step += 1

    return grade




