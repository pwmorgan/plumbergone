#!/usr/bin/env python

#A list of all the pipe orientation types
pipe_list = ['centerdown',
			 'centerleft',
			 'centerright',
	 		 'centerup',
	 		 'centercenter',
			 'downcenter',
			 'downleft',
			 'leftcenter',
			 'leftdown',
			 'leftleft',
			 'leftup',
			 'rightcenter',
			 'upcenter',
			 'upleft',
			 'upup']

#A list of pipes that are represented by other files.
other_pipes = {'downdown':'upup',
				'rightup':'downleft',
				'rightdown':'upleft',
				'downright':'leftup',
				'rightright':'leftleft',
				'upright':'leftdown',
				'leftright':'leftcenter',
				'rightleft':'rightcenter',
                'updown':'upcenter',
				'downup':'downcenter',
				}

#This dictionary converts the level text into images.
level_key = {'V':'pipes_3_upup.png',  #vertical upup pipe
			 'H':'pipes_3_leftleft.png',  #horizontal leftleft pipe
			 'U':'pipes_3_upcenter.png',  #upcenter pipe
			 'D':'pipes_3_downcenter.png',  #downcenter pipe
			 'L':'pipes_3_leftcenter.png',  #leftcenter pipe
			 'R':'pipes_3_rightcenter.png',  #rightcenter pipe
			 'C':'pipes_3_centercenter.png',  #centercenter pipe
			 'B':'black.png',  #horizontal leftleft pipe			 
			 'v':'gates_upup.png',  #vertical gate
			 'h':'gates_leftleft.png',  #horizontal gate
			 'X':'blocks_03.png',  #random collision block
			 '1':'powerups_01.png',  #powerup 1
			 '2':'powerups_02.png',  #powerup 2
			 '3':'powerups_03.png',  #powerup 3
			 'a':'doodads_01.png',  #doodad 1
			 #'b':'doodads_02.png',  #doodad 2
			 #'c':'doodads_03.png',  #doodad 3
			 }
