import pygame
import sys
from pygame.locals import *

#Global Game Settings
width = 1024
height = 512
size = width, height
white = 255, 255, 255

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
		self.start = [x, y]
		self.velocity = [0, 0]
		self.speed = 90 #pixels a second
		self.movement = 0
		
	def reset(self):
		self.velocity = [0, 0]
		self.rect.centerx = self.start[0]
		self.rect.centery = self.start[1]

	def movement(self):
		pass

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

while True:
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			sys.exit()
		if event.type == pygame.KEYDOWN:
			keystate = pygame.key.get_pressed()
			if keystate[player1.up]:
				player1.velocity = [0, -1]
			elif keystate[player1.down]:
				player1.velocity = [0, 1]
			elif keystate[player1.right]:
				player1.velocity = [1, 0]
			elif keystate[player1.left]:
				player1.velocity = [-1, 0]

			if keystate[player2.up]:
				player2.velocity = [0, -1]
			elif keystate[player2.down]:
				player2.velocity = [0, 1]
			elif keystate[player2.right]:
				player2.velocity = [1, 0]
			elif keystate[player2.left]:
				player2.velocity = [-1, 0]

	for players in [player1, player2]:
		if not collision_check(players, width, height):
			players.rect = players.rect.move(players.velocity)
			
	screen.fill(white)
	screen.blit(player1.image, player1.rect)
	screen.blit(player2.image, player2.rect)
	pygame.display.flip()  
