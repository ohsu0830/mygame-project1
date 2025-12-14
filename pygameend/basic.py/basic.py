from tkinter import *
import random
import time
import pygame
import os

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
IMG_DIR = os.path.join(PROJECT_ROOT, "image")


class LoveBulletAdventure:
    def __init__(self):
        self.window = Tk()
        self.window.title("꽃보다 소중한 짝사랑 지키자! 💖")
        self.window.geometry("800x600")
        self.canvas = Canvas(self.window, width=800, height=600)
        self.canvas.pack()

        self.name = ""
        self.get_name_screen()

    # ================= 배경 꽉 채우기 (Stage2, 엔딩 전용) =================
    def draw_full_background(self, bg_image):
        w = bg_image.width()
        h = bg_image.height()
        for x in range(0, 800, w):
            for y in range(0, 600, h):
                self.canvas.create_image(x, y, anchor=NW, image=bg_image)

    # 이름
    def get_name_screen(self):
        self.canvas.delete("all")
        bg = PhotoImage(file=os.path.join(IMG_DIR, "background111.png"))
        self.canvas.bg = bg
        self.canvas.create_image(0, 0, anchor=NW, image=bg)

        self.canvas.create_text(400,130,text="주인공 이름을 입력하세요",
                                font=("Arial",24,"bold"),fill="white")

        self.name_entry = Entry(self.window, font=("Arial",18))
        self.name_entry.place(relx=0.5, rely=0.40, anchor=CENTER)

        self.start_btn = Button(self.window, text="시작!", font=("Arial",16),
                                command=self.show_manual)
        self.start_btn.place(relx=0.5, rely=0.52, anchor=CENTER)

    # 설명서
    def show_manual(self):
        self.name = self.name_entry.get() or "주인공"
        self.name_entry.place_forget()
        self.start_btn.place_forget()

        self.canvas.delete("all")
        bg = PhotoImage(file=os.path.join(IMG_DIR, "background111.png"))
        self.canvas.bg = bg
        self.canvas.create_image(0,0,anchor=NW,image=bg)

        self.canvas.create_rectangle(120,120,680,480,
                                     fill="white", stipple="gray50", outline="black")

        manual_part1 = """← → : 움직이기
Space : 하트 발사 (1초에 한 번)

적 점수:
1점: 고백 편지 도둑 (1초마다 등장)
5점: 고백 실패 요정 (5초마다 등장)
"""
        red_text1 = "10점: 전썸의 잔상 (10초마다 등장)"
        red_text2 = "*주의: 사실 전썸남은 없었다... 흑역사라 안 보임!*"
        manual_part2 = """50점: 짝사랑의 정령 (25초마다 등장)

목표:
1스테이지 → 150점
2스테이지 → 300점
행운을 빌지!
"""
        self.canvas.create_text(400, 210, text=manual_part1,
                                font=("Arial", 16), fill="deeppink", justify="left")
        self.canvas.create_text(400, 285, text=red_text1,
                                font=("Arial", 16), fill="deeppink")
        self.canvas.create_text(400, 310, text=red_text2,
                                font=("Arial", 16), fill="red")
        self.canvas.create_text(400, 405, text=manual_part2,
                                font=("Arial", 16), fill="deeppink")

        self.window.after(3500, self.start_game)

    # 게임 시작
    def start_game(self):
        self.canvas.delete("all")

        self.bg1 = PhotoImage(file=os.path.join(IMG_DIR, "background111.png"))
        self.bg2 = PhotoImage(file=os.path.join(IMG_DIR, "background2.gif"))
        self.end_bg = PhotoImage(file=os.path.join(IMG_DIR, "background3.png"))

        # 주인공 캐릭터 1.6배 확대 (8배 확대 후 5배 축소)
        player_img_original = PhotoImage(file=os.path.join(IMG_DIR, "Girl.png"))
        self.player_img = player_img_original.zoom(8, 8).subsample(5, 5)
        self.bullet_img = PhotoImage(file=os.path.join(IMG_DIR, "heart.png"))

        # 1점 적 이미지 1/2 크기로 축소
        enemy1_img_original = PhotoImage(file=os.path.join(IMG_DIR, "Hat_man1.png"))
        self.enemy_imgs = {
            1: enemy1_img_original.subsample(2, 2),
            5: PhotoImage(file=os.path.join(IMG_DIR, "5s.png")),
            10: PhotoImage(file=os.path.join(IMG_DIR, "10s.png")),
            50: PhotoImage(file=os.path.join(IMG_DIR, "50s.png"))
        }

        self.player_x = 380
        self.player_y = 500

        self.bullets = []
        self.enemies = []

        self.score = 0
        self.time_left = 180

        self.spawn_times = {1:1, 5:5, 10:10, 50:25}
        self.last_spawn = {t: time.time() for t in self.spawn_times}

        self.last_shot = 0

        self.enemy_lines = {
            1:["이 편지 내 거야!","넌 평생 고백 못해!","너는 그 애와 어울리지 않아!",
               "넌 바보군 크흑","고백은 포기하도록!","히히! 마음 먼저 가져간다~",
               "사랑은 타이밍이라던데? 넌 늦었어!","편지 없어져도 울진 않겠지?",
               "몰래 가져가볼까~?"],
            5:["고백…실패…",
               "남자는 좋아하는 여자 앞에성 그냥이라고는 없어. 언제나 반드시 이유가 있지.",
               "떨려서 말 못 했지? 괜찮아~ 난 너 같은 애 전용 요정이거든!",
               "네 용기는 0, 실패 확률은 100%! 완벽하다!"],
            10:["잊은 줄 알았어…","썸…이었나?",
                "하얀 천이랑 바람만 있으면 어디든 갈 수 있어",
                "나도 남자야! 너란 여자를 죽도록 안고싶어하는 남자 맞다구!!"],
            50:["더 이상 피하지 않으려고, 한 번 포기하면 얼마나 후회막급인지 누구덕분에 알게됐거든",
                "네 마음… 따뜻하구나","넌 가능성이 있다"]
        }

        self.keys = {}
        self.window.bind("<KeyPress>", self.key_down)
        self.window.bind("<KeyRelease>", self.key_up)

        self.stage = 1
        self.show_stage_text()

    # 스테이지 시작
    def show_stage_text(self):
        self.canvas.delete("all")

        if self.stage == 1:
            self.canvas.create_image(0,0,anchor=NW,image=self.bg1)
        else:
            self.draw_full_background(self.bg2)

        self.canvas.create_text(400,80,text=f"🌟 Stage {self.stage} 🌟",
                                font=("Arial",28,"bold"),fill="yellow")
        self.window.after(1000, self.run_stage)

    # 스테이지 진행
    def run_stage(self):
        self.canvas.delete("all")

        if self.stage == 1:
            self.canvas.create_image(0,0,anchor=NW,image=self.bg1)
        else:
            self.draw_full_background(self.bg2)

        self.score_text = self.canvas.create_text(700,30,
            text=f"Score: {self.score}", font=("Arial",16,"bold"), fill="white")
        self.time_text = self.canvas.create_text(80,30,
            text=f"Time: {int(self.time_left)}", font=("Arial",16,"bold"), fill="white")

        self.player = self.canvas.create_image(self.player_x, self.player_y,
                                               anchor=NW, image=self.player_img)
        self.update_game()

    # 키 입력
    def key_down(self, e): self.keys[e.keysym] = True
    def key_up(self, e): self.keys[e.keysym] = False

    # 총알
    def shoot(self):
        now = time.time()
        if now - self.last_shot < 1: return
        self.last_shot = now
        b = self.canvas.create_image(self.player_x+20, self.player_y,
                                     anchor=NW, image=self.bullet_img)
        self.bullets.append(b)

    # 적 생성
    def spawn_enemy(self, s):
        y = random.randint(40,420)
        img = self.enemy_imgs[s]
        self.enemies.append([self.canvas.create_image(800,y,anchor=NW,image=img),
                              800,y,s])

    # 충돌
    def collide(self,a,b):
        if not self.canvas.bbox(a) or not self.canvas.bbox(b): return False
        ax1,ay1,ax2,ay2 = self.canvas.bbox(a)
        bx1,by1,bx2,by2 = self.canvas.bbox(b)
        return not (ax2<bx1 or bx2<ax1 or ay2<by1 or by2<ay1)

    # 게임 업데이트
    def update_game(self):
        if self.keys.get("Left"): self.player_x -= 10
        if self.keys.get("Right"): self.player_x += 10
        if self.keys.get("space"): self.shoot()

        self.player_x = max(0,min(750,self.player_x))
        self.canvas.coords(self.player,self.player_x,self.player_y)

        self.time_left -= 1/30
        self.canvas.itemconfig(self.time_text,text=f"Time: {int(self.time_left)}")

        now = time.time()
        for t in self.spawn_times:
            if now - self.last_spawn[t] > self.spawn_times[t]:
                self.spawn_enemy(t)
                self.last_spawn[t] = now

        for b in self.bullets[:]:
            self.canvas.move(b,0,-12)
            if self.canvas.bbox(b)[3] < 0:
                self.canvas.delete(b)
                self.bullets.remove(b)

        for e in self.enemies[:]:
            img,x,y,s = e
            x -= 4
            e[1] = x
            self.canvas.coords(img,x,y)

            for b in self.bullets[:]:
                if self.collide(img,b):
                    self.score += s
                    self.canvas.itemconfig(self.score_text,
                                           text=f"Score: {self.score}")
                    txt = self.canvas.create_text(x,y,
                        text=random.choice(self.enemy_lines[s]),
                        font=("Arial",12,"bold"),fill="black")
                    self.window.after(800,lambda t=txt:self.canvas.delete(t))
                    self.canvas.delete(img)
                    self.canvas.delete(b)
                    self.enemies.remove(e)
                    self.bullets.remove(b)
                    break

        if self.stage == 1 and self.score >= 150:
            self.stage = 2
            self.show_stage_text()
            return
        if self.stage == 2 and self.score >= 300:
            self.show_ending(); return
        if self.time_left <= 0:
            self.show_ending(); return

        self.window.after(33,self.update_game)

    # 엔딩
    def show_ending(self):
        self.canvas.delete("all")
        self.draw_full_background(self.end_bg)

        self.canvas.create_rectangle(80,80,720,460,
            fill="white",stipple="gray50",outline="yellow",width=4)

        ending_text = (
            f"끝! {self.name}, 잘했어!\n"
            "수많은 방해와 속에서도…\n"
            "넌 결국 사랑을 지켜냈다.\n\n"
            "하트에 너의 진심이 담겨 있었어.\n"
            "실패할 뻔한 순간도 있었지만,\n"
            "결국 너의 용기는 모든 위험을 이겼지.\n\n"
            "…솔직히 말해도 될까?\n"
            "너 이렇게 사랑 잘하면 반칙이야.\n"
            "앞으로도 누군가의 마음을 따뜻하게 지켜줄\n"
            "사랑의 수호자는 바로 너일 것 같네ㅎ."
        )

        self.canvas.create_text(400,270,text=ending_text,
            font=("Arial",18,"bold"),fill="pink",justify="center",width=580)

        self.canvas.create_text(400,520,text="클릭하면 다시 시작!",
            font=("Arial",22,"bold"),fill="black")

        self.canvas.bind("<Button-1>", self.restart)

    def restart(self,event):
        self.canvas.unbind("<Button-1>")
        self.get_name_screen()


if __name__ == "__main__":
    LoveBulletAdventure().window.mainloop()
            