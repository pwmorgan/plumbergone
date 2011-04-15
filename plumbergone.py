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

#Image files
def load_image(image):
	"""Load the image and convert it to a surface."""
	image = os.path.join(main_dir, 'media', image)
	surface = pygame.image.load(image)
	surface = surface.convert()
	surface.set_colorkey(white)
	return surface

def load_pipes(style, direction, filetype):
	"""Load all the pipes with the specific styles and orientations."""
	image = "pipes" + "_" + style + "_" + direction + "." + filetype
	return load_image(image)

def round(decimal):
	"""Convert float to integer, but round up or down instead of floor rounding."""
	integer = int(decimal)
	if (decimal - integer) >= .5:
		integer += 1
		return integer
	else:
		return integer

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

	def add_pipe(self, player_number, row, column):
		try:
			self.grid[row][column] = player_number #add additional details?
		except IndexError:
			#Out of list range means no pipe gets added.
			pass
				
	def store(self):
		gameboard.lowest = deepcopy(gameboard.previous)
		gameboard.previous = deepcopy(gameboard.grid)

class Player():
	def __init__(self, number, style, x, y, image, gameboard, previous_entry):
		#Initial player 
		self.number = number
		self.style = style
		self.score = 0
		self.collision = False

		#Load images
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
		self.currentcell = gameboard.row(self.y), gameboard.column(self.x)
		self.previouscell = self.currentcell
		self.entry = 'center'
		self.exit = previous_entry

	def reset(self):
		self.velocity = [0, 0]
		self.rect.centerx = self.x
		self.rect.centery = self.y

	def movement(self, direction):
		"""Calculates the x and y directional velocities."""
		self.velocity[0] = self.speed * direction[0]
		self.velocity[1] = self.speed * direction[1]

	def record_entry(self):
		opposite = {'up':'down', 'down':'up', 'left':'right', 'right':'left'}
		#[0] = row, [1] = column
		if self.previouscell[0] > self.currentcell[0]:
			self.exit = self.entry
			self.entry = 'down'
		elif self.previouscell[0] < self.currentcell[0]:
			self.exit = self.entry
			self.entry = 'up'
		elif self.previouscell[1] > self.currentcell[1]:
			self.exit = self.entry
			self.entry = 'right'
		elif self.previouscell[1] < self.currentcell[1]:
			self.exit = self.entry
			self.entry = 'left'
		else:
			pass
			
	def check_collision(self, x, y, gameboard):
		row = gameboard.row(y)
		column = gameboard.column(x)
		if column < 0:
			return True
		elif row < 0:
			return True
		elif row >= len(gameboard.grid):
			return True
		elif column >= len(gameboard.grid[row]):
			return True
		elif gameboard.grid[row][column] != 0:
			return True
		else:
		   	return False

	def check_pipe(self, x, y, gameboard):

		#Set the current row and column
		row = gameboard.row(y)
		column = gameboard.column(x)
		self.currentcell = (row, column)
		opposite = {'up':'down', 'down':'up', 'left':'right', 'right':'left'}
	
		#Check for collision
		if self.collision:
			#self.record_entry()
			self.exit = 'center'
			#Decide if the end pipe should go in the current cell or the previous cell
			#Add end pipe
			board.add_pipe(self.number, row, column) #add entry, exit?
			Pipe(gameboard.pos(self.previouscell[0], self.previouscell[1]),
				 self.style, self.entry + self.exit)
			print self.score

		#Check if row and column are same
		elif self.currentcell != self.previouscell:
			#[0] = row, [1] = column
			self.record_entry()
			#Add pipe in previous cell
			#Pipe(gameboard.pos(self.previouscell), self.style, self.entry + self.exit)
			board.add_pipe(self.number, self.previouscell[0], self.previouscell[1]) #add entry, exit?
			Pipe(gameboard.pos(self.previouscell[0], self.previouscell[1]),
				 self.style, self.exit + self.entry)
			self.score += 1
			self.previouscell = (row, column)
		
class Pipe(pygame.sprite.Sprite):
	images = {}
	def __init__(self, pos, style, direction):
		pygame.sprite.Sprite.__init__(self, self.containers)
		self.image = self.images[style][direction]
		self.rect = self.image.get_rect(topleft=pos)
		#print "New", direction, "pipe at", pos[0], pos[1]

class Score(pygame.sprite.Sprite):
	def __init__(self, players):
		self.players = players
		pygame.sprite.Sprite.__init__(self)
		self.font = pygame.font.Font(None, 20)
		self.font.set_italic(1)
		self.color = Color('black')
		self.update()
		self.rect = self.image.get_rect().move(25, 25)
	
	def update(self):
		msg = ""
		i = 0
		for players in self.players:
			msg += "Player %s: %d . " % (players.number, players.score)
			i += 1
		self.image = self.font.render(msg, 0, self.color)

def main():
	pass

pygame.init()

board = gameboard(cell_count_x, cell_count_y)
screen = pygame.display.set_mode(size)

#Draw the background
background_img = load_image('background1.png')
bg_rect = Rect(0, 0, width, height)
background = pygame.Surface((width, height))
background.blit(background_img, (0, 0))
screen.blit(background, (0,0))
#pygame.display.flip()

#Establish players and starting positions
player_image = "player.bmp"
startx1 = borderx + (cell_size / 2)
starty1 = bordery + (cell_size / 2)
startx2 = width - startx1
starty2 = height - starty1
player1 = Player(1, '1', startx1, starty1, player_image, board, 'left')
player2 = Player(2, '2', startx2, starty2, player_image, board, 'right')
playerlist = [player1, player2]

#Control Scheme
player2.up = K_UP
player2.down = K_DOWN
player2.left = K_LEFT
player2.right = K_RIGHT

player1.up = K_w
player1.down = K_s
player1.left = K_a
player1.right = K_d

#def load_pipes(style, direction, filetype):
pipe_styles = ['1', '2']

for style in pipe_styles:
	Pipe.images[style] = {}
	for pipe_type in image_list:
		Pipe.images[style][pipe_type] = load_pipes(style, pipe_type, 'png')

	secondary = other_images.keys()
	for key in secondary:
		Pipe.images[style][key] = Pipe.images[style][other_images[key]]

pipes = pygame.sprite.Group()
all = pygame.sprite.Group()

Pipe.containers = pipes, all
Score.containers = all

#Set up score
"""
if pygame.font:
	all.add(Score())
"""

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
			#if keystate[K_g]:
				#print board.grid

	#Display FPS
	pygame.display.set_caption("[FPS]: %.2f" % clock.get_fps())

	#Calculate player movement for each player.
	for player in playerlist:
		#Check if player does not move.
		if player.collision == False:
			#Move abstract value
			player.x += player.velocity[0] * seconds
			player.y += player.velocity[1] * seconds
			#Convert position to integer
			player.roundx = round(player.x)
			player.roundy = round(player.y)
			#Move art to pixels
			player.rect.centerx = player.roundx
			player.rect.centery = player.roundy
			screen.blit(player.image, player.rect)
			#Check for collisions
			player.collision = player.check_collision(player.roundx, player.roundy, board)
			#Check for pipe adds (collision pipe versus normal pipe)
			player.check_pipe(player.roundx, player.roundy, board)
			
	#Refresh screen and draw all the dirty rects.
	pygame.display.flip()  
	screen.blit(background, bg_rect)
	#screen.fill(white)
	dirty = all.draw(screen)
	pygame.display.update(dirty)

"""
if __name__ == '__main__':
	main()
"""
