#!/usr/bin/env python

"""
PLUMBERGONE
Patrick Morgan
p.w.morgan@gmail.com
April 2011

An arcade game where you lay down pipes across a variety of environments,
competing for the glorious job of professional plumber. Features art by
Royce Mclean and sounds from [source].  Written in python using the
pygame framework.
"""


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
FPS = 60
p1score = 0
p2score = 0
level = 0

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


#Load level files
def load_level(level_file):
	"""Load the image and convert it to a surface."""
	full_path = os.path.join(main_dir, 'levels', level_file)
	raw_level = file(full_path, 'r')
	done = False
	#Parse the raw level file
	main_layer = [] #Top art level with collisions
	sub_layer = [] #Bottom level without collisions
	while not done:	
		line = raw_level.readline()
		if line[:5] == 'LEVEL':
			line = raw_level.readline()
			while line[:3] != 'END':			
				row = line.split(' ')
				main_layer.append(row)
				line = raw_level.readline()
		elif line[:8] == 'SUBLEVEL':
			line = raw_level.readline()
			while line[:3] != 'END':			
				row = line.split(' ')
				sub_layer.append(row)
				line = raw_level.readline()
			done = True
	#Scrub the gameboard lists
	for board in (main_layer, sub_layer):
		for row in range(len(board)):
			for cell in range(len(board[row])):
				board[row][cell] = board[row][cell][0] 
	raw_level.close()
	return main_layer, sub_layer


#Sound files
class dummysound():
	"""Class that placeholds and plays an empty sound."""
	def play(self): 
		pass


def load_sound(sound):
	"""Load a sound and add it to the mixer."""
	if not pygame.mixer: 
		return dummysound()
	sound = os.path.join(main_dir, 'data', sound)
	try:
		mixed_sound = pygame.mixer.Sound(sound)
		return mixed_sound
	except pygame.error:
		print ('Warning: unable to load %s.' % sound)
	return dummysound()


#Utility Functions
def round(decimal):
	"""Round a float instead of truncating the decimal."""
	integer = int(decimal)
	if (decimal - integer) >= .5:
		integer += 1
		return integer
	else:
		return integer


#UI Classes
class Button():
	"""The button class controls the different states of the button image as well as the click event."""
	def __init__(self, x, y, up, hover, down):
		self.up = load_image(up)
		self.hover = load_image(hover)
		self.down = load_image(down)
		self.rect = self.down.get_rect()
		self.rect.bottomleft = (y, x)
		self.image = self.up
		self.clickrect = self.rect #Defaults to containing the rect as the clickable area.

	def status(self, screen, pos, click):
		"""Check whether the button has been clicked."""
		screen.blit(self.up, self.rect)
		if self.clickrect.top < pos[1] < self.clickrect.bottom:
			if self.clickrect.left < pos[0] < self.clickrect.right:
				self.image = self.hover
				if click:
					self.on_click()
					#Return True if a click is detected.
					return True
			else:
				self.image = self.up
		else:
			self.image = self.up

        #Return false if no click is detected
		return False
	
	def on_click(self):
		"""Play the click animation and run the button action."""
		self.image = self.down
		self.action(self)
				

class Options():
	pass


#Gameplay Classes
class gameboard():
	"""The gameboard class contains logic for storing the current game state and for detecting collisions. Also contains functions for determining positions of players."""

	def __init__(self, x, y):
		self.x = x
		self.y = y
		self.new()

	def create_level(self, level):
		level_key = {'V':'pipes_3_upup.png',  #vertical upup pipe
					 'H':'pipes_3_leftleft.png',  #horizontal leftleft pipe
					 'U':'pipes_3_upcenter.png',  #upcenter pipe
					 'D':'pipes_3_downcenter.png',  #downcenter pipe
					 'L':'pipes_3_leftcenter.png',  #leftcenter pipe
					 'R':'pipes_3_rightcenter.png',  #rightcenter pipe
					 'C':'pipes_3_centercenter.png',  #centercenter pipe
					 'v':'gates_upup.png',  #vertical gate
					 'h':'gates_leftleft.png',  #horizontal gate
					 'X':'blocks_01.png',  #random collision block
					 '1':'powerups_01.png',  #powerup 1
					 '2':'powerups_02.png',  #powerup 2
					 '3':'powerups_03.png',  #powerup 3
					 'a':'doodads_01.png',  #doodad 1
					 #'b':'doodads_02.png',  #doodad 2
					 #'c':'doodads_03.png',  #doodad 3
					 }

		#Load the current level as a list of layers
		layers = load_level('level%d.txt' % level) 
		#Grids that contain a full representation of each layer.
		self.main_layer = layers[0]
		self.sub_layer = layers[1] 
		#Empty lists for the active images on each layer.
		self.active = []
		#Convert layers from abstract data to the images for loading.
		for layer in layers:
			for row in range(len(layer)):
				for col in range(len(layer[row])):
					if layer[row][col] != '0':
						key = layer[row][col]
						if layer == self.sub_layer:
							x, y = self.pos(row-1, col-1)
						else:
							x, y = self.pos(row, col)
							#Add a collision obj on grid.
							self.grid[row][col] = 'X'
						layer[row][col] = Doodad(level_key[key], x, y)
						self.active.append(layer[row][col])

	def new(self):
		"""Create a new gameboard using row and column count."""
		x = self.x
		y = self.y
		self.grid = []
		for row in range(y):
			self.grid.append([])
			for column in range(x):
				self.grid[row].append(0)
		self.create_level(level)
	
	def pos(self, row, column):
		"""Given a row and column, this returns a tuple of x and y coords."""
		x = borderx + column * cell_size
		y = bordery + row * cell_size
		return x, y

	def row(self, y):
		"""Given a y coordinate, this returns the row of the coord."""
		return int((y - bordery) / cell_size)

	def column(self, x):
		"""Given a x coordinate, this returns the column of the coord."""
		return int((x - borderx) / cell_size)

	def add_pipe(self, player_number, row, column):
		try:
			self.grid[row][column] = player_number #add additional details?
		except IndexError:
			#Out of list range means no pipe gets added.
			pass
				
	def store(self):
		self.lowest = deepcopy(self.previous)
		self.previous = deepcopy(self.grid)
		self.new()

	def gamestate(self):
		pass

class Doodad():
	"""Adds an art item to the screen with an image file and x,y coord."""
	def __init__(self, image, x, y):
		self.image = load_image(image)
		self.image.set_colorkey(white)

		#Screen placement
		self.rect = self.image.get_rect()
		self.rect.topleft = x, y

class Player():
	"""The Player class contains all the attributes of the player's object
	as well as its position, speed, and score."""

	def __init__(self, number, style, x, y, score, 
				 image, gameboard, previous_entry):
		"""When initializing a player class, you need the player number, pipe
		sytle, x and y coordinates, player image, the gameboard, and which
		direction the first player pipe should come from."""

		#Initial player 
		self.number = number
		self.style = style
		self.score = score
		self.collision = False
		self.AI = False

		#Load images
		self.image = load_image(image)
		self.image.set_colorkey(white)

		#Screen placement
		self.rect = self.image.get_rect()
		self.start = [x, y]
		self.rect.centerx = x
		self.rect.centery = y
		#X and Y are the absolute values.  They get converted
		#to integers so the rect can be moved to pixel locations.
		self.x = x
		self.y = y
		self.velocity = [0, 0]
		self.speed = 100 #pixels a second

		#Grid placement
		self.currentcell = gameboard.row(self.y), gameboard.column(self.x)
		self.previouscell = self.currentcell
		self.entry = 'center'
		self.exit = previous_entry

	def reset(self):
		"""Reset clears the velocity and sets the center points."""
		self.velocity = [0, 0]
		self.collision = False
		self.x = self.start[0]
		self.y = self.start[1]
		self.rect.centerx = self.x
		self.rect.centery = self.y

	def movement(self, direction):
		"""Calculates the x and y directional velocities."""
		self.velocity[0] = self.speed * direction[0]
		self.velocity[1] = self.speed * direction[1]

	def record_entry(self):
		"""This function keeps track of from which direction the
		player entered the current cell."""
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
		"""This function checks a player's position with the border grid
		and the pipes that have already been laid down."""
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
			gameboard.add_pipe(self.number, self.previouscell[0], self.previouscell[1]) #add entry, exit?
			Pipe(gameboard.pos(self.previouscell[0], self.previouscell[1]),
				 self.style, self.entry + self.exit)

		#Check if row and column are same
		elif self.currentcell != self.previouscell:
			#[0] = row, [1] = column
			self.record_entry()
			#Add pipe in previous cell
			#Pipe(gameboard.pos(self.previouscell), self.style, self.entry + self.exit)
			gameboard.add_pipe(self.number, self.previouscell[0], self.previouscell[1]) #add entry, exit?
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

	def update(self):
		"""Leave update empty so that Pipe can work as a sprite."""
		pass


class Text(pygame.sprite.Sprite):
	def __init__(self, x, y, text):
		pygame.sprite.Sprite.__init__(self, self.containers)
		self.text = text
		self.mode = ''
		self.font = pygame.font.Font(None, 24)
		self.font.set_italic(0)
		self.color = Color('white')
		self.update()
		self.rect = self.image.get_rect().move(x, y)
	
	def update(self):
		if self.mode == 'score':
			msg = "Player %s: %d" % (self.player.number, self.player.score)
		else:
			msg = self.text
		self.image = self.font.render(msg, 0, self.color)


#Make this a class?
def start_screen(screen):
	#Start Screen settings
	screen = screen
	background_img = load_image('startscreen1.png')
	bg_rect = Rect(0, 0, width, height)
	background = pygame.Surface((width, height))
	background.blit(background_img, (0, 0))
	screen.blit(background, (0,0))
	
	def _quit(self):
		sys.exit()
	
	def _newgame(self):
		self.start = True

	def _options(self):
		print "Load options."
		return True

	#Load Buttons
	options = Button(512, 287, 'empty.png', 
                     'options_on.png', 'options_on.png') 
	newgame = Button(512, 0, 'empty.png', 
                     'newgame_on.png', 'newgame_on.png') 
	quit = Button(512, 640, 'empty.png', 
                  'quit_on.png', 'quit_on.png') 
	newgame.clickrect = Rect((0, 208), (287, 304))
	options.clickrect = Rect((287, 256), (352, 256))
	quit.clickrect = Rect((640,225), (384,287))
	newgame.start = False
	newgame.action = _newgame
	options.action = _options
	quit.action = _quit
	buttons = [newgame, options, quit]
	menu_loop = True

	while menu_loop:
		#Mouse Status
		pos = pygame.mouse.get_pos()

		#Screen Events
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				sys.exit()
			if event.type == pygame.KEYDOWN:
				keystate = pygame.key.get_pressed()
				if keystate[K_q]:
					sys.exit()
				if keystate[K_n]:
					return False
				if keystate[K_o]:
					#TODO add options panel
					pass
			if event.type == pygame.MOUSEBUTTONDOWN:
				for button in buttons:
					button.status(screen, pos, True)

		#Load buttons
		for button in buttons:
			button.status(screen, pos, False)
			screen.blit(button.image, button.rect)

		if newgame.start:
			return False

		pygame.display.flip()  
		screen.blit(background, bg_rect)

	return True


#Game Logic Functions
class prep_timer():
	"""Countdown in between levels."""

	def __init__(self, sprites, clock, screen, update, mode=''):
		sprites.empty()

		#Create the background rectangle
		self.prep_img = load_image('prep_timer.png')
		self.prep_rect = self.prep_img.get_rect()
		self.prep_rect.centery = 255
		self.prep_rect.centerx = width/2
		#background.blit(background_img, (0, 0))
		#screen.blit(background, (0,0))

		#Create the lines of text
		self.lines = []
		if mode == 'gameover':
			if p1score > p2score:
				winner = 'Player 1 wins!'
			elif p1score == p2score:
				winner = 'Tie!'
			else:
				winner = 'Player 2 wins!'
			self.line1 = Text(500, 225, 'Game over')
			self.line2 = Text(500, 265, winner)
			self.lines.append(self.line1)
			self.lines.append(self.line2)
		else:
			if level == 1:
				self.line1 = Text(500, 225, 'Game begins:')
			else:
				self.line1 = Text(500, 225, 'Next level:')
			self.line2 = Text(500, 265, '3')
			self.line2.font = pygame.font.Font(None, 48)
			self.lines.append(self.line1)
			self.lines.append(self.line2)
		for line in self.lines:
			line.color = Color('black')
			line.rect.centerx = width/2
		self.update = update
		Text.containers = sprites
		if mode == 'gameover':
			self.gameover(sprites, screen)
		else:
			self.run(sprites, clock, screen)

	def run(self, sprites, clock, screen):
		"""Run the count down timer."""
		time = 0
		pause = 3
		while time < pause:
			milliseconds = clock.tick(FPS)
			countdown = int(1 + pause - time)
			self.line2.text = str(countdown)
			time += milliseconds / 1000.0
            #Update Screen
			self.update(sprites, None, None, self.prep_img, self.prep_rect)
		#End the timer.
		self.cleanup()
	
	def gameover(self, sprites, screen):
		"""Run the gameover screen."""
		loop = True
		while loop:
			self.update(sprites, self.prep_img, self.prep_rect)
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					sys.exit()
				if event.type == pygame.KEYDOWN:
					keystate = pygame.key.get_pressed()
					if keystate[K_RETURN]:
						loop = False
		self.cleanup()

	def cleanup(self):
		"""Kills the rectangle and the text sprites."""
		for line in self.lines:
			line.kill()

def end_match(players):
	for player in players:
		if player.collision == False:
			return False
	return True


def main():
	#Game Initialization
	pygame.init()
	screen = pygame.display.set_mode(size) #,pygame.FULLSCREEN)
	global level
	global p1score
	global p2score

	menu = True

	if level == 0:
		while menu:
			menu = start_screen(screen)
		level += 1

	#Game init
	playtime = 0
	mainloop = True
	board = gameboard(cell_count_x, cell_count_y)
	clock = pygame.time.Clock()

	#Draw the background
	background_img = load_image('background1.png')
	bg_rect = Rect(0, 0, width, height)
	background = pygame.Surface((width, height))
	background.blit(background_img, (0, 0))
	screen.blit(background, (0,0))

	#Establish players and starting positions
	player_image = "player.png"
	startx1 = borderx + (cell_size / 2)
	starty1 = bordery + (cell_size / 2)
	startx2 = width - startx1
	starty2 = height - starty1
	player1 = Player(1, '1', startx1, starty1, p1score, player_image, board, 'left')
	player2 = Player(2, '2', startx2, starty2, p2score, player_image, board, 'right')
	player1.movement([1, 0])
	player2.movement([-1, 0])
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
	text = pygame.sprite.Group()
	all = pygame.sprite.Group()
	Pipe.containers = pipes, all
	Text.containers = text, all

	def screen_update(sprites, background=None, bg_rect=None,
					  foreground=None, fg_rect=None):
		#sprites.update()
		pygame.display.flip()  
		if background:
			screen.blit(background, bg_rect)
		for item in board.active:
			screen.blit(item.image, item.rect)
		sprites.update()
		if foreground:
			screen.blit(foreground, fg_rect)
		dirty = sprites.draw(screen)
		pygame.display.update(dirty)

	#Pause before each level
	pygame.display.update()  
	if level == 1:
		prep_timer(all, clock, screen, screen_update)

	#Set up text
	score1 = Text(30, 25, '')
	score1.mode = 'score'
	score1.player = player1
	score2 = Text(900, 25, '')
	score2.mode = 'score'
	score2.player = player2
	leveltext = Text(500, 20, 'Level ' + str(level))
	leveltext.rect.centerx = width/2
	leveltext.font = pygame.font.Font(None, 36)
	text.add(score1)
	text.add(score2)
	text.add(leveltext)

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
				for player in playerlist:
					#Check previous entrypoint to prevent self crashes.
					if keystate[player.up]:
						if player.entry != 'up':
							player.movement([0, -1])
					elif keystate[player.down]:
						if player.entry != 'down':
							player.movement([0, 1])
					elif keystate[player.right]:
						if player.entry != 'right':
							player.movement([1, 0])
					elif keystate[player.left]:
						if player.entry != 'left':
							player.movement([-1, 0])
				if keystate[K_g]:
					print board.grid
				if keystate[K_q]:
					sys.exit()
				if keystate[K_r]:
					level = 0
					mainloop = False

		#Display FPS
		pygame.display.set_caption("Plumbergone . [FPS]: %.2f"
								   % clock.get_fps())

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
				#Move art to x,y pixels
				player.rect.centerx = player.roundx
				player.rect.centery = player.roundy
				screen.blit(player.image, player.rect)
				#Check for collisions
				player.collision = player.check_collision(player.roundx, player.roundy, board)
				#Check for pipe adds (collision pipe versus normal pipe)
				player.check_pipe(player.roundx, player.roundy, board)

		#Refresh screen and draw all the dirty rects.
		screen_update(all, background, bg_rect)

		#End match, clean up and next level
		if end_match(playerlist):
			p1score = player1.score
			p2score = player2.score
			if level == 10:
				prep_timer(all, clock, screen, screen_update, 'gameover')
				level = 0
				mainloop = False
			else:
				level += 1
				prep_timer(all, clock, screen, screen_update)
				mainloop = False

if __name__ == '__main__':
	while True:
		main()
