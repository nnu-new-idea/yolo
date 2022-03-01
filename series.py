from circuitstoring import *
import numpy as np

def swt(cops):
    cop = cops[info_cops1.get('Sliding Rheostat')]
    res = []
    res0 = [1, -1, -1, 1]
    res1_1 = [1, 1, -1, -1]
    res1_2 = [-1, -1, 1, 1]
    res1_3 = [1, -1, 1, -1]
    res1_4 = [-1, 1, -1, 1]
    res2 = [-1, 1, 1, -1]
    tlist = [-1, -1, -1, -1]
    for i in range(0, len(cop._t_list)):
        if cop._t_list[i] != -1:
            tlist[i] = 1
    if tlist == res0:
        res = [0, 0, 3]
    else:
        if tlist == res1_1:
            res = [1, 0, 1]
        else:
            if tlist == res1_2:
                res = [1, 2, 3]
            else:
                if tlist == res2:
                    res = [2, 1, 2]
                else:
                    if tlist == res1_3:
                        res = [1, 0, 2]
                    else:
                        if tlist == res1_4:
                            res = [1, 1, 3]
                        else:
                            res.append(3)
                            for i in range(0, len(cop._t_list)):
                                if cop._t_list[i] != -1:
                                    res.append(i)
    return res


def generate_graph(graph,index,end,cindex,visited):
    cop = info_cops1[tmns[index].belong()]
    if index == end:
        graph[cindex][cop] = 1
        return graph

    # 先判断电流是否能从该接线柱流出，如果能则说明不经过当前元器件
    for i in tmns[index].next_list():
        # 判断是否是上一个元器件的接线柱，避免回流
        if info_cops1[tmns[i].belong()] != cindex:
            graph = generate_graph(graph, i, end, cindex, visited)

    # 当前接线柱所有路径
    visited[index] = 1
    # 跨越元器件，把有向图中上一个元器件到当前元器件的权值置为1
    graph[cindex][cop] = 1
    # 遍历当前元器件下一个接线柱
    for i in cops[cop].t_list():
        if i != -1 and i != index and visited[i] == 0:
            graph = generate_graph(graph, i, end, cop, visited)

    return graph

def crete_series(cops, tmns):
    # 调用了circuitstoring中的函数
    # init(info_cops2)
    # cops, tmns = circuitstoring(image_path)
    '''
    增加功能：滑动变阻器是否正确连接；电流表、电压表正负极、量程
    返回值：
    （1）电路连接情况，分为一个主电路pcop2和并联列表pcop，主电路形式为[B,A,S,0,SW]，数字表示当前碰到并联情况并且为并联列表中的索引，并联列表为[ [[R],[V]] ]
    （2）滑动变阻器的连接情况元组sw=[0,1,2]，第一个数字表示滑动变阻器是正常连接（接线柱一上一下）——>1；或者是短路（同下）——>0；或者是全部接入（同上）——>2；其他——>3。后面两个数字表示接线柱
    （3）电流表的量程sa_a（单位为A）
    （4）电压表的量程sa_V（单位为V）
    （5）电压表接线柱是否连接正确vt=False/True
    （6）电流表接线柱是是否连接正确at=False/True
    （7）开关状态sof=-1关着/1开着
    （8）电池的节数bn以及单个电池的电压bv
    '''
    vt = True
    at = True
    vis = np.zeros((len(tmns),), dtype=int)
    vis2 = np.zeros((len(cops),), dtype=int)
    index = cops[0]._t_list[1]  # 从电池的红色接线柱开始绕圈
    end = cops[0]._t_list[0]  # 最后绕回电池的黑色接线柱
    pa = 0
    pcop = [[[], []]]  # 并联的元器件们
    pcop2 = ['Battery']  # 电路图
    pflag = False
    pi = 0  # 第几个并联

    while index!=end:
        # print("目前索引的接线柱为：",end="")
        # tmns[index].out3()
        #if index==10:
        #    break
        vis[index]=1
        if tmns[index]._c_num ==1 :
            if(vis[tmns[index]._t_list[0]]==0): #这个接线柱还没有被访问过
                index = tmns[index]._t_list[0]
                continue
            else: #这个接线柱被访问过了，所以需要跨过这个元器件
                #print("in")
                cindex=info_cops1.get(tmns[index]._category)
                #print("pflag="+ str(pflag)+" pa=" + str(pa) + " cindex=" + info_cops2.get(cindex))
                vis2[cindex] = 1 #标注这个元器件被访问过了
                if pflag:
                    pcop[pi][int(pa/2)].append(info_cops2.get(cindex))
                    #pcop2[len(pcop2)-1].append(info_cops2.get(cindex))
                    #print("pa="+str(pa)+" cindex="+info_cops2.get(cindex))
                else:
                    pcop2.append(info_cops2.get(cindex))
                #找下一个接线柱
                for a in range(0,4):
                    if cops[cindex].get_tlist(a) !=-1 and cops[cindex].get_tlist(a) !=index and vis[cops[cindex].get_tlist(a)]==0 :
                        index = cops[cindex].get_tlist(a)
                        break
                # 找不到下一个未访问接线柱，说明连接断了，回溯到并联起点重新找通路，若没有并联点则说明电路断开
                else:
                    if pflag:
                        index = pbegin
                        continue
                if tmns[index]._color == 1:#是从红色接线柱出来的
                    if cindex == 5:#是电压表
                        vt = False
                    if cindex == 4:#是电流表
                        at = False
        else: #碰到并联情况了
            '''if pa==4:
                print("发现两处并联，错误！")
                break'''
            if pa == 0:#说明刚碰到并联
                pcop2.append(str(pi))
                pflag = True
                pa = 1
                pbegin = index #并联开始的地方
                if (vis[tmns[index]._t_list[0]] == 0):  # 这个接线柱还没有被访问过
                    index = tmns[index]._t_list[0]
                    continue
                if (vis[tmns[index]._t_list[1]] == 0):  # 这个接线柱还没有被访问过
                    index = tmns[index]._t_list[1]
                    continue
                #因为这是第一次访问，所以两个中必定有一个没有访问过，需要跨越元器件的情况这里不考虑
            else:
                if pa==1:#回溯到并联开始的地方
                    vis[index] = 0
                    index = pbegin
                    pa = 2
                    continue
                else:
                    if pa ==2: #第三次，回溯到并联开始的地方了
                        pa=3
                        if (vis[tmns[index]._t_list[1]] == 0):  # 这个接线柱还没有被访问过
                            index = tmns[index]._t_list[1]
                            continue
                        else:
                            #print("innnnn")
                            cindex = info_cops1.get(tmns[index]._category)
                            vis2[cindex] = 1  # 标注这个元器件被访问过了
                            pcop[pi][int(pa/2)].append(info_cops2.get(cindex))
                            #print("pflag="+ str(pflag)+" pa=" + str(pa) + " cindex=" + info_cops2.get(cindex))
                            # 找下一个接线柱
                            for i in cops[cindex]._t_list:
                                if i != -1 and i != index and vis[i]==0:
                                    index = i
                                    break
                            if tmns[index]._color == 1:  # 是从红色接线柱出来的
                                if cindex == 5:  # 是电压表
                                    vt = False
                                if cindex == 4:  # 是电流表
                                    at = False
                    else:#往下走
                        pflag = False
                        pi = pi+1
                        pa=4
                        if (vis[tmns[index]._t_list[0]] == 0):  # 这个接线柱还没有被访问过
                            index = tmns[index]._t_list[0]
                            continue
                        if (vis[tmns[index]._t_list[1]] == 0):  # 这个接线柱还没有被访问过
                            index = tmns[index]._t_list[1]
                            continue
                        cindex = info_cops1.get(tmns[index]._category)
                        vis2[cindex] = 1  # 标注这个元器件被访问过了
                        pcop2.append(info_cops2.get(cindex))
                        # 找下一个接线柱
                        for i in cops[cindex]._t_list:
                            if i != -1 and i != index:
                                index = i
                                break
                        if tmns[index]._color == 1:  # 是从红色接线柱出来的
                            if cindex == 5:  # 是电压表
                                vt = False
                            if cindex == 4:  # 是电流表
                                at = False

    # 检查串联
    # vis2[0]=1
    # res=True
    # for i in vis2:
    #     if i==0:
    #         print("存在未接入电路的元器件，错误！")
    #         res=False
    # print(pcop)
    # print(pcop2)
    sw = swt(cops)
    sa_a = cops[info_cops1.get('Ammeter')].AMsa
    sa_v = cops[info_cops1.get('Voltmeter')].VOsa
    sof = cops[info_cops1.get('Switch')].onoff
    bn = cops[info_cops1.get('Battery')].b_num
    return pcop, pcop2, sw, sa_a, sa_v, sof, bn, vt, at


if __name__ == "__main__":
    # init(info_cops2)
    # main()
    # out_cop(cops)  # 只打印接线柱连接了哪个元器件
    # out_tmns(tmns)
    pcop, pcop2, sw, sa_a, sa_v, sof, bn, bv, vt, at = crete_series()
    print(pcop)
    print(pcop2)
    print(sw)
    print(sa_a)
    print(sa_v)
    print(sof)
    print(bn)
    print(bv)
    print(vt)
    print(at)
