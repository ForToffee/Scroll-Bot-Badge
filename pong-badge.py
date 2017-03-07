import random
import time
import RPi.GPIO as GPIO
import scrollphathd as sphd
from scrollphathd.fonts import font5x7, font3x5

BUTTONR_PIN = 7
BUTTONL_PIN = 35

BRIGHTNESS = 0.5

GPIO.setmode(GPIO.BOARD)
GPIO.setup(BUTTONR_PIN,GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(BUTTONL_PIN,GPIO.IN, pull_up_down=GPIO.PUD_UP)

PADDLE_FREQ = 2
BALL_FREQ = 3

class Paddle:
	def __init__(self,left_hand):
		if left_hand:
			self.x = 0
			self.pin = BUTTONL_PIN
		else:
			self.x = 16
			self.pin = BUTTONR_PIN
		self.y = 6
		self.score = 0
		self.cycle = 0
	
	def move(self):
		if self.cycle == PADDLE_FREQ:
			sphd.clear_rect(x=self.x ,y=self.y-1 ,width=1, height=3)
			if GPIO.input(self.pin) == GPIO.HIGH:
				self.y += 1
				if self.y > 7:
					self.y = 7
			else:
				self.y -= 1
				if self.y < -1:
					self.y = -1
			#print(self.pos)
			self.draw()
			self.cycle = 0
		self.cycle += 1
		
	def hit_check(self, ball):

		if (ball.x == 0 and ball.v_x < 0) or (ball.x ==16 and ball.v_x > 0):	#check direction of travel
			if ball.x == self.x:	#has the ball reached the line of the paddle
				if ball.y == self.y: #middle?
					return 1
				elif self.y + 1 >= ball.y >= self.y - 1:  #ends?
					return 2
				else:	#miss?
					return -1

		return 0	#ball still in play
		
	def draw(self):
		sphd.fill(brightness=BRIGHTNESS, x=self.x, y=self.y-1, width=1, height=3)

class Ball:
	def __init__(self):
		self.x = random.randint(4,12)
		self.y = random.randint(2,4)
		self.v_x = random.choice([-1,1])
		self.v_y = random.choice([-1,1])
		self.cycle = 0
		self.freq = BALL_FREQ

	def move(self):
		if self.cycle == self.freq:
			sphd.set_pixel(self.x, self.y, 0)
			self.x += self.v_x
			self.y += self.v_y
			
			if self.y <= 0 or self.y >= 6:
				self.v_y = self.v_y * -1

			if self.x <= 0:
				self.x = 0
			elif self.x >= 16:
				self.x = 16
				
			sphd.set_pixel(self.x, self.y, BRIGHTNESS)
			self.cycle = 0
			return True
		self.cycle += 1
		return False

	def hit_paddle(self, value):
		self.v_x = self.v_x * -1
		self.freq = BALL_FREQ
		if value == 2:
			self.freq -= 2

		if self.x <= 0:	#move ball in front of paddle
			self.x = 1
		elif self.x >= 16:
			self.x = 15
		sphd.set_pixel(self.x, self.y, BRIGHTNESS)
			
	def clear(self):
		sphd.set_pixel(self.x, self.y, 0)

def game_over(offset, win):

	sphd.set_pixel(x=offset + 2,y=1,brightness=BRIGHTNESS)
	sphd.set_pixel(x=offset + 6,y=1,brightness=BRIGHTNESS)
	sphd.set_pixel(x=offset + 4,y=3,brightness=BRIGHTNESS)

	if win:
		sphd.set_pixel(x=offset + 2,y=5,brightness=BRIGHTNESS)
		sphd.set_pixel(x=offset + 6,y=5,brightness=BRIGHTNESS)
		for x in range(3,6):
			sphd.set_pixel(x=offset + x,y=6,brightness=BRIGHTNESS)
	else:
		sphd.set_pixel(x=offset + 2,y=6,brightness=BRIGHTNESS)
		sphd.set_pixel(x=offset + 6,y=6,brightness=BRIGHTNESS)
		for x in range(3,6):
			sphd.set_pixel(x=offset + x,y=5,brightness=BRIGHTNESS)
	
		
padL = None
padR = None
ball = None

	
def run_game():
	sphd.clear()
	sphd.show()
	padL = Paddle(True)
	padR = Paddle(False)
	ball = Ball()
	
	win = False
	reset = False

	for n in range(3,0,-1):
		sphd.clear()
		sphd.write_string(str(n), x=(3 - n) * 5, y=3-n, font=font3x5, brightness=0.25)
		sphd.show()
		time.sleep(0.75)

		sphd.clear()
	sphd.write_string("GO! ", x=4, y=1, font=font3x5, brightness=0.5)
	sphd.show()
	time.sleep(0.75)
	sphd.clear()

	while not win:
		#draw divider
		for y in range(0,4):
			sphd.set_pixel(x=8,y=y * 2,brightness=BRIGHTNESS/4)
		
		#draw score bar
		if padL.score > 0:
			sphd.fill(brightness=BRIGHTNESS, x=7-padL.score, y=0, width=padL.score, height=1)
		if padR.score > 0:
			sphd.fill(brightness=BRIGHTNESS, x=10, y=0, width=padR.score, height=1)
	
		padL.move()
		padR.move()
		if ball.move():
		
			hit = padL.hit_check(ball)
			if hit > 0:
				ball.hit_paddle(hit)
			elif hit < 0:	#miss
				padR.score += 1
				win = (padR.score == 5)
				reset = True
			
			hit = padR.hit_check(ball)
			if hit > 0:
				ball.hit_paddle(hit)
			elif hit < 0:	#miss
				padL.score += 1
				win = (padL.score == 5)
				reset = True
			
		sphd.show()
		if win:
			sphd.clear()
			game_over(0,padL.score == 5)
			game_over(9,padR.score == 5)
			sphd.show()
			time.sleep(5)
			
		elif reset:
			time.sleep(1)
			ball.clear()
			ball = Ball()
			reset = False

		sphd.show()
		time.sleep(0.05)

sphd.rotate(180)
while True:
	sphd.clear()
	sphd.write_string("Carl Monk   @ForToffee   ", x=0, y=0, font=font5x7, brightness=BRIGHTNESS)
	while GPIO.input(BUTTONR_PIN) == GPIO.HIGH:
		sphd.show()
		sphd.scroll(1)
		time.sleep(0.05)
		
	run_game()
