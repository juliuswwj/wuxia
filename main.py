#!/usr/bin/python3


import cv2
import numpy as np
import adbutils
import algo
import time
import sys
import json
import subprocess

from PIL import Image


DONE_JSON = '.done.json'


def log(str):
    print(f'[{time.ctime()}] {str}', flush=True)


class wuxia:
    def __init__(self):
        try:
            with open(DONE_JSON, 'r') as f:
                self.done = json.load(f)
        except:
            self.done = {}

        self.load()

    def load(self):
        self.wx = None

        log('Load')

        adb = adbutils.AdbClient()
        for i in range(3):
            for dev in adb.device_list():
                if 'emulator-' in dev.serial or 'localhost:555' in dev.serial:
                    self.wx = dev
                    break

            if self.wx:
                break

            self.proc = subprocess.Popen(
                [r'C:\Program Files\BlueStacks_nxt\HD-Player.exe'])
            time.sleep(10)
            adb.connect('localhost:5555', 3)
        else:
            raise Exception('Can not start BlueStacks_nxt')

        NOVASTAR = 'com.wuxia.novastar'
        app = self.wx.app_current()
        if app.package != NOVASTAR:
            self.wx.app_start(NOVASTAR)
            time.sleep(8)

        app = self.wx.app_current()
        if app.package != NOVASTAR:
            raise Exception(f'E: can not start {NOVASTAR} cur={app.package}')

        self.update()

    def login(self):
        if not algo.ismenu(self.s):
            log('login')
            self.click((600, 370), 6000)  # login
            self.click(algo.POS_IDLE, 1000)  # discard online notice
            for i in range(5):
                self.click((600, 580), 4000)  # 开始游戏
                self.click((810, 476), 1000)  # 强制下载
                self.click(algo.POS_IDLE, 1000)
                self.update()
                if algo.ismenu(self.s):
                    break
            else:
                self.s.save(f'_nologin.png')
                self.stop()
                raise Exception(f'E: can not login')

    def stop(self):
        self.update()

        log('Stop')

        if algo.ismenu(self.s):
            self.click(algo.SUB_MENU, 800)
            self.click((650, 430), 800)  # 切换设备
        self.click((770, 470), 8000)

        subprocess.run(['taskkill', '/F', '/IM', 'HD-Player.exe'])

    def update(self):
        self.s = self.wx.screenshot()
        if self.s.size != algo.SCREEN:
            raise Exception(f'E: wrong screen size {self.s.size}')

        if not algo.ismenu(self.s):
            return

        region = algo.img2str(self.s, algo.SUB_REGION)
        if '#(' in region:
            raise Exception(f"bad region {region}")

        region = region.replace('(', ',').replace(')', ',').split(',')
        self.region = (region[0], (int(region[1]), int(region[2])))

    def click(self, pos, sleep=300):
        self.wx.click(pos[0], pos[1])
        time.sleep(sleep/1000)

    def subhash(self, pos):
        return algo.subhash(self.s, pos)

    def work(self):
        self.go(('南阳渡', (25, 23)))

        cnt = 0
        ecnt = 0
        last = ()
        while True:
            self.update()
            pos = self.region[1]
            if last != pos:
                last = pos
                time.sleep(1)
                continue

            elif ecnt > 4:
                # discard work dialog
                log("end of work")
                for i in range(3):
                    self.click(algo.POS_IDLE, 2000)
                return

            elif pos == (25, 23):
                ecnt += 1
                doc = algo.SUB_NEAR(1)
                hdoc = self.subhash(doc)
                act = algo.SUB_ACTION(2)
                hact = self.subhash(act)
                if hact in ('b5f8a39883d41faf', '19082fac8537dba7'):  # 打工, 交差
                    self.click(act, 800)
                    self.click(algo.POS_IDLE)
                    self.click(algo.POS_IDLE, 800)
                    self.update()

                    act = algo.SUB_ACTION(1)
                    hact2 = wx.subhash(act)
                    if hact2 == '0dbf7bb391efcc23':  # 离开，没干完活
                        self.click(act, 500)
                        hact = 'b5f8a39883d41faf'
                    if hact == 'b5f8a39883d41faf':
                        self.click((642, 319), 1000)  # to stove
                elif hdoc == 'ab02a53929e19fff':  # 老郎中
                    self.click(doc)
                else:
                    log(f'hact={hact} hdoc={hdoc}')
                continue

            elif pos == (25, 22):
                self.click(algo.SUB_NEAR(1))
                self.click(algo.POS_IDLE)

                self.click(algo.SUB_ACTION(0))
                self.click((768, 248))  # 查看药方
                self.click((858, 533), 500)  # 确认丹方

                self.update()
                hot = self.subhash(algo.SUB_DAN_HOT)
                if hot in ('82915becacc0d477', ):
                    ecnt = 0
                    cnt += 1
                    log(f"working {cnt}")
                    # SUB_FAN == 26fdda31cc1132a8 煽火
                    for tm in (1000, 1810, 2600, 2580, 2700, 2650, 2600):
                        self.click(algo.SUB_DAN_FAN, 0)
                        time.sleep(tm/1000)

                self.click((935, 496), 1000)  # 离开
                self.click((497, 390), 1000)  # 去 老郎中
                continue

            else:
                ecnt += 1
                log(f'unknown pos {pos}')
                time.sleep(1)

    def gomap(self, map):
        if self.region[0] == map:
            return
        pos = algo.MAP.get(map, None)
        if not pos:
            raise Exception(f"E: bad destination {map}")

        for i in range(5):
            self.click((275, 690), 1000)
            self.update()

            if self.subhash(algo.SUB_CANCEL) == '3101f10d3185c963':  # click on save button
                self.click(algo.SUB_CANCEL, 800)
                continue

            h = self.subhash(algo.SUB_TRAVEL_TICKET)
            if h not in ('aef6297b7e9cf85a', '0942aedb46062a59', 'c2d996151d90383b', 'b1288b2d3d49bfca', 'e8ceb833966794f8', '9fd6bc63af53a3e9', '48c09c045a0e12ae', '8a366cf0bcab81dc', 'c9a88875c84cb7c7'):  # 叫唤马车
                if i < 4:
                    self.click((1220, 670), 1000)  # exit
                    continue
                raise Exception(f"E: no travel ticket {h}")
            self.click(algo.SUB_TRAVEL_TICKET, 1000)
            self.wx.swipe(1155, 622, 700, 400, 1.5)
            time.sleep(0.3)
            self.wx.swipe(230, 600, 380, 640, 1)
            time.sleep(0.3)
            self.wx.swipe(380, 640, 530, 670, 1)
            time.sleep(0.3)

            self.click(pos, 1000)
            self.update()

            gopng = cv2.imread('gomap.png')
            ret = cv2.minMaxLoc(cv2.matchTemplate(
                np.array(wx.s), gopng, cv2.TM_CCOEFF_NORMED))
            log(f'gomap result {ret}')
            if ret[1] > 0.8:
                self.click(ret[3], 3000)
                self.update()
                return
            else:
                self.click((1220, 670), 1000)  # exit
        raise Exception(f"E: failed to go map {map}")

    def dist(self, pos, target):
        dist = []
        for x in range(-6, 7):
            for y in range(-6, 7):
                r = algo.SUB_SPOT(x, y)
                if r[0] < 10 or r[0] > 1080 or r[1] < 50 or r[1] > 615:
                    continue
                d = ((x + pos[0] - target[0])**2) + \
                    ((y + pos[1] - target[1])**2)
                dist.append((d, (r[0]+r[2])//2, (r[1]+r[3])//2))
        dist.sort()
        return (dist[0][1], dist[0][2])

    def go(self, region):
        log(f'Go {region}')
        self.gomap(region[0])

        last = ()
        ecnt = 0
        while True:
            self.update()
            pos = self.region[1]
            if last != pos:
                last = pos
                ecnt = 0
                time.sleep(1)
                continue

            elif pos == region[1]:
                return

            if ecnt <= 5:
                self.click(self.dist(pos, region[1]), 1000)
                ecnt += 1
                continue

            key = f'{self.region[0]}({pos[0]},{pos[1]})'
            if key in algo.STUCK:
                self.click(self.dist(pos, algo.STUCK[key]), 1000)
                continue

            log(f'stuck at {key}')
            ecnt = 0
            self.gomap('落霞镇')
            self.update()
            self.gomap(region[0])

    def daylight(self):
        self.update()
        b = algo.bright(self.s)
        if b > 140:
            return
        log(f'bright -> {b}')
        self.go(('落霞镇', (23, 14)))
        self.click(algo.SUB_NEAR(1), 600)
        self.click(algo.POS_IDLE, 800)
        self.click(algo.SUB_ACTION(0), 5000)
        self.update()

    def shop(self):
        self.update()
        for i in range(8):
            h = algo.subhash(wx.s, algo.SUB_SHOP(i))
            c = algo.ORDER.get(h, 0)
            log(f'ORDER {i} {h} {c}')
            if c == 0:
                continue
            self.click(algo.SUB_SHOP(i))
            while c > 1:
                self.click((1108, 418))
                c -= 1
            self.click((1000, 580), 800)  # 购买
        self.click((1238, 638), 800)  # 离开

    def setdone(self, name, short=False):
        next = 80000
        if short:
            next = 6*3600-600
        self.done[name] = next + time.time()
        with open(DONE_JSON, 'w') as f:
            json.dump(self.done, f, indent=2)
        log(f'!SetDone {name} with {next}')

    def isdone(self, name):
        return self.done.get(name, 0) > time.time()

    def resource(self):
        for area, addrs in algo.RESOURCE.items():
            addrs = list(addrs)
            while addrs:
                sx, sy = self.region[1]
                addrs.sort(key=lambda t: ((sx - t[0])**2) + ((sy - t[1])**2))

                pos = addrs[0]
                key = f'{area}({pos[0]},{pos[1]})'
                if self.isdone(key):
                    del addrs[0]
                    continue
                self.setdone(key, key in algo.SHORTRSC)

                self.daylight()
                self.go((area, pos))
                del addrs[0]

                if self.subhash(algo.SUB_NEAR(1)) == '59ec98a1e3fcf0dd':
                    log(f'W: empty room {self.region}')
                    continue

                self.click(algo.SUB_NEAR(1), 600)

                REMAIN_RESOURCE = '剩余资源'
                self.update()
                resource = algo.img2str(self.s, algo.SUB_RESOURCE)
                isrsc = resource.startswith(REMAIN_RESOURCE)

                if isrsc:
                    self.click((766, 322), 1000)  # 开始采集
                    while True:
                        self.update()
                        resource = algo.img2str(self.s, algo.SUB_RESOURCE)
                        if not resource.startswith(REMAIN_RESOURCE) or resource == REMAIN_RESOURCE+'0':
                            self.click(algo.POS_IDLE, 800)
                            break
                        time.sleep(3)
                else:
                    time.sleep(4)
                    self.update()

                    for i in range(4):
                        pos = algo.SUB_ACTION(i)
                        h = algo.subhash(wx.s, pos)
                        log(f'{i} {h}')
                        # 宰杀/拔草寻花/曲院风荷/取水
                        if h in ('64ad7dc4453b36b8', '0e8f4a2706026a2e', '406a89b92d02b3b4', '2a6178c2af0c2f1f'):
                            self.click(pos, 3000)
                            self.click(algo.POS_IDLE, 2000)
                            break

                        if h in ('c61ac622d0f191df', ): # 喂食
                            self.click(pos, 1000)
                            self.click((326, 265), 1000) # 米
                            self.click(algo.POS_IDLE, 1000)
                            self.click(algo.POS_IDLE, 3000)
                            self.click(algo.SUB_NEAR(0), 800)
                            self.click(algo.SUB_ACTION(0), 5000) # 搜索
                            break

                        if h in ('28adcc73d92da80f', ):  # 练武
                            self.click(pos, 5000)
                            break

                        if h in ('05239573f0a332eb', ):  # 挑战
                            self.click(pos, 2000)
                            self.click(pos, 2000)
                            self.jump(20)
                            break

                        if h in ('7d988460f6d701d5', '16f120bde69e49a2'):  # 买卖 / 门派商店
                            self.click(pos, 2000)
                            self.shop()
                            break

                        if h in ('b0ddffdf32fcedd4', ):  # 离开
                            self.click(pos, 1000)
                            break

    def jump(self, cnt):
        for i in range(cnt):
            log(f'Jump {i}')
            time.sleep(1.5)
            self.wx.swipe(500, 400, 500, 370, 0.950)
        time.sleep(1)
        self.wx.swipe(500, 400, 500, 370, 0.2)
        log('End of jump')
        for i in range(5):
            self.click(algo.POS_IDLE, 1000)

    def collect(self):
        self.click((945, 685), 1000)  # 地图
        self.click((1226, 572), 1000)  # 收取资源
        self.click((1220, 670))  # 返回

    def fishing(self):
        TITLE = (170, 196, 230, 222, 180)
        CATCH = (900, 230, 1020, 260, 180)
        EXIT = (900, 490, 1020, 520, 180)
        POLE = (760, 400, 772, 412, 100)

        def infishing():
            return algo.subhash(self.s, TITLE) == 'dbdb49f684f6714d'  # 钓鱼

        while True:
            self.update()
            if not infishing():
                self.click(algo.SUB_NEAR(0), 1000)
                self.click(algo.SUB_ACTION(0), 1000)
                self.update()
            if not infishing():
                break
            ecnt = 0
            cnt = 0
            while infishing():
                if algo.subhash(self.s, CATCH) in ('a866611484f8ad94', 'dca62e0596a98600'):  # 继续钓鱼 / 开始钓鱼
                    ecnt += 1
                    if ecnt > 2:
                        self.click(EXIT, 2000)
                        break
                    self.click(CATCH)
                    self.update()
                while algo.subhash(self.s, CATCH) == '5e80ba360e3c0bc9':  # 拉杆
                    ecnt = 0
                    self.update()
                    b = algo.bright(self.s, POLE)
                    if b < 170:
                        cnt += 1
                        log(f'fishing {cnt}')
                        self.click(CATCH)
                        break
                time.sleep(1.5)
                self.update()
            if ecnt > 2:
                break

    def stamina(self):
        self.update()
        st = algo.img2str(self.s, algo.SUB_STAMINA)
        log(f'stamina = {st}')
        try:
            return int(st)
        except:
            return 50

    def fight(self):
        area = '青城山'
        if self.region[0] != area:
            self.go(('成都', (21, 16)))
            self.click(algo.SUB_NEAR(1))
            self.click(algo.POS_IDLE, 1500)
            self.click(algo.SUB_ACTION(1))
            self.click(algo.POS_IDLE, 1000)
            self.update()
            if self.subhash(algo.SUB_ACTION(0)) == '8798752b3e0d58bc': # 答应下来
                self.click(algo.SUB_ACTION(0), 800)
            else:
                self.click(algo.SUB_ACTION(1), 800)
            self.click(algo.POS_IDLE, 1000)

            self.go(('成都', (19, 4)))
            self.go(('成都', (1, 2)))
            self.click(algo.SUB_SPOT(-2, -1), 6000)
            self.update()

        while self.stamina() > 20:
            for pos in [(18, 17), (15, 18), (13, 12), (10, 15), (8, 11)]:
                self.go((area, pos))
                time.sleep(1)


    def all(self):
        self.login()

        if not self.isdone('mapResource') and algo.ismenu(self.s):
            self.setdone('mapResource')
            self.collect()

        self.resource()

        if not self.isdone('work'):
            self.setdone('work')
            self.work()

        if not self.isdone('fishing'):
            self.setdone('fishing')
            self.go(('姑苏', (37, 38)))
            self.fishing()

        if self.stamina() > 140:
            self.fight()

        self.stop()


wx = wuxia()
if '-act' in sys.argv:
    for i in range(3):
        print(i, algo.subhash(wx.s, algo.SUB_ACTION(i)))

elif '-shop' in sys.argv:
    for i in range(8):
        print(i, algo.subhash(wx.s, algo.SUB_SHOP(i)))

elif '-fight' in sys.argv:
    wx.fight()

elif '-save' in sys.argv:
    wx.s.save('_save.png')

elif '-test' in sys.argv:
    print(algo.subhash(wx.s, algo.SUB_CANCEL, True))

elif '-save20' in sys.argv:
    for i in range(20):
        print(f'save {i}')
        wx.wx.screenshot().save(f'_save{i}.png')
        time.sleep(0.5)

elif '-spot' in sys.argv:
    img = np.array(wx.s)
    for x in range(-6, 7):
        for y in range(-6, 7):
            r = algo.SUB_SPOT(x, y)
            if r[0] < 10 or r[0] > 1080 or r[1] < 50 or r[1] > 615:
                continue
            img = cv2.rectangle(img, (r[0], r[1]), (r[2], r[3]), (255, 0, 0))
    Image.fromarray(img).show(f'spots')

elif '-fishing' in sys.argv:
    wx.fishing()

else:
    wx.all()

sys.exit(0)
