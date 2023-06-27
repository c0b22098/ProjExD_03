import random
import sys
import time
import math
import random

import pygame as pg
import numpy as np


WIDTH = 1200  # ゲームウィンドウの幅1600
HEIGHT = 600  # ゲームウィンドウの高さ900
NUM_OF_BOMBS = 3



def check_bound(obj_rct: pg.Rect) -> tuple[bool, bool]:
    """
    オブジェクトが画面内or画面外を判定し，真理値タプルを返す関数
    引数：こうかとん，または，爆弾SurfaceのRect
    戻り値：横方向，縦方向のはみ出し判定結果（画面内：True／画面外：False）
    """
    yoko, tate = True, True
    if obj_rct.left < 0 or WIDTH < obj_rct.right:
        yoko = False
    if obj_rct.top < 0 or HEIGHT < obj_rct.bottom:
        tate = False
    return yoko, tate


class Bird:
    """
    ゲームキャラクター（こうかとん）に関するクラス
    """
    delta = {  # 押下キーと移動量の辞書
        pg.K_UP: (0, -5),
        pg.K_DOWN: (0, +5),
        pg.K_LEFT: (-5, 0),
        pg.K_RIGHT: (+5, 0),
    }

    def __init__(self, num: int, xy: tuple[int, int]):
        """
        こうかとん画像Surfaceを生成する
        引数1 num：こうかとん画像ファイル名の番号
        引数2 xy：こうかとん画像の位置座標タプル
        """
        self.img = pg.transform.rotozoom(  # 2倍に拡大
                pg.image.load(f"ex03/fig/{num}.png"), 
                0, 
                2.0)
        self.rct = self.img.get_rect()
        self.rct.center = xy

    def change_img(self, num: int, screen: pg.Surface):
        """
        こうかとん画像を切り替え，画面に転送する
        引数1 num：こうかとん画像ファイル名の番号
        引数2 screen：画面Surface
        """
        self.img = pg.transform.rotozoom(pg.image.load(f"ex03/fig/{num}.png"), 0, 2.0)
        screen.blit(self.img, self.rct)

    def update(self, key_lst: list[bool], screen: pg.Surface):
        """
        押下キーに応じてこうかとんを移動させる
        引数1 key_lst：押下キーの真理値リスト
        引数2 screen：画面Surface
        """
        sum_mv = [0, 0]
        for k, mv in __class__.delta.items():
            if key_lst[k]:
                sum_mv[0] += mv[0]
                sum_mv[1] += mv[1]
        self.rct.move_ip(sum_mv)
        if check_bound(self.rct) != (True, True):
            self.rct.move_ip(-sum_mv[0], -sum_mv[1]) 
        # 操作がない場合
        if np.array_equal(sum_mv, (0, 0)):
            kk_rotation = 270
            is_flip = True
        else:
            # 操作がある場合
            kk_rotation = math.atan2(abs(sum_mv[0]) * -1, sum_mv[1]) * 180 / np.pi
            is_flip = sum_mv[0] >= 0
        kk_img_roto = pg.transform.rotozoom(self.img, kk_rotation + 90, 1.0)
        screen.blit(pg.transform.flip(kk_img_roto, is_flip, False), self.rct)


class Bomb:
    """
    爆弾に関するクラス
    """
    
    BOMB_COLORS = (
        (255, 0, 0),
        (0, 255, 0),
        (0, 0, 255),
        (255, 255, 0),
        (255, 0, 255),
        (0, 255, 255)
        )
    BOMB_DIRECTIONS = (
        (5, 5),
        (0, 7.5),
        (7.5, 0),
        (-5, -5),
        (0, -7.5),
        (-7.5, 0)
    )
    
    def __init__(self, rad: int):
        """
        引数に基づき爆弾円Surfaceを生成する
        引数1 color：爆弾円の色タプル
        引数2 rad：爆弾円の半径
        """
        self.img = pg.Surface((2*rad, 2*rad))
        pg.draw.circle(self.img, random.choice(Bomb.BOMB_COLORS), (rad, rad), rad)
        self.img.set_colorkey((0, 0, 0))
        self.rct = self.img.get_rect()
        self.rct.center = random.randint(0, WIDTH), random.randint(0, HEIGHT)
        self.vx, self.vy = random.choice(Bomb.BOMB_DIRECTIONS)

    def update(self, screen: pg.Surface):
        """
        爆弾を速度ベクトルself.vx, self.vyに基づき移動させる
        引数 screen：画面Surface
        """
        yoko, tate = check_bound(self.rct)
        if not yoko:
            self.vx *= -1
        if not tate:
            self.vy *= -1
        self.rct.move_ip(self.vx, self.vy)
        screen.blit(self.img, self.rct)


class Beam:
    """
    ビームの関数
    """
    
    BEAM_SPEED = (5, 0)

    def __init__(self, koukaton: Bird) -> None:
        self.img = pg.image.load("ex03/fig/beam.png")
        self.rct = self.img.get_rect()
        krct = koukaton.rct.copy()
        self.rct.center = (krct.centerx + krct.width / 2 + 5, krct.centery + 5)

    def update(self, screen: pg.Surface):
        self.rct.move_ip(Beam.BEAM_SPEED)
        screen.blit(self.img, self.rct)





def main():
    bombList = [Bomb(10) for __ in range(NUM_OF_BOMBS)]
    beamList: list[Beam] = [] #画面内にあるビームのリスト
    pg.display.set_caption("たたかえ！こうかとん")
    screen = pg.display.set_mode((WIDTH, HEIGHT))    
    bg_img = pg.image.load("ex03/fig/pg_bg.jpg")
    bird = Bird(3, (900, 400))
    

    clock = pg.time.Clock()
    tmr = 0
    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return
            if event.type == pg.KEYDOWN and event.key == pg.K_SPACE:
                beamList.append(Beam(bird))

        key_lst = pg.key.get_pressed()
        screen.blit(bg_img, [0, 0])
        isHit = False
        for i in range(len(beamList)):
            for j in range(len(bombList)):
                if bombList[j] is None or beamList[i] is None:
                    continue
                if beamList[i].rct.colliderect(bombList[j].rct):
                    beamList[i] = None
                    bombList[j] = None
                    isHit = True
                    continue
            if beamList[i] is not None:
                beamList[i].update(screen)

        bombList = [a for a in bombList if a is not None]
        beamList = [b for b in beamList if b is not None]
        
        if isHit:
            bird.change_img(6, screen)
            pg.display.update()
            time.sleep(1)

        for b in bombList:
            if bird.rct.colliderect(b.rct):
                # ゲームオーバー時に，こうかとん画像を切り替え，1秒間表示させる
                bird.change_img(8, screen)
                pg.display.update()
                time.sleep(1)
                return
            else:
                b.update(screen)
        bird.update(key_lst, screen)
        pg.display.update()
        tmr += 1
        clock.tick(50)
 

if __name__ == "__main__":
    pg.init()
    main()
    pg.quit()
    sys.exit()
