# import matplotlib
# matplotlib.use('TkAgg')  # set the backend here
import schemdraw
import schemdraw.elements as elm
from schemdraw.segments import *
from series import *
from svglib.svglib import svg2rlg
from reportlab.graphics import renderPDF, renderPM


class threeBatteries(elm.Element2Term):
    ''' threeBatteries '''
    def __init__(self, *d, **kwargs):
        super().__init__(*d, **kwargs)
        gap = (math.nan, math.nan)
        resheight = 0.25
        batw = resheight * .75
        bat1 = resheight * 1.5
        bat2 = resheight * .75
        self.segments.append(Segment([(0, 0), gap, (batw*5, 0)]))
        self.segments.append(Segment([(0, bat1), (0, -bat1)]))
        self.segments.append(Segment([(batw, bat2), (batw, -bat2)]))
        self.segments.append(Segment([(batw*2, bat1), (batw*2, -bat1)]))
        self.segments.append(Segment([(batw*3, bat2), (batw*3, -bat2)]))
        self.segments.append(Segment([(batw * 4, bat1), (batw * 4, -bat1)]))
        self.segments.append(Segment([(batw * 5, bat2), (batw * 5, -bat2)]))


#自定义滑动变阻器类
class SlideRheostat1(elm.ResistorIEC):
    def __init__(self, *d, **kwargs):
        super().__init__(*d, **kwargs)
        gap = (math.nan, math.nan)
        resheight = 0.25  # Resistor height
        reswidth = 1.0 / 6  # Full (inner) length of resistor is 1.0 data unit
        self.segments.append(SegmentArrow((3*reswidth, resheight*3),
                                          (3*reswidth, resheight),
                                          headwidth=.16, headlength=.2))
        self.segments.append(Segment(
            [(-reswidth*4,resheight*3),(3*reswidth, resheight*3)]))
        self.segments.append(Segment(
            [(-reswidth * 4, resheight * 3), (-reswidth * 4, 0)]
        ))



def save_img(d, img_path):
    # save_path = 'circuit_draw/'
    # d.draw()
    d.save('schematic.svg')#矢量图形式保存到路径circuit_draw\inputsvg
    drawing = svg2rlg("schematic.svg")
    renderPM.drawToFile(drawing, img_path +'电路连接图.png', fmt="PNG")

def draw_func(paralleling, series, sw, sa_a, sa_v, sof, bn, vt, at, img_path):
    # 数据传入
    # paralleling, series, sw, sa_a, sa_v, sof, bn, vt, at = crete_series(image_path)  # series()函数中输出电路连接情况
    # 输入示例数据如下：
    '''
    series=['Battery','Switch','0','SR']#串联情况
    paralleling=[[['Resistance','Ammeter'],['Voltmeter']]]#并联情况
    bn=2#电池节数
    bv=1.5#单个电池电压
    sof=1#开关状态
    sa_a=3#电流表量程
    sa_v=3#电压表量程
    vt=True#电压表接线柱是否连接正确
    at=False#电流表接线柱是否连接正确
    sw=[1,1,3]
    '''

    def change(strlist, str1, str2):
        for a0, i in enumerate(strlist):
            if isinstance(i, list):
                for a1, j in enumerate(i):
                    if isinstance(j, list):
                        for a2, k in enumerate(j):
                            if j[a2] == str1:
                                j[a2] = str2
                    else:
                        if i[a1] == str1:
                            i[a1] = str2
            else:
                if strlist[a0] == str1:
                    strlist[a0] = str2

    # 调用change函数将字符串Sliding Rheostat转化为SR
    change(paralleling, 'Sliding Rheostat', 'SR')
    change(series, 'Sliding Rheostat', 'SR')

    # 开始绘图
    elm.style(elm.STYLE_IEC)
    d = schemdraw.Drawing()

    # 电源情况
    if bn == 2:
        Battery = elm.Battery().label('3V')
    elif bn == 1:
        Battery = elm.BatteryCell().label('1.5V')
    elif bn == 3:
        Battery = threeBatteries().label('4.5V')
    # 开关情况
    if sof == 1:
        Switch = elm.Switch(action='close').theta(180)
    elif sof == -1:
        Switch = elm.Switch(action='open').theta(180)
    # 电流表情况
    if sa_a == 0.6:
        if (at == True):
            Ammeter = elm.MeterA().label('0~0.6A')
        else:
            Ammeter = elm.MeterA().label('0~0.6A').fill('red')
    elif sa_a == 3:
        if (at == True):
            Ammeter = elm.MeterA().label('0~3A')
        else:
            Ammeter = elm.MeterA().label('0~3A').fill('red')
    # 电压表情况
    if sa_v == 3:
        if (vt == True):
            Voltmeter = elm.MeterV().label('0~3V')
        else:
            Voltmeter = elm.MeterV().label('0~3V').fill('red')
    elif sa_v == 15:
        if (vt == True):
            Voltmeter = elm.MeterV().label('0~15V')
        else:
            Voltmeter = elm.MeterV().label('0~15V').fill('red')
    # 电阻情况
    Resistance = elm.ResistorIEC()
    # 滑动变阻器情况
    if sw[0] == 0:
        # if (sw[1] == 1 and sw[2] == 2) or (sw[1] == 2 and sw[2] == 1):
        SR = elm.Line().style('red')
    # elif (sw[1] == 0 and sw[2] == 3) or (sw[1] == 0 and sw[2] == 3):
    #         SR = elm.ResistorIEC().label('20Ω').fill('red')
    elif sw[0] == 1:
        SR = SlideRheostat1()
    elif sw[0] == 2:
        SR = elm.ResistorIEC().label('20Ω').fill('red')

    # 首先绘制电源

    if series[0] == 'Battery':
        B1 = d.add(Battery.reverse())
    # 从电源右端即正极绘制串联情况在第一排绘制三个元器件
    i = 1
    k = 1
    j = 0

    while k < 3:
        if series[i].isdigit():
            # 并联情况
            d.push()
            d += elm.Dot()
            d += elm.Line().up()
            sta = locals()[paralleling[int(series[i])][1][0]]
            d += sta.right()
            for j in range(len(paralleling[int(series[i])][0]) - 1):
                d += elm.Line().right()  # 根据并联中个数加线
            d += elm.Line().down()
            d += elm.Dot()
            d.pop()  # 并联结束
            index = int(series[i])
            for j in range(len(paralleling[index][0])):
                tmp = locals()[paralleling[index][0][j]]
                d += tmp.right()
                k = k + 1
                i = i + 1
        else:
            tmp = locals()[series[i]]
            d += tmp.right()
            i = i + 1
            k = k + 1

    d += elm.Line().up()
    d += elm.Line().up()
    # 在第二排继续绘制
    for i in range(i, len(series)):
        if (series[i].isdigit()):
            # 并联情况
            d.push()
            d += elm.Dot()
            d += elm.Line().up()
            sta = locals()[paralleling[int(series[i])][1][0]]
            d += sta.left()
            for j in range(len(paralleling[int(series[i])][0]) - 1):
                d += elm.Line().left()  # 根据并联中个数加线
            d += elm.Line().down()
            d += elm.Dot()
            d.pop()  # 并联结束
            for j in range(len(paralleling[int(series[i])][0])):
                tmp = locals()[paralleling[int(series[i])][0][j]]
                d += tmp.left().flip().reverse()
        else:
            tmp = locals()[series[i]]
            d += tmp.left().flip().reverse()
            i = i + 1

    # 计算串联并联元器件个数
    totallen = 0
    for j in range(len(series)):
        if series[j].isalpha():
            totallen = totallen + 1
        elif series[j].isdigit():
            totallen = totallen + len(paralleling[int(series[j])][0]) + 1

    # 如果元器件有6个，构成回路
    if totallen == 6:
        d.add(elm.Line().left().tox(B1.start))
        d.add(elm.Line().down())
        d.add(elm.Line().down())

    save_img(d, img_path)