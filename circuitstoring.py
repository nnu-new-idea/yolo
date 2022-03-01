from component import *
from terminal import *


'''
输入:
（1）导线列表：[[(导线一端元器件名字，接线柱类别)，(导线一端元器件名字，接线柱类别)],[……],……]，如[['battery',0,'slide',1],[……],……]
    关于接线柱类别：
    0->BTerminal_1 ; 1->RTerminal_1 ; 2->RTerminal_2 ; 3->BTerminal_2
    对于只有两个接线柱的元器件：0表示黑色接线柱，1表示红色接线柱
    对于电流表和电压表：0表示黑色接线柱，1表示中间的红色接线柱，2表示右边的红色接线柱
    对于滑动变阻器：0表示左上的黑色接线柱，1表示左下的红色接线柱，2表示右下的红色接线柱，3表示右上的黑色接线柱
（2）开关状态：-1关着，1开着
（3）串联的电池数目
（4）电流表和电压表的量程：0表示连接了中间的红色接线柱，1表示连接了右边的红色接线柱
'''
'''lines = [[('Voltmeter', 'RTerminal_1'), ('Sliding Rheostat', 'RTerminal_1')],
         [('Switch', 'RTerminal_1'), ('Battery', 'RTerminal_1')],
         [('Resistance', 'RTerminal_1'), ('Battery', 'BTerminal_1')],
         [('Sliding Rheostat', 'BTerminal_2'), ('Resistance', 'BTerminal_1')],
         [('Voltmeter', 'BTerminal_1'), ('Switch', 'BTerminal_1')],
         [('Resistance', 'RTerminal_1'), ('Ammeter', 'RTerminal_1')],
         [('Ammeter', 'BTerminal_1'),('Voltmeter', 'RTerminal_1')]]
lines = [[('Battery', 'RTerminal_1'), ('Sliding Rheostat', 'BTerminal_1')],
         [('Switch', 'RTerminal_1'), ('Battery', 'BTerminal_1')],
         [('Switch', 'BTerminal_1'), ('Ammeter', 'RTerminal_2')],
         [('Ammeter', 'BTerminal_1'), ('Resistance', 'BTerminal_1')],
         [('Ammeter', 'BTerminal_1'), ('Voltmeter', 'RTerminal_1')],
         [('Resistance', 'RTerminal_1'), ('Voltmeter', 'BTerminal_1')],
         [('Resistance', 'RTerminal_1'),('Sliding Rheostat', 'RTerminal_2')]]
lines = [[('Switch', 'BTerminal_1'),('Sliding Rheostat', 'RTerminal_2')],
         [('Switch', 'RTerminal_1'), ('Battery', 'RTerminal_1')],
         [('Battery', 'BTerminal_1'), ('Resistance', 'RTerminal_1')],
         [('Resistance', 'BTerminal_1'), ('Voltmeter', 'BTerminal_1')],
         [('Sliding Rheostat', 'BTerminal_2'), ('Ammeter', 'BTerminal_1')],
         [('Ammeter', 'RTerminal_2'), ('Resistance', 'BTerminal_1')],
         [('Resistance', 'RTerminal_1'), ('Voltmeter', 'RTerminal_1')]]'''
'''lines = [[['Switch open', 'BT_1'], ['Sliding Rheostat', 'RT_2']],
         [['Switch open', 'RT_1'], ['Battery', 'RT_1']],
         [['Battery', 'BT_1'], ['Resistance', 'RT_1']],
         [['Resistance', 'BT_1'], ['Voltmeter', 'BT_1']],
         [['Sliding Rheostat', 'BT_2'], ['Ammeter', 'BT_1']],
         [['Ammeter', 'RT_2'], ['Resistance', 'BT_1']],
         [['Resistance', 'RT_1'], ['Voltmeter', 'RT_1']]]'''


# info_cops3 = {'Battery':0,'Switch open':1,'Switch close':1,'Sliding Rheostat':2,'Resistance':3,'Ammeter':4,'Voltmeter':5}
info_cops1 = {'Battery': 0, 'Switch': 1, 'Sliding Rheostat': 2, 'Resistance': 3, 'Ammeter': 4, 'Voltmeter': 5}
info_cops2 = {0: 'Battery', 1: 'Switch', 2: 'Sliding Rheostat', 3: 'Resistance', 4: 'Ammeter', 5: 'Voltmeter'}
# info_tmn = {'BTerminal_1':0,'RTerminal_1':1,'RTerminal_2':2,'BTerminal_2':3}
info_tmn = {'BT_1': 0, 'RT_1': 1, 'RT_2': 2, 'BT_2': 3}


def init(info, cops):
    for i in range(0, len(info)):
        cops.append(Component(info.get(i)))


def add_ter(dot, cop, cops, tmns):
    cops[cop].set_tlist(dot, len(tmns))  # 修改元器件的接线柱索引
    if dot == 0 or dot == 3:
        tmns.append(Terminal(-1, info_cops2.get(cop)))
    else:
        tmns.append(Terminal(1, info_cops2.get(cop)))
    # print("dot="+str(dot)+" cop="+str(cop)+" tmns.len="+str(len(tmns)))


def circuitstoring(lines, b_num, s_of):
    cops = []
    tmns = []
    AMsa = 0
    VOsa = 0
    bv = 3  # 一节电池的电压
    a_sa = [0.6, 3]  # 电流表的两个量程
    v_sa = [3, 15]  # 电压表的两个量程

    # lines, b_num, s_of = distinguish.fun(image_path)
    # lines, b_num, s_of = test3.main(image_path)
    # 初始化元器件类
    init(info_cops2, cops)
    # print(lines)
    for line in lines:
        dot1 = info_tmn.get(line[0][1])
        dot2 = info_tmn.get(line[1][1])
        cop1 = info_cops1.get(line[0][0])
        cop2 = info_cops1.get(line[1][0])

        # print("元器件1=" + line[0][0] + " 接线柱1=" + line[0][1] + " 元器件2=" + line[1][0]+" 接线柱2="+ line[1][1])
        # 将接线柱加入列表
        # 查询是否已经在列表中
        index1 = cops[cop1].get_tlist(dot1)
        # print("index1="+str(index1))
        if index1 == -1:  # 不在列表中，需要加入列表
            add_ter(dot1, cop1, cops, tmns)
            index1 = len(tmns) - 1
        index2 = cops[cop2].get_tlist(dot2)
        # print("index2=" + str(index2))
        if index2 == -1:  # 不在列表中，需要加入列表
            add_ter(dot2, cop2, cops, tmns)
            index2 = len(tmns) - 1
        # 将元器件加入接线柱类的列表中
        tmns[index1].add_c(cop2, index2)
        tmns[index2].add_c(cop1, index1)
        '''
        print("cops:")
        out_cop(cops)
        print("tmns:")
        out_tmns(tmns)'''

    if cops[info_cops1.get('Ammeter')].get_tlist(info_tmn.get('RT_2')) != -1:
        AMsa = 1
    if cops[info_cops1.get('Voltmeter')].get_tlist(info_tmn.get('RT_2')) != -1:
        VOsa = 1
    # 电池的节数存入
    cops[info_cops1.get('Battery')].b_num = b_num
    # 开关的闭合状态
    cops[info_cops1.get('Switch')].onoff = s_of
    # 电流表量程
    cops[info_cops1.get('Ammeter')].AMsa = a_sa[AMsa]
    # 电压表量程
    cops[info_cops1.get('Voltmeter')].VOsa = v_sa[VOsa]

    return cops, tmns


def out_cop(cops, tmns):
    for i in range(0, len(cops)):
        # print(i,end=": ")
        # cops[i].out()
        print("元器件： " + cops[i]._category)
        print("黑色接线柱连接：", end="")
        if cops[i].get_tlist(0) == -1:
            print("无")
        else:
            print("index=" + str(cops[i].get_tlist(0)) + ",元器件：", end="")
            tmns[cops[i].get_tlist(0)].out()
        print("红色色接线柱连接：", end="")
        if cops[i].get_tlist(1) == -1:
            print("无")
        else:
            print("index=" + str(cops[i].get_tlist(1)) + ",元器件：", end="")
            tmns[cops[i].get_tlist(1)].out()
        if i == 2 or i == 4 or i == 5:
            print("红色接线柱连接2：", end="")
            if cops[i].get_tlist(2) == -1:
                print("无")
            else:
                print("index=" + str(cops[i].get_tlist(2)) + ",元器件：", end="")
                tmns[cops[i].get_tlist(2)].out()
        if i == 2:
            print("黑色接线柱连接2：", end="")
            if cops[i].get_tlist(3) == -1:
                print("无")
            else:
                print("index=" + str(cops[i].get_tlist(3)) + ",元器件：", end="")
                tmns[cops[i].get_tlist(3)].out()


def out_tmns(tmns):
    for i in range(0, len(tmns)):
        print(i, end=": ")
        tmns[i].out2()
