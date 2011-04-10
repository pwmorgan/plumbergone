import pygame
import sys
from pygame.locals import *

#Global Game Settings
width = 1024
height = 512
size = width, height
white = 255, 255, 255
clock = pygame.time.Clock()
mainloop = True
FPS = 60
playtime = 0

#Grid Settings
cell_size = 35 #pixels
borderx = (width % cell_size) / 2 + cell_size
bordery = (height % cell_size) / 2 + cell_size
cellsx = width / cell_size
cellsy = height / cell_size
cell_count_x = (width - (2 * borderx)) / cell_size
cell_count_y = (height - (2 * bordery)) / cell_size
	
class gameboard():
	def __init__(self, x, y):
		self.grid = []
		self.new(x, y)
		self.previous = []
		self.lowest = []

	def new(self, x, y):
		for row in range(x):
			self.grid.append([])
			for column in range(y):
				self.grid[row].append(0)

	def add_pipe(self, player, x, y):
		row = (x - borderx) / cell_size
		column = (y - bordery) / cell_size
		self.grid[row][column] = player.number
				
	def collision(self, x, y):
		row = (x - borderx) / cell_size
		column = (y - bordery) / cell_size
		if row < 0:
			return True
		elif column < 0:
			return True
		elif row >= len(self.grid):
			return True
		elif column >= len(self.grid[row]):
			return True
		if self.grid[row][column] != 0:
			return True
		else:
		   	return False
                       
board = gameboard(cell_count_x, cell_count_y)

def collision_check(player, width, height):
	if 0 < player.rect.centerx < width:
		if 0 < player.rect.centery < height:
			return False
	return True        

	def store(self):
		gameboard.lowest = gameboard.previous[0:]
		gameboard.previous = gameboard.grid[0:]

#Image files
player_image = "media/player.bmp"
pipe_image = "media/pipe.bmp"

screen = pygame.display.set_mode(size)

class player():
	def __init__(self, number, x, y, image):
		self.number = number
		self.image = pygame.image.load(image)
		self.rect = self.image.get_rect()
		self.rect.centerx = x
		self.rect.centery = y
		self.x = x
		self.y = y
		self.velocity = [0, 0]
		self.speed = 85 #pixels a second
		
	def reset(self):
		self.velocity = [0, 0]
		self.rect.centerx = self.x
		self.rect.centery = self.y

	def movement(self, direction):
		self.velocity[0] = self.speed * direction[0]
		self.velocity[1] = self.speed * direction[1]

class pipes():
	def __init__(self):
		pass

#Establish players and starting positions
startx1 = borderx + (cell_size / 2)
starty1 = bordery + (cell_size / 2)
startx2 = width - startx1
starty2 = height - starty1
player1 = player(1, startx1, starty1, player_image)
player2 = player(2, startx2, starty2, player_image)

#Control Scheme
player1.up = K_UP
player1.down = K_DOWN
player1.left = K_LEFT
player1.right = K_RIGHT

player2.up = K_w
player2.down = K_s
player2.left = K_a
player2.right = K_d

while mainloop:
    #Calculate time.
	milliseconds = clock.tick(FPS)
	seconds = milliseconds / 1000.0
	playtime += seconds
	
	#Watch for key events.
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			sys.exit()
		if event.type == pygame.KEYDOWN:
			keystate = pygame.key.get_pressed()
			for players in [player1, player2]:
				if keystate[players.up]:
					players.movement([0, -1])
				elif keystate[players.down]:
					players.movement([0, 1])
				elif keystate[players.right]:
					players.movement([1, 0])
				elif keystate[players.left]:
					players.movement([-1, 0])

	#Display FPS
	pygame.display.set_caption("[FPS]: %.2f" % clock.get_fps())
	screen.fill(white)

	#Calculate player movement
	for players in [player1, player2]:
		if not board.collision(int(players.x), int(players.y)):
			players.x += players.velocity[0] * seconds
			players.y += players.velocity[1] * seconds
			players.rect.centerx = players.x
			players.rect.centery = players.y
		screen.blit(players.image, players.rect)

	pygame.display.flip()  
