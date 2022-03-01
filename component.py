class Component(object):
    _category = "" #元器件的名字，0->Battery ; 1->Switch ; 2->Sliding Rheostat ; 3->Resistance ; 4->Ammeter ; 5->Voltmeter
    #_t_list = [-1,-1,-1,-1] #接线柱列表，黑t_list[0]，红t_list[1]，红t_list[2]，黑t_list[3]

    def __init__(self, category):
        self._category = category
        self._t_list = [-1, -1, -1, -1]#这里存的不是索引，是类的实例，一开始的连接数是0

    def add_t(self,category,index):
        self._t_list[index]=category

    def __str__(self):
        return 'Component [category=%s , t_list=%s]'%(self._category,self._t_list)

    def out(self):
        '''
        print('Component :category='+self._category,end="  ")
        print('t_list=',end=" ")
        print(self._t_list)
        print("元器件： "+self._category)
        print("黑色接线柱连接：",end="")
        print("黑色接线柱连接：",end="" )
        print("黑色接线柱连接：",end="" )
        print("黑色接线柱连接：",end="" )'''

    def set_tlist(self,index,n):
        self._t_list[index]=n

    def get_tlist(self,index):
        return self._t_list[index]

    def t_list(self):
        return self._t_list

    pass


class Battery(Component):
    b_num = 1 #串联的电池数目
    def __init__(self, category,num):
        self.category = category
        self.b_num = num

    pass


class Switch(Component):
    on_off = 0 #开关状态，-1关着，1开着

    def __init__(self, category, on_off):
        self.category = category
        self.on_off = on_off

    pass