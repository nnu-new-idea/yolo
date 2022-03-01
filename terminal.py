class Terminal(object):
    #_color = 0 #接线柱的颜色，-1为黑色，1为红色
    #_c_num = 0 #连接元器件的数量，不包含自身
    #_c_list = []
    #放接线柱序号
    #放所属的元器件
    #color好像不需要
    info_cops2 = {0: 'Battery', 1: 'Switch', 2: 'Sliding Rheostat', 3: 'Resistance', 4: 'Ammeter', 5: 'Voltmeter'}
    info_tmn = {0:'BTerminal_1',1: 'RTerminal_1',2: 'RTerminal_2',3: 'BTerminal_2'}

    def __init__(self,color,category):
        self._color = color
        self._c_num = 0
        self._c_list = [] #接线柱所属的元器件
        self._t_list = [] #接线柱序号
        self._category = category

    def link_num(self):
        return self._c_num

    def next(self, pos):
        return self._t_list[pos]

    def next_list(self):
        return self._t_list

    def belong(self):
        return self._category

    def add_c(self,index1,index2):
        self._c_num += 1
        self._c_list.append(index1)
        self._t_list.append(index2)

    def out(self):
        '''print("color=",end=" ")
        print(self._color,end=" ")
        print("元器件=", end=" ")
        print(self._category, end=" ")
        print("元器件个数=", end=" ")
        print(self._c_num, end=":")
        print("元器件列表=", end=" ")
        print(self._c_list)'''
        for one in self._c_list:
            print(self.info_cops2.get(one),end="  ")
        print()

    def out2(self):
        print("color=",end=" ")
        print(self._color,end=" ")
        print("元器件=", end=" ")
        print(self._category, end=" ")
        print("元器件个数=", end=" ")
        print(self._c_num, end=":")
        print("元器件列表=", end=" ")
        for one in self._c_list:
            print(self.info_cops2.get(one), end="  ")
        print()

    def out3(self):
        print(self._category+"的",end="")
        # _color = 0 #接线柱的颜色，-1为黑色，1为红色
        if self._color==-1 :
            print("黑色接线柱")
        else:
            print("红色接线柱")
    pass

