#!/usr/bin/env python

"""
PLUMBERGONE
Patrick Morgan
p.w.morgan@gmail.com
April 2011

An arcade game where you lay down pipes across a variety of environments,
competing for the glorious job of professional plumber. Features art by
Royce Mclean and music from [source].  Written in python using the
pygame framework.
"""


#Import Modules
import os
import sys
import pygame
from pygame.locals import *
from copy import deepcopy

#Import game settings       
from image_files import * 

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
borderx = (width % cell_size) / 2 #+ cell_size
bordery = (height % cell_size) / 2 #+ cell_size
cell_count_x = width / cell_size
cell_count_y = height / cell_size


#Image files
def load_image(image, transparency=white):
	"""Load the image and convert it to a surface."""
	image = os.path.join(main_dir, 'media', image)
	surface = pygame.image.load(image)
	surface = surface.convert()
	if transparency:
		surface.set_colorkey(transparency)
	return surface


def load_pipes(style, direction, filetype):
	"""Load all the pipes with the specific styles and orientations."""
	image = "pipes" + "_" + style + "_" + direction + "." + filetype
	return load_image(image)


#Load level files
def load_level(level_file):
	"""Load the level txt file and convert it into layers of assets."""
	full_path = os.path.join(main_dir, 'levels', level_file)
	raw_level = file(full_path, 'r')
	done = False
	#Parse the raw level file
	timer_layer = [] #Gate timer storage
	main_layer = [] #Top art level with collisions
	while not done:	
		line = raw_level.readline()
		if line[:5] == 'LEVEL':
			line = raw_level.readline()
			while line[:3] != 'END':			
				row = line.split(' ')
				main_layer.append(row)
				line = raw_level.readline()
			done = True

	#Scrub the gameboard lists
	for row in range(len(main_layer)):
		for cell in range(len(main_layer[row])):
			contents = main_layer[row][cell]   
			if ',' in contents:
				cell_timer = contents.split(',')
				timer_layer.append([(row, cell), cell_timer[1]])
			main_layer[row][cell] = contents[0]
	raw_level.close()
	return main_layer, timer_layer #, sub_layer


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
	def __init__(self, x, y, up='empty.png', hover='empty.png', down='empty.png'):
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
	def init(self):
		pass
		#Player AI
		#Volume
		#Sound/Music
		#Speed?
		#Game modes?
		#Controls


#Gameplay Classes
class Gameboard():
	"""The gameboard class contains logic for storing the current game state 
	and for detecting collisions. Also contains functions for determining 
	positions of players."""

	def __init__(self, x, y):
		self.x = x #Rows
		self.y = y #Columns
		self.new(x, y)

	def create_level(self, level):
		"""Load the current level as a list of layers."""
		#A list of all the power-up keys on the board.
		self.powerups = ['1', '2', '3', 'C', 'U', 'D', 'L', 'R']
		grid, self.timers = load_level('level%d.txt' % level) 
		#self.grid = deepcopy(grid)
		#Empty lists for the active images on each layer.
		#self.active = []
		#Convert layer from abstract data to the images for loading.
		for row in range(len(grid)):
			for col in range(len(grid[row])):
				if grid[row][col] != '0':
					key = grid[row][col]
					x, y = self.pos(row, col)
					#Add a collision obj on grid.
					self.grid[row][col] = key #This will be useful for AI and collision detection
					grid[row][col] = Doodad(level_key[key], x, y)
					self.active[row][col] = grid[row][col]

	def new(self, x, y):
		"""Create a new gameboard using row and column count."""
		self.grid = []
		self.pipes = []
		self.active = []
		for row in range(y):
			self.grid.append([])
			for column in range(x):
				self.grid[row].append('0')
		#self.pipes = deepcopy(self.grid)
		self.active = deepcopy(self.grid)
		self.create_level(level)
	
	def pos(self, row=0, column=0):
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
	
	"""
	#Unused grid store command.
	def store(self):
		self.lowest = deepcopy(self.previous)
		self.previous = deepcopy(self.grid)
		self.new()
	"""

	def midpoint(self, point, direction):
		if direction == "y":
			y = self.pos(row = point)
			y = y[1] + (cell_size / 2)
			return y
		elif direction == "x":
			x = self.pos(column = point)
			x = x[0] + (cell_size / 2)
			return x
		elif direction == "both":
			x = self.pos(column = point[0])
			x = x[0] + (cell_size / 2)
			y = self.pos(row = point[1])
			y = y[1] + (cell_size / 2)
			return x, y
			

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
				 image, border, gameboard, previous_entry):
		"""When initializing a player class, you need the player number, pipe
		sytle, x and y coordinates, player image, the gameboard, and which
		direction the first player pipe should come from."""

		#Initial player 
		self.number = number
		self.style = style
		self.score = score
		self.collision = False
		self.AI = False
		self.tblock = 0

		#Load images
		self.image = load_image(image)
		self.border = load_image(border)
		self.border_rect = self.border.get_rect()
		#self.image.set_colorkey(white)

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
		elif gameboard.grid[row][column] in gameboard.powerups:
			self.powerup(gameboard, row, column)
			return False
		elif gameboard.grid[row][column] != '0':
			return True
		else:
		   	return False
	
	def powerup(self, gameboard, row, column):
		item = gameboard.grid[row][column]
		#Remove collision object
		gameboard.grid[row][column] = '0'
		if item == "1":
			#Increase player speed by 10%
			self.speed *= 1.4
			self.velocity = [self.velocity[0]*1.4, self.velocity[1]*1.4]
			#print self.speed, self.velocity
		elif item == "2":
			#Give player 3 t-blocks
			#self.tblock += 3
			self.speed *= .6
			self.velocity = [self.velocity[0]*.6, self.velocity[1]*.6]
		elif item == "3":
			#Power up 3: crazy controls?
			self.up, self.down = self.down, self.up 
			self.left, self.right = self.right, self.left
		elif item == "C":
			#Final pipe
			self.score += 100
			self.currentcell = (row, column)
			gameboard.add_pipe(self.number, row, column)
			opposite = {'up':'down', 'down':'up', 'left':'right', 'right':'left'}
			Pipe(gameboard, gameboard.pos(row, column), self.style, "center" + opposite[self.entry], row, column)
			self.collision = True
		elif item in ["R", "U", "D", "L"]:
			#Create an center facing pipe on one side.
			#row = gameboard.row(self.y)
			#column = gameboard.column(self.x)
			self.currentcell = (row, column)
			gameboard.add_pipe(self.number, row, column)
			opposite = {'up':'down', 'down':'up', 'left':'right', 'right':'left'}
			Pipe(gameboard, gameboard.pos(row, column), self.style, "center" + opposite[self.entry], row, column)

			#Send player to opposite side of the screen
			teleport = {"L": ([-1, 0], len(gameboard.grid[0])-1), 
						"R": ([1, 0], 0),
						"U": ([0, -1], len(gameboard.grid)-1),
						"D": ([0, 1], 1)}
			if item == "L" or item == "R":
				self.y = gameboard.midpoint(row, "y")
				self.x = gameboard.midpoint(teleport[item][1], "x")
			else:	
				self.y = gameboard.midpoint(teleport[item][1], "y")
				self.x = gameboard.midpoint(column, "x")

			self.entry = "center"
			self.exit = "center"
			row = gameboard.row(self.y)
			column = gameboard.column(self.x)
			self.currentcell = (row, column)
			self.previouscell = self.currentcell
			gameboard.grid[row][column] = '0'

			#Change the player direction.
			self.movement(teleport[item][0])

			#Find a way to remove powerup from the graphics layer

	def check_pipe(self, x, y, gameboard):
		"""Checks the players current position and then creates a pipe as the player exits a cell."""
		#Set the current row and column
		row = gameboard.row(y)
		column = gameboard.column(x)
		self.currentcell = (row, column)
		opposite = {'up':'down', 'down':'up', 'left':'right', 'right':'left'}
	
		#Check for collision
		if self.collision:
			#self.record_entry()
			self.exit = 'center'
			#Add end pipe
			gameboard.add_pipe(self.number, self.previouscell[0], self.previouscell[1]) #add entry, exit?
			Pipe(gameboard, gameboard.pos(self.previouscell[0], self.previouscell[1]),
				 self.style, self.entry + self.exit, row, column)

		#Check if row and column are same
		elif self.currentcell != self.previouscell:
			#[0] = row, [1] = column
			self.record_entry()
			#Add pipe in previous cell
			#Pipe(gameboard.pos(self.previouscell), self.style, self.entry + self.exit)
			gameboard.add_pipe(self.number, self.previouscell[0], self.previouscell[1]) #add entry, exit?
			Pipe(gameboard, gameboard.pos(self.previouscell[0], self.previouscell[1]),
				 self.style, self.exit + self.entry, row, column)
			self.score += 1
			self.previouscell = (row, column)
		

class Pipe():
	"""The Pipe class contains a list of all pipe orientations and creates an appropriate image when called."""
	images = {}
	#The following takes data from an file that contains pipe orientations.
	for pipe in pipe_list:
		images[pipe] = pipe
	secondary = other_pipes.keys()
	for pipe in secondary:
		images[pipe] = other_pipes[pipe]

	def __init__(self, board, pos, style, direction, row=0, column=0):
		direction = self.images[direction]
		self.image = load_pipes(style, direction, 'png')
		self.rect = self.image.get_rect(topleft=pos)
		board.pipes.append(self)
		"""
		try:
			board.pipes[row][column] = self
		except IndexError:
			pass
		"""


class Text(pygame.sprite.Sprite):
	"""The Text class is a Sprite class that displays words on the screen when updated."""
	def __init__(self, x, y, text):
		pygame.sprite.Sprite.__init__(self, self.containers)
		self.text = text
		self.mode = ''
		self.font = pygame.font.Font(None, 24)
		self.font.set_italic(0)
		self.color = Color('white')
		self.time = 0 #Used by timers
		self.update()
		self.rect = self.image.get_rect().move(x, y)
	
	def update(self):
		if self.mode == 'score':
			msg = "Player %s: %d" % (self.player.number, self.player.score)
		elif self.mode == 'timer':
			msg = str(int(self.text) - self.time) 
		else:
			msg = self.text
		self.image = self.font.render(msg, 0, self.color)


#Make this a class?
def start_screen(screen):
	#Start Screen settings
	screen = screen
	background_img = load_image('startscreen1.png', None)
	bg_rect = Rect(0, 0, width, height)
	background = pygame.Surface((width, height))
	background.blit(background_img, (0, 0))
	screen.blit(background, (0,0))

	#Reset the scores at the beginning of each game.
	global p1score
	global p2score
	p1score = 0
	p2score = 0
	
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
			self.update(sprites, None, None, self.prep_img, self.prep_rect)
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
	board = Gameboard(cell_count_x, cell_count_y)
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
	starty1 = bordery + (cell_size / 2) + cell_size #Starts 2 cells down
	startx2 = width - startx1
	starty2 = height - starty1 + cell_size
	player1 = Player(1, '1', startx1, starty1, p1score, player_image, 'border1.png', board, 'left')
	player2 = Player(2, '2', startx2, starty2, p2score, player_image, 'border2.png', board, 'right')
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

	text = pygame.sprite.Group()
	all = pygame.sprite.Group()
	Text.containers = text, all

	def screen_update(sprites, background=None, bg_rect=None,
					  foreground=None, fg_rect=None):
		#sprites.update()
		pygame.display.flip()  
		if background:
			screen.blit(background, bg_rect)
		for row in board.active:
			for item in row:
				if item != "0":
					screen.blit(item.image, item.rect)
		sprites.update()
		for pipe in board.pipes:
			screen.blit(pipe.image, pipe.rect)
		"""
		for row in board.pipes:
			for pipe in row:
				if pipe != "0":
					screen.blit(pipe.image, pipe.rect)
		"""
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
	for time in board.timers:
		location = board.midpoint((time[0][1], time[0][0]), "both")
		time.append(Text(0, 0, str(time[1])))
		time[-1].mode = "timer"
		time[-1].rect.center = location
		text.add(time[-1])
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
					if not player.AI:
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
				row = board.row(player.roundy)
				column = board.column(player.roundx)
				player.border_rect.topleft = board.pos(row, column)
				#plaryer.board.rect.top = board.
				screen.blit(player.border, player.border_rect)
				screen.blit(player.image, player.rect)
				#Check for pipe adds (collision pipe versus normal pipe)
				player.check_pipe(player.roundx, player.roundy, board)
				#Check for collisions
				player.collision = player.check_collision(player.roundx, player.roundy, board)

		for timer in range(len(board.timers)):
			#calculate remaining time
			board.timers[timer][-1].time = int(playtime)
			#if remaining time is 0 or less, kill sprite
			if int(playtime) >= int(board.timers[timer][-1].text):
				board.timers[timer][-1].kill() #kill sprite 
				row = board.timers[timer][0][0]
				column =  board.timers[timer][0][1]
				board.grid[row][column] = "0" #kill collision object
				board.active[row][column] = "0" #kill art
				#remove timer from board.timers

		#Refresh screen and draw all the dirty rects.
		screen_update(all, background, bg_rect)

		#End match, clean up, and next level
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
