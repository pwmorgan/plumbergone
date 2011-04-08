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

#Image files
player_image = "media/player.bmp"
pipe_image = "media/pipe.bmp"

screen = pygame.display.set_mode(size)

class player():
	def __init__(self, x, y, image):
		self.image = pygame.image.load(image)
		self.rect = self.image.get_rect()
		self.rect.centerx = x
		self.rect.centery = y
		self.x = x
		self.y = y
		self.velocity = [0, 0]
		self.speed = 80 #pixels a second
		
	def reset(self):
		self.velocity = [0, 0]
		self.rect.centerx = self.x
		self.rect.centery = self.y

	def movement(self, direction):
		self.velocity[0] = self.speed * direction[0]
		self.velocity[1] = self.speed * direction[1]

#Establish players and starting positions
player1 = player(35, 35, player_image)
player2 = player(990, 475, player_image)

#Control Scheme
player1.up = K_UP
player1.down = K_DOWN
player1.left = K_LEFT
player1.right = K_RIGHT

player2.up = K_w
player2.down = K_s
player2.left = K_a
player2.right = K_d

def collision_check(player, width, height):
	if 0 < player.rect.centerx < width:
		if 0 < player.rect.centery < height:
			return False
	return True

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
			if keystate[player1.up]:
				player1.movement([0, -1])
			elif keystate[player1.down]:
				player1.movement([0, 1])
			elif keystate[player1.right]:
				player1.movement([1, 0])
			elif keystate[player1.left]:
				player1.movement([-1, 0])

			if keystate[player2.up]:
				player2.movement([0, -1])
			elif keystate[player2.down]:
				player2.movement([0, 1])
			elif keystate[player2.right]:
				player2.movement([1, 0])
			elif keystate[player2.left]:
				player2.movement([-1, 0])

	pygame.display.set_caption("[FPS]: %.2f" % clock.get_fps())
	screen.fill(white)
	for players in [player1, player2]:
		if not collision_check(players, width, height):
			#players.movement(seconds)
			players.x += players.velocity[0] * seconds
			players.y += players.velocity[1] * seconds
			players.rect.centerx = players.x
			players.rect.centery = players.y
		#if I include the below line in the if statment, I can cut out the player art when they crash
		screen.blit(players.image, players.rect)
	pygame.display.set_caption("[FPS]: %.2f." % clock.get_fps())
	pygame.display.flip()  
