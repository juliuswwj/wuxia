#!/usr/bin/python3
# -*- coding: utf-8 -*-
# pip3 install opencv-python xxhash adbutils pyserial

import cv2
import numpy as np
import adbutils
import algo
import time
import serial
import sys
import re
import json
import subprocess

from PIL import Image


DONE_JSON = '.done.json'
HOMETOWN = '落霞镇'


def log(str):
    print(f'[{time.ctime()}] {str}', flush=True)


def kick():
    from serial.tools.list_ports_windows import comports

    comport = ''
    for p in list(comports()):
        # print(p.name, p.vid, p.pid)
        if p.vid == 9025 and p.pid == 32822:
            comport = p.name
    if comport == '':
        return

    # align to 0:25, 4:25, 8:25 ...
    t = time.localtime()
    t = (4 - t.tm_hour % 4)*12 - t.tm_min//5 + 5

    ser = serial.Serial(comport, 1000000, timeout=1,
                        parity=serial.PARITY_EVEN, rtscts=1)
    ser.write([int(t),])
    ser.close()


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
        self.region = None

        log('Load')

        adb = adbutils.AdbClient()
        for i in range(3):
            for dev in adb.device_list():
                if 'emulator-' in dev.serial or 'localhost:555' in dev.serial:
                    if dev.get_state() != 'device':
                        adb.disconnect(dev.serial)
                        continue
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
            time.sleep(12)

        app = self.wx.app_current()
        if app.package != NOVASTAR:
            raise Exception(f'E: can not start {NOVASTAR} cur={app.package}')

        self.update()

    def login(self):
        if not algo.ismenu(self.s):
            log('login')
            for i in range(8):
                self.click((600, 370), 4000)  # login
                self.click((600, 580), 3000)  # 开始游戏
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

    def update(self, display=False):
        self.s = self.wx.screenshot()
        if self.s.size != algo.SCREEN:
            raise Exception(f'E: wrong screen size {self.s.size}')

        if not algo.ismenu(self.s):
            return

        region = algo.img2str(self.s, algo.SUB_REGION)
        if display:
            log(f'update {region}')
            return
        if '#(' in region:
            if self.region:
                if 'NA' in self.region:
                    return
                raise Exception(f"bad region {region}")
            self.region = ('NA', (1, 1))
            log(f'go HOMETOWN from {region}')
            self.gomap(HOMETOWN)
            return

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
                if hact in ('5f40412562962130', 'f8947f4bc7b54c4c'):  # 打工, 交差
                    self.click(act, 800)
                    self.click(algo.POS_IDLE)
                    self.click(algo.POS_IDLE, 1500)
                    if hact == '5f40412562962130':  # 打工
                        self.click((642, 319), 1000)  # to stove
                elif hdoc == '140117e44b9fec70':  # 老郎中
                    self.click(doc)
                else:
                    log(f'hact={hact} hdoc={hdoc}')
                continue

            elif pos == (25, 22):
                self.click(algo.SUB_NEAR(1))
                self.click(algo.POS_IDLE)

                self.click(algo.SUB_ACTION(0), 600)
                self.click((768, 248), 500)  # 查看药方
                self.click((858, 533), 1000)  # 确认丹方

                self.update()
                hot = self.subhash(algo.SUB_DAN_HOT)
                # print(f'hot={hot}')
                if hot in ('55be6162a51b0ca1', ):
                    ecnt = 0
                    cnt += 1
                    log(f"working {cnt}")
                    # SUB_FAN == 26fdda31cc1132a8 煽火
                    for tm in (1000, 1650, 2600, 2580, 2700, 2650, 2600):
                        self.click(algo.SUB_DAN_FAN, 0)
                        time.sleep(tm/1000)

                self.click((935, 496), 1500)  # 离开
                self.click((497, 390), 1500)  # 去 老郎中
                continue

            else:
                ecnt += 1
                log(f'unknown pos {pos}')
                time.sleep(1)

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

    def gomap(self, map):
        pos = algo.INNER_MAP.get(self.region[0], None)
        if pos:
            self.click(self.dist(self.region[1], pos), 2000)
            self.update()

        if self.region[0] == map:
            return

        pos = algo.MAP.get(map, None)
        if not pos:
            walk = algo.WALK_MAP.get(map, None)
            if walk:
                self.go(walk, map)
                return
            raise Exception(f"E: bad destination {map}")

        for i in range(5):
            self.click((275, 690), 1000)
            self.update()
            if self.region[0] == map:
                return

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
                np.array(self.s), gopng, cv2.TM_CCOEFF_NORMED))
            log(f'gomap {map} {ret}')
            if ret[1] > 0.8:
                self.click(ret[3], 3000)
                self.update()
                return

            self.click((1220, 670), 1000)  # exit
            if i == 2:
                self.gomap(HOMETOWN)

        raise Exception(f"E: failed to go map {map}")

    def go(self, region, destmap=None):
        log(f'Go {region} from {self.region}')

        last = ()
        ecnt = 0
        retry = 0
        while retry < 150:
            retry += 1
            self.update()
            # print("report", self.region, region)
            if self.region[0] == destmap:
                # return to gomap WALK_MAP
                return
            if self.region[0] != region[0]:
                self.gomap(region[0])
            pos = self.region[1]
            if last != pos:
                last = pos
                ecnt = 0
                time.sleep(1)
                continue

            elif pos == region[1]:
                return

            if ecnt <= 3:
                self.click(self.dist(pos, region[1]), 1000)
                ecnt += 1
                continue

            key = f'{self.region[0]}({pos[0]},{pos[1]})'
            if key in algo.STUCK:
                self.click(self.dist(pos, algo.STUCK[key]), 1000)
                continue

            log(f'stuck at {key}')

            if self.region[0] == HOMETOWN:
                raise Exception(f'already in HOMETOWN')

            ecnt = -3
            self.gomap(HOMETOWN)
            self.gomap(region[0])

        raise Exception('too many retries in go()')

    def daylight(self):
        self.update()
        b = algo.bright(self.s)
        if b > 140:
            return
        log(f'bright -> {b}')
        self.go((HOMETOWN, (23, 14)))
        self.click(algo.SUB_NEAR(1), 600)
        self.click(algo.POS_IDLE, 800)
        self.click(algo.SUB_ACTION(0), 5000)
        self.update()

    def shop(self):
        pos = self.region[1]
        key = f'{self.region[0]}({pos[0]},{pos[1]})'
        cnt = []
        items = {}
        for n, m in algo.ORDER.items():
            if key not in m:
                continue
            s = m[key]
            i = ord(s[-1]) - ord('a')
            if i < 0 or i > 20:
                continue
            while len(cnt) <= i:
                cnt.append(0)
            cnt[i] = int(s[:-1])
            items[n] = cnt[i]

        log(f'buy {items}')

        di = 0
        for i in range(len(cnt)):
            if i in (8, 10, 12, 14, 16):
                self.wx.swipe(524, 290, 524, 190, 1)
                time.sleep(0.5)
                di += 1
            c = cnt[i]
            if c == 0:
                continue
            self.click((350+350*(i % 2), 220+100*(i//2 - di)))
            while c > 1:
                self.click((1110, 424))  # ADD
                c -= 1
            self.click((1000, 580), 800)  # 购买

        self.click((1238, 638), 800)  # 离开

    def save_done(self, name, value):
        self.done[name] = value
        with open(DONE_JSON, 'w') as f:
            json.dump(self.done, f, indent=2)

    def task(self, name, hours):
        tm = time.time()
        if self.done.get(name, 0) > tm:
            return False
        if hours <= 0:  # special hour
            t = time.localtime()
            hours = 0 - t.tm_hour - hours
            if hours <= 0:
                hours += 24
        next = hours * 3420
        self.save_done(name, int(next + tm))
        log(f'!nextTask {name} in {hours} hours')
        return True

    def doact(self):
        n = 0
        for i in range(4):
            pos = algo.SUB_ACTION(i)
            h = algo.subhash(wx.s, pos)
            n = i
            log(f'act{i}={h}')
            if h in ('87b381a340daa9a1',):  # empty
                break

        for i in range(n):
            pos = algo.SUB_ACTION(i)
            h = algo.subhash(wx.s, pos)

            # 宰杀/拔草寻花/曲院风荷/取水
            if h in ('b4712956c4619de7', 'f03cd63041eeed45', 'c6c868190dab835a', 'dc40d28e0aee95e6', 'b1a2d1db29b1714f', '12dbc05e25e36746', 'e2243967c8abfc3c', '2a6178c2af0c2f1f', 'd08946563f721462'):
                self.click(pos, 3000)
                self.click(algo.POS_IDLE, 2000)
                return

            if h in ('47a110082c4c55bc', '3d44319cf4720c24'):  # 喂食
                self.click(pos, 1000)
                self.click((426, 265), 1000)  # 米 (326, 265)  鱼饵
                self.click(algo.POS_IDLE, 1000)
                self.click(algo.POS_IDLE, 3000)
                self.click(algo.SUB_NEAR(0), 800)
                self.click(algo.SUB_ACTION(0), 5000)  # 搜索
                return

            if h in ('37b4cccc754fabb8', 'e9d6eff49ff77d2b'):  # 练武
                self.click(pos, 5000)
                return

            if h in ('382c32044b0793bb', '07fc9df1ad384656'):  # 挑战
                self.click(pos, 2000)
                self.click(pos, 2000)
                self.jump(20)
                return

            if h in ('ad558275084d24ef', 'e39d918cb2fd1099', '82e44623ef3ccc6b', 'c454377181e94947', 'b492652b3ce8a964'):  # 买卖 / 门派商店
                self.click(pos, 2000)
                self.shop()
                return

            if h in ('79f544fd129ef060', '4e0567c9ec3cdf0a', 'b0ddffdf32fcedd4', 'f43adfda31dff123', '462a53057717c661'):  # 离开
                self.click(pos, 1000)
                return

    def empty_near(self):
        h = self.subhash(algo.SUB_NEAR(1))
        return h in ['59ec98a1e3fcf0dd', ]

    def resource(self):
        pattern = r"(.*)\((\d+),(\d+)\)"
        for t in algo.ORDER.values():
            for k in t.keys():
                m = re.match(pattern, k)
                if m:
                    zone, x, y = m.groups()
                    pos = (int(x), int(y))
                    if zone not in algo.RESOURCE:
                        algo.RESOURCE[zone] = [pos,]
                        continue
                    if pos not in algo.RESOURCE[zone]:
                        algo.RESOURCE[zone].append(pos)

        for area, addrs in algo.RESOURCE.items():
            addrs = list(addrs)
            while addrs:
                sx, sy = self.region[1]
                addrs.sort(key=lambda t: ((sx - t[0])**2) + ((sy - t[1])**2))

                pos = addrs[0]
                del addrs[0]
                key = f'{area}({pos[0]},{pos[1]})'
                if not self.task(key, 3 if key in algo.SHORTRSC else -4):  # 4am daily
                    continue

                self.daylight()
                self.go((area, pos))

                if self.empty_near():
                    log(f'W: empty room {self.region}')
                    continue

                kick()
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
                    self.doact()

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
            return algo.subhash(self.s, TITLE) == 'c6b1704e34f5f644'  # 钓鱼

        # print(algo.subhash(self.s, TITLE))
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
                if algo.subhash(self.s, CATCH) in ('c65ad9abf1cd8b1c', '1c4fcdb146c420e8'):  # 继续钓鱼 / 开始钓鱼
                    ecnt += 1
                    if ecnt > 2:
                        self.click(EXIT, 2000)
                        break
                    self.click(CATCH)
                    self.update()
                while algo.subhash(self.s, CATCH) == 'eacadc043615bcbb':  # 拉杆
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

    def fight70(self):
        area = '青城山'
        if self.region[0] != area:
            self.go(('成都', (21, 16)))
            self.click(algo.SUB_NEAR(1))
            self.click(algo.POS_IDLE, 1500)
            self.click(algo.SUB_ACTION(1))
            self.click(algo.POS_IDLE, 1000)
            self.update()
            if self.subhash(algo.SUB_ACTION(0)) == '8798752b3e0d58bc':  # 答应下来
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

    def fight80(self):
        area = '大雪山'
        self.go((area, (13, 20)))

        while self.stamina() > 20:
            for pos in [(9, 16), (4, 17), (9, 23), (10, 30), (4, 24)]:
                self.go((area, pos))
                time.sleep(1)

    def fight(self):
        area = '十方集'
        self.go((area, (6, 8)))

        while self.stamina() > 20:
            for pos in [(5, 22), (2, 23), (4, 26), (8, 28), (9, 24)]:
                self.go((area, pos))
                time.sleep(1)

    def give_one(self, count, simg):
        for c in range(10):
            self.update()

            img = np.array(self.s)
            for i in range(4):
                if count[i] <= 0:
                    continue
                ret = cv2.minMaxLoc(cv2.matchTemplate(
                    img, simg[i], cv2.TM_CCOEFF_NORMED))
                # print(f'${c} {i} {ret[1]}')
                if ret[1] > 0.7:
                    count[i] -= 1
                    scnt = ','.join(map(str, count))
                    log(f'give fruit={i} remain={scnt}')
                    self.save_done('give_fruit', scnt)
                    self.click(ret[3])
                    self.click((930, 440))  # 确认
                    return True

            self.wx.swipe(760, 456, 760, 260, 1)

        self.click((930, 520))  # 取消
        return False

    def give(self):
        if len(sys.argv) > 2 and ',' in sys.argv[2]:
            count = sys.argv[2]
        else:
            count = self.done['give_fruit']
        count = list(map(int, count.split(',')))
        if len(count) != 4:
            log(f'E: len(count) != 4')
            return

        simg = [cv2.imread(f'give{i}.png') for i in range(4)]

        while self.subhash(algo.SUB_NEAR(1)) == 'c4fcbe9c03aced92':  # 老猿
            self.click(algo.SUB_NEAR(1))
            self.click(algo.POS_IDLE)
            self.click(algo.SUB_ACTION(1), 500)
            self.click((839, 189), 500)  # 材料

            if not self.give_one(count, simg):
                break

            self.click(algo.POS_IDLE, 500)
            self.click(algo.POS_IDLE, 500)
            self.update()

        log('end of give')

    def xplant(self):
        self.click(algo.SUB_NEAR(1), 600)
        for i in range(4):
            self.update()
            h = self.subhash(algo.SUB_PLANT)
            if h != '4be321783be15182':  # 活力
                # log(f'no dialog {i} {h}')
                break
            self.click((760, 330+70*i))  # plant action
            for j in range(8):
                time.sleep(0.5)
                self.update()
                h = self.subhash(algo.SUB_PLANTING)
                if h != '08c81c66597d921f':
                    # log(f'no planting {i} {j} {h}')
                    break
            if j > 0:
                break

        self.click(algo.POS_IDLE)
        self.update()

    def plant(self):
        area = '龙泉镇'

        ecnt = 0
        while ecnt < 5:
            for pos in [(19, 15), (19, 16), (19, 17), (20, 17)]:
                self.go((area, pos))

                if not self.empty_near():  # empty
                    ecnt = 0
                    self.xplant()
                    if not self.empty_near():
                        continue

                ecnt += 1
                self.click(algo.SUB_NEAR(0), 700)
                self.update()
                if self.subhash(algo.SUB_ACTION(1)) == '77ff06340bae4846':  # 种植1
                    self.click(algo.SUB_ACTION(1), 700)
                elif self.subhash(algo.SUB_ACTION(2)) == '07cc1356fb5e47d2':  # 种植2
                    self.click(algo.SUB_ACTION(2), 700)
                else:
                    log('W: no plant button')
                    break
                self.click((320, 260), 500)
                self.update()
                if not algo.ismenu(self.s):
                    self.click(algo.POS_IDLE)

    def wudao(self):
        self.go(('洛阳', (20, 28)))
        self.click(algo.SUB_NEAR(1), 500)
        self.click(algo.POS_IDLE)
        self.click(algo.SUB_ACTION(0), 2000)
        self.update()

        WUDAO = 'f56fcafbecdc8185'
        for i in range(1, 16):
            if algo.subhash(self.s, algo.SUB_WUDAO) != WUDAO:
                break
            log(f'wudao {i}')
            self.click(algo.SUB_WUDAO, 8000)
            done = False
            for j in range(120):
                time.sleep(1)
                self.update()
                if algo.subhash(self.s, algo.SUB_WUDAO) == WUDAO:
                    if j == 0:
                        done = True
                    break
            if done:
                break
        self.click(algo.POS_IDLE, 500)


    def all(self):
        self.login()
        kick()

        if algo.ismenu(self.s) and self.task('mapResource', 18):
            self.collect()

        self.resource()

        if self.task('wudao', -4):
            self.wudao()
            kick()

        if self.task('work', 12):
            self.work()
            kick()

        if self.task('fishing', 80):
            self.go(('姑苏', (37, 38)))
            self.fishing()
            kick()

        if self.task('plant', 100):
            self.plant()
            kick()

        if self.stamina() > 140:
            self.fight()
            kick()

        self.stop()


wx = wuxia()
if '-act' in sys.argv:
    for i in range(4):
        print(i, algo.subhash(wx.s, algo.SUB_ACTION(i)))

elif '-doact' in sys.argv:
    wx.doact()

elif '-shop' in sys.argv:
    for i in range(8):
        print(i, algo.subhash(wx.s, algo.SUB_SHOP(i)))

elif '-fight' in sys.argv:
    wx.fight()

elif '-work' in sys.argv:
    wx.work()

elif '-wudao' in sys.argv:
    wx.wudao()

elif '-plant' in sys.argv:
    wx.plant()

elif '-save' in sys.argv:
    wx.s.save('_save.png')

elif '-test' in sys.argv:
    print(algo.subhash(wx.s, algo.SUB_WUDAO, True))

elif '-test2' in sys.argv:
    s = Image.open('_save.png')
    print(algo.subhash(s, algo.SUB_PLANTING, True))


elif '-valid' in sys.argv:
    while True:
        wx.update(True)

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

elif '-kick' in sys.argv:
    kick()

elif '-give' in sys.argv:
    wx.give()

else:
    wx.all()

sys.exit(0)
