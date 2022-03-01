

class Status(object):
    def __init__(self, name):
        self.category = name
        self.init_cord = [0, 0]
        self.cord = [0, 0]
        self.image = None         # 用来保存图像证据
        self.move_state = 0       # 元器件此刻的移动状态：未变化：0；被挡住：1；挡住后重新出现：2；挡住后位置移动：3；未挡住后直接移动：4；首次出现：5
        self.move_flag = False    # 表示元器件有没有被移动过,当所有元器件都被移动过,就开始导线的检测
        self.check_flag = 0       # 元器件只在开始进行检查,有3种状态,初始为0,移动到中间检查变成1,检查完毕放回原处变成2
        self.hidden = True        # 表示该元器件是否被遮挡
        self.location = [0] * 5   # 列表里存储前五帧该元器件位置
        self.point = -1           # 当前location的下标

    def nearby(self, cord1, cord2, distance=500):
        if (cord1[0] - cord2[0]) ** 2 + (cord1[1] - cord2[1]) ** 2 < distance:
            return True
        else:
            return False

    # 更新元器件状态，修改移动状态：未变化：0；被挡住：1；挡住后重新出现：2；挡住后位置移动：3；未挡住直接移动：4；首次出现：5
    def update(self, new_cord):
        # pre_cord = self.location[self.point]
        # 元器件之前被挡住
        if self.hidden:
            # 新帧依旧被挡住，重置point，返回0
            if new_cord == [0, 0]:
                self.point = -1
                self.move_state = 0
            # 新帧出现了，则继续判断后四帧，此时仍未变化，返回0
            elif self.point == -1:
                self.point += 1
                self.location[self.point] = new_cord
                self.move_state = 0
            # 前一帧出现了，判断新帧和旧帧位置是否一致，若一致则加入location，不一致则替换，返回0
            else:
                old_cord = self.location[self.point]
                if self.nearby(old_cord, new_cord):
                    self.point += 1
                    # 如果连续5帧都一致，则说明该元器件出现了
                    if self.point == 5:
                        self.hidden = False
                        self.point = -1
                        # 如果是第一次出现，则返回4
                        if self.cord == [0, 0]:
                            self.init_cord = new_cord
                            self.cord = new_cord
                            self.move_state = 5
                        # 如果新帧和被遮挡前的位置一致，说明位置没变，返回2
                        elif self.nearby(new_cord, self.cord):
                            self.move_state = 2
                        # 否则说明位置被移动了
                        else:
                            self.cord = new_cord
                            self.move_flag = True
                            self.move_state = 3
                    # 否则将该帧加入location，返回0
                    else:
                        self.location[self.point] = new_cord
                        self.move_state = 0
                # 如果跟前一帧不一致，则将该帧作为起始帧
                else:
                    self.point = 0
                    self.location[self.point] = new_cord
                    self.move_state = 0
        # 元器件之前未被挡住
        else:
            # 如果位置没变，则返回0
            if self.nearby(self.cord, new_cord):
                self.point = -1
                self.move_state = 0
            elif self.point == -1:
                self.point += 1
                self.location[self.point] = new_cord
                self.move_state = 0
            else:
                old_cord = self.location[self.point]
                # 如果这一帧跟上一帧一致，则继续判断
                if self.nearby(old_cord, new_cord):
                    self.point += 1
                    # 如果连续5帧都一致，则说明该元器件位置改变了或被遮挡了
                    if self.point == 5:
                        self.point = -1
                        # 如果新帧为[0,0]，说明元器件被遮挡了
                        if new_cord == [0, 0]:
                            self.hidden = True
                            self.move_state = 1
                        # 否则说明位置被移动了
                        else:
                            self.cord = new_cord
                            self.move_flag = True
                            self.move_state = 4
                    # 否则将该帧加入location，继续判断后面的帧
                    else:
                        self.location[self.point] = new_cord
                        self.move_state = 0
                # 如果跟上一帧不一致，重置point
                else:
                    self.point = 0
                    self.location[self.point] = new_cord
                    self.move_state = 0

    # 检查该元器件是否位于中心,若是则返回True,否则返回False
    def in_center(self):
        x_low = 2560 // 2 - 250
        x_high = 2560 // 2 + 250
        y_low = 1440 // 2 - 150
        y_high = 1440 // 2 + 150

        if x_low < self.cord[0] < x_high and y_low < self.cord[1] < y_high:
            return True

        return False

    # 判断元器件是否回归原位,若是则返回True,否则返回False
    def reset(self):
        if self.nearby(self.init_cord, self.cord, 2500):
            return True
        else:
            return False

    # 检查元器件,即将元器件移动到中心再移动回原处,完成检查则返回1,未完成返回0
    def check_out(self, image):
        if self.check_flag == 0:
            if self.in_center():
                self.check_flag = 1
                self.image = image
        if self.check_flag == 1:
            # 移动到中间后回到原位,说明完成检查
            if self.reset():
                print(f'{self.category}完成检查')
                self.check_flag = 2
                return 1
        if self.check_flag == 2:
            return 1

        return 0


class SwitchStatus(Status):
    def __init__(self):
        super().__init__(name='Switch')
        self.key = 1   # 开关断开是-1，闭合是1。初始状态为1
        # self.activation = False

    # 开关状态:（闭合开关：1）；（断开开关：-1）；（没有变化：0）
    def change_switch(self, new_key):
        # 移动状态若为1说明被遮挡，激活开关状态，之后如果出现2或3说明重新出现，判断新的开关状态是否与原来一致
        # if self.move_state == 1:
        #     self.activation = True
        # if self.activation and (self.move_state == 2 or self.move_state == 3):
        #     self.activation = False
        #     if self.key != new_key:
        #         self.key = new_key
        #         return new_key
        if self.move_state == 2 or self.move_state == 3:
            if self.key != new_key:
                self.key = new_key
                return new_key

        return 0