import pygame
import sys
from pygame.locals import *

#Settings
width = 1024
height = 512
size = width, height
speed = 90.0 #pixels per second
velocity = 0, 0
white = 255, 255, 255

#Image files
player_image = "media/player.bmp"
pipe_image = "media/pipe.bmp"

screen = pygame.display.set_mode(size)

class player():
	pass

player1 = pygame.image.load(player_image)
player1_box = player1.get_rect()

player2 = pygame.image.load(player_image)
player2_box = player2.get_rect()

def movement(direction, speed):
	velocity = speed / 90.0 #pixels per second / frames per second
	return direction[0] * velocity, direction[1] * velocity		

while True:
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			sys.exit()
		if event.type == pygame.KEYDOWN:
			keystate = pygame.key.get_pressed()
			if keystate[K_RIGHT]:
				velocity = movement([1,0], speed)
			elif keystate[K_LEFT]:
				velocity = movement([-1,0], speed)
			elif keystate[K_UP]:
				velocity = movement([0,-1], speed)
			elif keystate[K_DOWN]:
				velocity = movement([0,1], speed)

	player1_box = player1_box.move(velocity)
	
	screen.fill(white)
	screen.blit(player1, player1_box)
	screen.blit(player2, player2_box)
	pygame.display.flip()  
