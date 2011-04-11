#!/usr/bin/env python

#Import Modules
import os
import sys
import pygame
from pygame.locals import *
from copy import deepcopy

#Import game settings       
from image_files import image_list, other_images 

#Global Game Settings
main_dir = os.path.split(os.path.abspath(__file__))[0]
width = 1024
height = 512
size = width, height
white = 255, 255, 255
black = 0, 0, 0
clock = pygame.time.Clock()
mainloop = True
FPS = 60
playtime = 0

#Grid Settings
cell_size = 35 #pixels
borderx = (width % cell_size) / 2 + cell_size
bordery = (height % cell_size) / 2 + cell_size
cell_count_x = (width - (2 * borderx)) / cell_size
cell_count_y = (height - (2 * bordery)) / cell_size

class gameboard():
	def __init__(self, x, y):
		self.grid = []
		self.new(x, y)
		self.previous = []
		self.lowest = []

	def new(self, x, y):
		for row in range(y):
			self.grid.append([])
			for column in range(x):
				self.grid[row].append(0)
	
	def pos(self, row, column):
		x = borderx + column * cell_size
		y = bordery + row * cell_size
		return x, y

	def row(self, y):
		return int((y - bordery) / cell_size)

	def column(self, x):
		return int((x - borderx) / cell_size)

	def add_pipe(self, player, column, row, entry, exit):
		self.grid[row][column] = [player, entry+exit]
		Pipe(self.pos(row, column), entry+exit)
		#player.lastpipe = (row, column)
		#print player, column, row, entry+exit
				
	def collision(self, x, y):
		row = (x - borderx) / cell_size
		column = (y - bordery) / cell_size
		if column < 0:
			return True
		elif row < 0:
			return True
		elif column >= len(self.grid):
			return True
		elif row >= len(self.grid[column]):
			return True
		if self.grid[column][row] != 0:
			return True
		else:
		   	return False
                       
	def store(self):
		gameboard.lowest = deepcopy(gameboard.previous)
		gameboard.previous = deepcopy(gameboard.grid)

board = gameboard(cell_count_x, cell_count_y)

#Image files
def load_image(image):
	"""Load the image and convert it to a surface."""
	image = os.path.join(main_dir, 'media', image)
	surface = pygame.image.load(image)
	return surface.convert()

def load_pipes(style, direction, filetype):
	image = "pipes" + "_" + style + "_" + direction + "." + filetype
	return load_image(image)

#screen = pygame.display.set_mode(size)

class player():
	def __init__(self, number, x, y, image, previous_entry):
		self.number = number
		#self.image = pygame.image.load(image)
		#self.image = pygame.Surface.convert(self.image)
		self.image = load_image(image)
		self.image.set_colorkey(white)

		#Screen placement
		self.rect = self.image.get_rect()
		self.rect.centerx = x
		self.rect.centery = y
		self.x = x
		self.y = y
		self.velocity = [0, 0]
		self.speed = 85 #pixels a second

		#Grid placement
		self.entry = "center"
		self.previous_entry = previous_entry
		self.previous_column = board.column(self.x)
		self.previous_row = board.row(self.y)
		self.current_column = self.previous_column
		self.current_row = self.previous_row

	def reset(self):
		self.velocity = [0, 0]
		self.rect.centerx = self.x
		self.rect.centery = self.y

	def movement(self, direction):
		"""Calculates the x and y directional velocities."""
		self.velocity[0] = self.speed * direction[0]
		self.velocity[1] = self.speed * direction[1]

	def change_grid(self, direction, column, row):
		self.previous_entry = self.entry
		self.entry = direction
		board.add_pipe(self.number, column,
		   			   row, self.previous_entry, 
		   			   self.entry)
		self.lastpipe = (column, row)
		self.previous_column = self.current_column
		self.previous_row = self.current_row

	def status(self, collision):
		"""Status checks the column and rows for changes, then places pipes."""
		self.current_column = board.column(self.x)
		self.current_row = board.row(self.y)

		if collision:
			if self.lastpipe:
				pass
			else:
				self.lastpipe = (self.current_column, self.current_row)
			self.entry = 'center'
			board.add_pipe(self.number, self.lastpipe[0],
						   self.lastpipe[1], self.previous_entry,
						   self.entry)

		else:
			if self.previous_column != self.current_column:
				if self.previous_column > self.current_column:
					self.change_grid('right', self.previous_column, self.current_row)
				else:
					self.change_grid('left', self.previous_column, self.current_row)

			if self.previous_row != self.current_row:
				if self.previous_row > self.current_row:
					self.change_grid('down', self.current_column, self.previous_row)
				else:
					self.change_grid('up', self.current_column, self.previous_row)

class Pipe(pygame.sprite.Sprite):
	images = {}
	def __init__(self, pos, direction):
		pygame.sprite.Sprite.__init__(self, self.containers)
		self.image = self.images[direction]
		self.rect = self.image.get_rect(topleft=pos)
		#print "New pipe at", pos[0], pos[1]

"""
	
class Score(pygame.sprite.Sprite):
	def __init__(self):
		pygame.sprite.Sprite.__init__(self)
		self.font = pygame.font.Font(None, 20)
		self.color = black
		self.update()
		self.rect = self.image.get_rect().move(0, 0)
"""

def main():
	"""
	pygame.init()
	"""
	pass

screen = pygame.display.set_mode(size)

#Establish players and starting positions
player_image = "player.bmp"
startx1 = borderx + (cell_size / 2)
starty1 = bordery + (cell_size / 2)
startx2 = width - startx1
starty2 = height - starty1
player1 = player(1, startx1, starty1, player_image, 'left')
player2 = player(2, startx2, starty2, player_image, 'right')
playerlist = [player1, player2]

#Control Scheme
player1.up = K_UP
player1.down = K_DOWN
player1.left = K_LEFT
player1.right = K_RIGHT

player2.up = K_w
player2.down = K_s
player2.left = K_a
player2.right = K_d

screen.fill(white)

#def load_pipes(style, direction, filetype):
pipe_styles = ['1',]

for style in pipe_styles:
	for pipe_type in image_list:
		Pipe.images[pipe_type] = load_pipes(style, pipe_type, 'png')
        #Pipe.images[pipe_type].set_colorkey(white)
secondary = other_images.keys()

for key in secondary:
	Pipe.images[key] = Pipe.images[other_images[key]]

pipes = pygame.sprite.Group()
all = pygame.sprite.Group()

Pipe.containers = pipes, all

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
			for players in playerlist:
				if keystate[players.up]:
					players.movement([0, -1])
				elif keystate[players.down]:
					players.movement([0, 1])
				elif keystate[players.right]:
					players.movement([1, 0])
				elif keystate[players.left]:
					players.movement([-1, 0])
			if keystate[K_g]:
				print board.grid

	#Display FPS
	pygame.display.set_caption("[FPS]: %.2f" % clock.get_fps())

	#Calculate player movement
	for players in playerlist:
		collision = False
		if not board.collision(int(players.x), int(players.y)):
			players.x += players.velocity[0] * seconds
			players.y += players.velocity[1] * seconds
			players.rect.centerx = players.x
			players.rect.centery = players.y
			screen.blit(players.image, players.rect)
		else:
			collision = True
		players.status(collision)
		#screen.blit(players.image, players.rect)
	pygame.display.flip()  
	
	screen.fill(white)
	dirty = pipes.draw(screen)
	pygame.display.update(dirty)

"""
if __name__ == '__main__':
	main()
"""
