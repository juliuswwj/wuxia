#!/usr/bin/python3


import cv2
import numpy as np
import xxhash
from PIL import Image

SCREEN = (1280, 720)
POS_IDLE = (1062, 678)
SUB_MENU = (1200, 106, 1260, 140, 100)
SUB_RESOURCE = (748, 240, 880, 260, -130)
SUB_REGION = (1120, 222, 1260, 244, 90)
SUB_DAYLIGHT = (1188, 270, 1220, 284, 100)
SUB_VIEW = (90, 90, 1070, 600, 0)
SUB_DAN_FAN = (922, 205, 1007, 238, 140)
SUB_DAN_HOT = (428, 520, 796, 528, 120)
SUB_TRAVEL_TICKET = (315, 572, 442, 600, -80)
SUB_STAMINA = (168, 14, 208, 34, 160)
SUB_CANCEL = (356, 446, 446, 476, -110)
SUB_PLANT = (310, 180, 386, 208, -130)
SUB_PLANTING = (726, 380, 752, 400, 40)

def SUB_NEAR(idx):
    idx *= 54
    return (1166, 325+idx, 1234, 353+idx, -80)


def SUB_ACTION(idx):
    idx *= 73
    return (746, 295+idx, 818, 325+idx, 180)


def SUB_SPOT(x, y):
    dx = (x-y) * 72
    dy = (x+y) * 36
    return (522+dx, 337+dy, 592+dx, 371+dy)


def SUB_SHOP(idx):
    dx = 308 * (idx % 2)
    dy = 108 * (idx//2)
    return (320+dx, 176+dy, 419+dx, 206+dy, 220)


STUCK = {
    "洛阳(3,31)": (9, 32),
    "南阳渡(13,9)": (19, 10),
    "南阳渡(18,15)": (26, 15),
    "杭州(22,15)": (25, 4),
}

SHORTRSC = [
    "杭州(10,18)",
    "杭州(14,32)",
    "峨眉山(43,5)",
    "洛阳(3,6)",
    "洛阳(34,27)",
    "南阳渡(14,6)",
    "落霞镇(29,35)",
    "落霞镇(32,22)",
    "姑苏(32,23)",
    "龙泉镇(11,19)",
    "双王镇(22,27)",
    "凤鸣集(5,2)",
    "成都(30,2)",
    "泉州(20,2)",
    "峨眉山(37,20)",
    "峨眉山(43,5)",
    "成都(25,5)",
]

RESOURCE = {
    "幽州": [(33, 36), (16, 28), (16, 21), (23, 31), (25, 32)],
    "洛阳": [(11, 42), (25, 2), (21, 37), (2, 34), (3, 6), (20, 30), (16, 24), (24, 29), (34, 27)],
    "落霞镇": [(24, 28), (19, 31), (26, 4), (41, 32), (9, 28), (29, 35), (32, 22), (18, 12)],
    "南阳渡": [(44, 24), (25, 23), (24, 20), (22, 4), (8, 14), (13, 30), (14, 6), (19, 19)],
    "太乙山": [(26, 30), (2, 16), (20, 15)], # (2, 26),
    "嵩山": [(8, 35), ],  # (17, 3)
    "泰安镇": [(33, 9), (20, 38), (7, 4), (19, 21), (33, 23), (24, 33)],
    "姑苏": [(28, 2), (4, 22), (10, 26), (32, 23), (20, 20), (21, 16), (15, 16)],
    "杭州": [(30, 2), (30, 26), (20, 5), (14, 32), (24, 17), (27, 23), (10, 18), (6, 13)],
    "龙泉镇": [(11, 8), (3, 2), (19, 5), (24, 17), (3, 17), (11, 19)],
    "泉州": [(15, 28), (17, 1), (13, 15), (19, 13), (20, 2)],
    "南岭": [(12, 10), (12, 21), (27, 18), (18, 4), (1, 17)],
    "双王镇": [(23, 13), (19, 32), (3, 23), (28, 16), (22, 27), (21, 23), (22, 21), (16, 17)],
    "凤鸣集": [(2, 25), (22, 17), (28, 31), (26, 20), (5, 2), (12, 23), (15, 21), (13, 25)],
    "明月山": [(35, 18), (10, 23)], #  (17, 1)
    "成都": [(16, 14), (17, 14), (30, 2), (25, 5)],
    "峨眉山": [(19, 1), (46, 27), (37, 20), (43, 5), (41, 27)],
    "大雪山": [(4, 21), ],
}

ORDER = {
    '6c2fe071989e5700': 5,  # 茯苓
    '01cc9d4b5f9c49e2': 2,  # 白芍
    'e61be2c5c83af0f5': 5,  # 白芍
    '0099102b5b790d2a': 3,  # 金银花
    '365045c33e148ad8': 2,  # 黄精
    '2af296b12528b791': 5,  # 黄精
    'f64e467a3942fda9': 2,  # 地黄
    'aef5f31263718e8c': 5,  # 地黄
    '14d80a6c9eb4e4e6': 1,  # 解毒丹
    'b479aaa84a7c4483': 1,  # 解毒丹
    '6f0fb37953206422': 1,  # 捕兽夹
    '7c10db1a7f6ddf07': 1,  # 捕兽夹
    'a5367a0422adcf6b': 1,  # 捕兽夹
    #'816d247d0d00e34b': 1,  # 鱼竿
    '2e6fff6b66b9d674': 1,  # 鱼饵
    '7a5b073e27fb2172': 5,  # 枸杞
    "99d488ee7329116e": 3,  # 枸杞
    '789dfa64b2892a5f': 5,  # 当归
    'fe1d915f6330ccab': 5,  # 杜仲
    'f5bc8bf1c63e39bc': 2,  # 雄黄
    '662bc24d9e4f9c15': 3,  # 雄黄
    'b620195ca69e0c99': 2,  # 牛黄
    '8b49bc8e7fb75f7d': 3,  # 烧刀子
    'fde339d9f1952b05': 3,  # 竹叶青
    'afa512317eb9d85f': 1,  # 九坛春
    '872fcfef0e8ace3c': 2,  # 葡萄酒
    'e27a82ccd948f38c': 1,  # 佛香
    '067916b910b1dd8e': 5,  # 苹果
    'a7648b616265f808': 5,  # 香蕉
    '9e2b82f6811e78d0': 5,  # 西瓜
    '6ae68d3c0d214853': 5,  # 山楂
    '027586d503a02218': 3,  # 调料
    '564ae79252a6f111': 3,  # 葱蒜
    '104aab7d759caa05': 3,  # 辣椒
    'a7c67dcfa94c7fd5': 5,  # 米
    'd28388b56f06696c': 3,  # 青菜种子
    '973eb90805b08d83': 3,  # 韭菜种子
    '515a1ea313f53946': 3,  # 冬瓜种子
    '1354e619008639ef': 3,  # 茄子种子
}

MAP = {
    "塞北": (801, 3),
    "幽州": (1077, 119),
    "泰安镇": (1102, 267),
    "姑苏": (1136, 403),
    "杭州": (1100, 513),
    "泉州": (1153, 574),
    "龙泉镇": (998, 556),
    "嵩山": (859, 240),
    "洛阳": (872, 334),
    "南阳渡": (825, 447),
    "双王镇": (824, 516),
    "南岭": (783, 704),
    "落霞镇": (714, 287),
    "太乙山": (718, 402),
    "凤鸣集": (678, 511),
    "明月山": (687, 588),
    "鄯善": (457, 99),
    "敦煌": (346, 157),
    "成都": (546, 563),
    "峨眉山": (412, 647),
    "大雪山": (240, 366),
    "十方集": (134, 47),
}

OCR = {
    # resource name
    "4f452434fb940602+4f927ef19138052d": "剩",
    "4f452434fb940602+f74e2c90f09bd225": "剩",
    "81c5b1b7fe4e41b5": "余",
    "6d5bd4b09bcbc985": "资",
    "09c8a5b1bc555ef1+11818dc3d642321e": "源",

    # resource count
    "f462f1593319a196": "0",
    "82e568becd2bb02f": "0",
    "2524d69646e769a3": "1",
    "60c1a6457443df26": "1",
    "5719ddc17465ebe7": "2",
    "cc2bcb06eda2efd7": "2",
    "9de390d82e99bd06": "3",
    "ae2cddd9da7bb199": "3",
    "a66e9ce8ebff06a1": "4",
    "877ea24a6130c98e": "4",
    "b6b13dc2cd03564c": "5",
    "83690aafe0050be4": "5",
    "a7514792fc9848cd": "6",
    "b0af644229ed0e59": "6",
    "185eb70e32ef7de1": "7",
    "75d2ad45829e20b4": "7",
    "8ecb07c3b33133bb": "8",
    "183542bceeaabf81": "8",
    "c890677c509c8fc6": "9",
    "545ac9a1eeac3696": "9",

    # stamina
    "0ad15eb3d6b6ab07": "0",
    "2dd043a735d91231": "0",
    "8dee69b4f9d0bbb9": "0",
    "2213b2064762ce54": "0",
    "359953365dbaf0ff": "0",
    "165a5ca11dbebc61": "1",
    "373075f83497b59f": "1",
    "a259994df767edd9": "1",
    "63e22419d7ed3796": "1",
    "418156c601a80811": "1",
    "686efacfc7605472": "2",
    "1f80cb719ced47da": "2",
    "06cbc42efceeea01": "2",
    "940b47a0d1d877cb": "2",
    "9de60a52201ab2cc": "2",
    "6ba2df48c7027924": "2",
    "08806595b84ab360": "3",
    "9a42026f2dedcdd2": "3",
    "ff7dfb70c7c5a388": "3",
    "83c3403135fc10d9": "3",
    "b62d95225766b2d6": "3",
    "41155b64ca91d246": "4",
    "27e66557192523dd": "4",
    "5bc6eb950763e675": "4",
    "ba2ead8680197914": "4",
    "1d25f74e4c182b80": "5",
    "a4859a29b311a8b7": "5",
    "5cc697948fa3eb05": "5",
    "24ad474f828841df": "5",
    "f97de52b56992ae5": "6",
    "34e6db6b02d244b3": "6",
    "a7548b851bbd8997": "6",
    "533d7922b62a5af6": "6",
    "7b462f13ab128c3f": "6",
    "fad293e740e32e12": "6",
    "9488c8679d6a7162": "7",
    "2fd5ed41bb42d3da": "7",
    "af816a076664547d": "7",
    "86fb70a902f5d52c": "8",
    "ca37f3e236337518": "8",
    "294d342f8d725d85": "8",
    "a710630e35dff112": "8",
    "7311ae6e0dc1d70a": "9",
    "8606f3c87ce0803e": "9",
    "0fb0cca4f8751070": "9",
    "af591f9da4e8a363": "9",
    "68433756f863b390": "",
    "33cc7223159e9ce6": "",

    # region
    "e8fcdae9bab13e96": ",",
    "e4602bfd2a62ae40": ",",
    "f3b8189fc293f86c": ",",
    "2f26cd485f8fcb3c": ",",

    "256111942d6fd8ef": "南",
    "3fefa622f565b7ed": "南",
    "fcfe5d6b6a6476ee": "南",
    "d55664c00c22c37a": "阳",
    "2a8952bace0a34d4": "渡",

    "83831c5facd7dcda": "洛",
    "9a424480aed02075": "洛",
    "c2007bb7829bdcb8": "阳",

    "0b9f31ff83042964": "落",
    "22432de24bcc2554": "落",
    "deb1d5d769606eeb": "霞",
    "8b85184e038789f0": "镇",
    "d34b9c4c3587d65e": "镇",

    "9040f809fbac4cfa": "嵩",
    "f6b0cbc0519c34aa": "山",

    "58b187b41e9b2352": "泰",
    "4cc6b4ed346833a2": "安",

    "77d87b0d33513640": "姑",
    "ebf79bf24797d98c": "姑",
    "9ad75899da29b51c": "苏",
    "5ad86e31ee004bb7": "苏",

    "690239034e0dd45a+cc20393deffc087d": "杭",
    "404346f0e5589973+7e819e20cd145dda": "州",

    "18725d32a307c7f2": "泉",

    "622d108f44a9d1f6": "龙",
    "b855876fe9b81333": "泉",

    "d14805e7015a308b": "双",
    "0289a7aa91581f6c": "王",

    "27601872580365ae": "明",
    "d9c2abdafa061b65": "月",
    "50368b444559277d": "山",

    "12022ddd60f0c30b": "凤",
    "ed81da1a3430bf3a": "鸣",
    "edeb568c6f7258eb": "集",

    "0c4dfacdf6f122c4": "峨",
    "21b0259fe705b6d4": "眉",

    "e1060aace5436866": "成",
    "a3f7077cae4364d5": "都",
    "acbf29de43e8b82b": "都",

    "718c5db40c779513": "大",
    "ca520ef26bead8fc": "雪",

    "7e3b2fc20a682762": "敦",
    "bc7e83c53e6643ec": "煌",

    "50ab9eb3d40fc221": "青",
    "44a2cd22a2a953c9": "城",

    "23c9f5eef170a6bb": "十",
    "472b809ddceac96f": "方",

    "bc73c34e2b3cf218": "塞",
    "986ff01f0188a04c+12c2aae3185fbf71": "北",

    "1e55f8150c172afa": "幽",

    "efc6b2e614123b65": "太",
    "e627a9e52647dac4": "乙",

    "846896536d94cb5b": "岭",

    "e40ee206a4212f16": "衡",

    "7412a0c64992d208": "(",
    "5f7faf401550c6d7": "(",
    "aef091470480dd28": "(",

    "c64fae619605a0ff": ")",
    "5d85b5cb0407fbf1": ")",
    "cc067b6a4b6c6a6e": ")",

    "8eef1f4a86d41f47": "0",
    "6e9826a85134658a": "0",
    "ead195b361f2e0d7": "0",
    "35119afa0cb8c749": "0",
    "6390fccc3ff07b51": "0",

    "e4c16b2f9f338a0f": "1",
    "558cf069059c22f1": "1",
    "737ec3a1baa47df6": "1",
    "ac25d35e836519c2": "1",
    "655a3102e77d8304": "1",
    "aa6cf92e840cceb9": "1",
    "907ca2cff662f2cb": "1",
    "d5cb7078c5bdb04c": "1",

    "7d459c9943476693": "2",
    "55c4c4d14610bf83": "2",
    "32605c8fa1f1ff06": "2",
    "44a24cd3ecb8443f": "2",
    "3990079e16e065bc": "2",
    "3da52b2229b5eb6e": "2",
    "954a3810b19df2d8": "2",
    "0fded74140ef8611": "2",
    "ffae41cd6ac0e643": "2",

    "d155a081965ed746": "3",
    "0697be65a242d1c5": "3",
    "2f16b3ac6922f53c": "3",
    "f7dde943b3b429c2": "3",
    "3c0b5d69eddf814a": "3",
    "e28143d47dc1243c": "3",
    "5ef7d479e43c7859": "3",
    "8d59ec5d043919cc": "3",
    "5201acaaeafece9f": "3",
    "66d5ec9446dd7a7b": "3",

    "ce86eac67dcda445": "4",
    "08affe60d13ce2ce": "4",
    "3822864ed894058e": "4",
    "bdc89fc228e89456": "4",
    "79f603dfd025b210": "4",
    "3d53c87f44494600": "4",
    "0c1f8c737070c87c": "4",
    "2152a8f1b96d36b1": "4",
    "b7119ab8588b9e33": "4",
    "3abbc62ea8b70ca8": "4",
    "79090b8cb3f44dfe": "4",
    "e0f24f4a0182b1a8": "4",

    "e14b49f0c7fabf0e": "5",
    "0f71c0d318a37ce6": "5",
    "aefd91813395a006": "5",
    "ab6478b9aaae0776": "5",
    "8940d87a87e201f7": "5",
    "16e12c3ca3e3571a": "5",
    "0b93633726848a97": "5",
    "e206d3f455992d19": "5",

    "abdef9b0805e6beb": "6",
    "c7dfadba12f6a2dd": "6",
    "438c16435a18b51c": "6",
    "fd43f0ae202833c4": "6",
    "7f0733c35c72b8d8": "6",
    "8335b647053b54b3": "6",
    "2bcb8e252794933f": "6",

    "ca797bba9ec12c89": "7",
    "ff3d6b893863ee62": "7",
    "278f041a34b267b2": "7",
    "9982f1db0477c6c0": "7",
    "0b444364d7cc9bab": "7",
    "68e634c9077466a4": "7",

    "4fe78dfa49d5e26a": "8",
    "31eede5e906d178d": "8",
    "3304a981ecd56286": "8",
    "f51baf45c53724fe": "8",
    "ab12d39f2a6c868c": "8",
    "1a53cc44dc4d70b6": "8",

    "913a9da89a839ca9": "9",
    "6c3cccce761517f0": "9",
    "90d7bfbb036f7105": "9",
    "4ae477da9b5a8f16": "9",
    "73f62f14e992fecd": "9",
    "6caaeb407371448c": "9",
    "fee120d7d025f418": "9",
    "8d0413b858237256": "9",
}


def hash(arr):
    return xxhash.xxh64(arr).hexdigest()


def subimg(img: Image.Image, sub: tuple[int], show=False):
    img = np.array(img.crop(sub[:4]))
    img = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    if sub[4] > 0:
        _, img = cv2.threshold(img, sub[4], 255, cv2.THRESH_BINARY)
    if sub[4] < 0:
        _, img = cv2.threshold(img, -sub[4], 255, cv2.THRESH_BINARY_INV)
    if show:
        Image.fromarray(img).show(f'subimg {sub}')
    return img


def subhash(img: Image.Image, sub: tuple[int], show=False):
    return hash(subimg(img, sub, show))


def img2str(image: Image.Image, sub: tuple[int]):
    img = subimg(image, sub)
    contours, _ = cv2.findContours(
        img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    hashes = []
    for i, contour in enumerate(contours):
        x, y, w, h = cv2.boundingRect(contour)
        im = img[y:y+h, x:x+w].tobytes()
        hh = hash(im)
        if h > 8 or hh in OCR:
            hashes.append((x, w, h, hh))
        # else:
        #    print(x, w, h, hh)
    hashes.sort()

    txt = ''
    i = 0
    while i < len(hashes):
        if i < len(hashes)-1:
            key = hashes[i][3] + '+' + hashes[i+1][3]
            if key in OCR:
                txt += OCR[key]
                i += 2
                continue
        key = hashes[i][3]
        i += 1
        if key in OCR:
            txt += OCR[key]
            continue
        txt += f'#{hashes[i-1]}#'

    if '#(' in txt:
        Image.fromarray(img).save('_img2str.png')

    return txt


def ismenu(image: Image.Image):
    img = subimg(image, SUB_MENU)
    return hash(img) in ['15ed6bc6745e343a', '']


def bright(image: Image.Image, sub: tuple[int] = SUB_DAYLIGHT):
    return subimg(image, sub).mean()


def gridlines(img: cv2.Mat, dx: int, tcmin: int):
    sx = 455
    sy = 75
    thresh = 1.03
    lines = []
    ts = []
    while sy < 275:
        t = 0
        ct = 1
        x, y = sx, sy
        for i in range(200):
            a, b, c = img[y-1, x-dx], img[y, x], img[y+1, x+dx]
            if b > 1 and a/b > thresh and c/b > thresh:
                t += ct
                ct += 1
            elif ct > 1:
                ct -= 1
            x -= dx
            y += 1
        sx += dx
        sy += 1
        if t > tcmin:
            lines.append((sx, sy, x, y))
        ts.append(t)
    print(ts)
    return lines


def grid(image: Image.Image):
    img = subimg(image, SUB_VIEW)
    Image.fromarray(img).save('_grid.png')

    cimg = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)

    for line in gridlines(img, 2, 110):
        x1, y1, x2, y2 = line
        cv2.line(cimg, (x1, y1), (x2, y2), (255, 0, 0), 1)
    for line in gridlines(img, -2, 110):
        x1, y1, x2, y2 = line
        cv2.line(cimg, (x1, y1), (x2, y2), (0, 255, 0), 1)

    Image.fromarray(cimg).show(f'lines')
