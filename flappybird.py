#! /usr/bin/env python3

import math
import os
import sys
from random import randint
import pygame
from pygame.locals import *


FPS = 100
ANIMATION_SPEED = 0.18
WIN_WIDTH = 284 * 2
WIN_HEIGHT = 512


class Bird():

	WIDTH = HEIGHT = 32
	def __init__(self, x, y, flying_time_left, images):	
		self.down_speed = 0.18
		self.fly_speed = 0.30
		self.fly_time = 333.3
		self.x, self.y = x, y
		self.dead = False
		self.flying_time_left = flying_time_left
		self.img_wingup, self.img_wingmid, self.img_wingdown, self.img_dead = images
		self.mask_wingup = pygame.mask.from_surface(self.img_wingup)
		self.mask_wingmid = pygame.mask.from_surface(self.img_wingmid)
		self.mask_wingdown = pygame.mask.from_surface(self.img_wingdown)
		self.mask_dead = pygame.mask.from_surface(self.img_dead)

	def update(self):
		if self.flying_time_left > 0:
			climb_done = 1 - self.flying_time_left/self.fly_time
			self.y -= (self.fly_speed * 1000 / FPS *
					   (1 - math.cos(climb_done * math.pi)))
			self.flying_time_left -= 1000 / FPS
		else:
			self.y += self.down_speed * 1000 / FPS

	@property
	def image(self):
		if self.dead:
			return self.img_dead
		if pygame.time.get_ticks() % 510 <= 170:
			return self.img_wingup
		elif pygame.time.get_ticks() % 510 >= 340:
			return self.img_wingdown
		else:
			return self.img_wingmid

	@property
	def mask(self):
		if pygame.time.get_ticks() % 510 <= 170:
			return self.mask_wingup
		elif pygame.time.get_ticks() % 510 >= 340:
			return self.mask_wingdown
		else:
			return self.mask_wingmid

	@property
	def rect(self):
		return Rect(self.x, self.y, Bird.WIDTH, Bird.HEIGHT)


class Pipes():

	WIDTH = 80
	PIECE_HEIGHT = 32
	ADD_INTERVAL = 3000

	def __init__(self, pipe_endimg, pipe_bodyimg):
		self.x = float(WIN_WIDTH - 1)
		self.score_counted = False
		self.image = pygame.Surface((Pipes.WIDTH, WIN_HEIGHT), SRCALPHA)
		total_pipe_body_pieces = int((WIN_HEIGHT - 3 * Bird.HEIGHT - 3 * Pipes.PIECE_HEIGHT) / Pipes.PIECE_HEIGHT)
		self.bottom_pieces = randint(1, total_pipe_body_pieces)
		self.top_pieces = total_pipe_body_pieces - self.bottom_pieces

		# bottom pipe
		for i in range(1, self.bottom_pieces + 1):
			piece_pos = (0, WIN_HEIGHT - i * Pipes.PIECE_HEIGHT)
			self.image.blit(pipe_bodyimg, piece_pos)
		bottom_pipe_end_y = WIN_HEIGHT - self.bottom_pieces * Pipes.PIECE_HEIGHT
		bottom_end_piece_pos = (0, bottom_pipe_end_y - Pipes.PIECE_HEIGHT)
		self.image.blit(pipe_endimg, bottom_end_piece_pos)

		# top pipe
		for i in range(self.top_pieces):
			piece_pos = (0, i * Pipes.PIECE_HEIGHT)
			self.image.blit(pipe_bodyimg, piece_pos)
		top_pipe_end_y = self.top_pieces * Pipes.PIECE_HEIGHT
		self.image.blit(pipe_endimg, (0, top_pipe_end_y))

		# compensate for added end pieces
		self.top_pieces += 1
		self.bottom_pieces += 1

		# for collision detection
		self.mask = pygame.mask.from_surface(self.image)

	@property
	def visible(self):
		return -Pipes.WIDTH < self.x < WIN_WIDTH

	@property
	def rect(self):
		return Rect(self.x, 0, Pipes.WIDTH, Pipes.PIECE_HEIGHT)

	def update(self):
		self.x -= ANIMATION_SPEED * 1000 / FPS

	def collides_with(self, bird):
		return pygame.sprite.collide_mask(self, bird)


def load_images():
	

	def load_image(img_file_name):
		file_name = os.path.join('.', 'images', img_file_name)
		img = pygame.image.load(file_name)
		img.convert()
		return img

	return {'background': load_image('background.png'),
		'pipe-end': load_image('pipe_end.png'),
		'pipe-body': load_image('pipe_body.png'),
		'bird-wingup': load_image('bird_wing_up.png'),
		'bird-wingmid': load_image('bird_wing_mid.png'),
		'bird-dead': load_image('bird_dead.png'),
		'bird-wingdown': load_image('bird_wing_down.png')}




def main():
	again = True
	#collisions won't be detected if testing = 1
	testing = 0
	if len(sys.argv) > 1 and int(sys.argv[1]) == 1:
		testing = 1
	pygame.init()
	display_surface = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
	pygame.display.set_caption('Flappy Bird')
	clock = pygame.time.Clock()
	#set font style, size, boldness 
	start_font = pygame.font.SysFont(None, 50, bold=True)
	score_font = pygame.font.SysFont(None, 32, bold=True)
	over_font = pygame.font.SysFont(None, 50, bold=True)
	exit_font = pygame.font.SysFont(None, 40, bold=True)
	images = load_images()
	while again:
		bird = Bird(50, int((WIN_HEIGHT - Bird.HEIGHT) / 2), 2,
				(images['bird-wingup'], images['bird-wingmid'], images['bird-wingdown'], images['bird-dead']))
		pp1 = Pipes(images['pipe-end'], images['pipe-body'])
		pp2 = Pipes(images['pipe-end'], images['pipe-body'])
		frame_clock = 0
		score = 0
		point_sound_time = 0
		done = paused = False
		pipe_add_time = 300
		#text, anti-aliasing and colour of messege
		start_surface = start_font.render("PRESS ANY KEY TO START", True, (255, 255, 255))
		score_surface = score_font.render(str(score), True, (255, 255, 255))
		over_surface = over_font.render("GAME OVER", True, (0, 0, 0))
		exit_surface = exit_font.render("TO EXIT PRESS ESC", True, (255, 255, 255))
		score_x = (WIN_WIDTH - score_surface.get_width()) / 2
		while not done:
			clock.tick(FPS)
			#update score board
			score_surface = score_font.render(str(score), True, (255, 255, 255))
			#add new pipe
			if not (paused or frame_clock % pipe_add_time):
				pipe_add_time = randint(-50, 50) + FPS * Pipes.ADD_INTERVAL / 1000
				if frame_clock:
					frame_clock = pipe_add_time
				pp2 = pp1
				if not frame_clock:
					pp2.x = - Pipes.WIDTH - 2
				pp1 = Pipes(images['pipe-end'], images['pipe-body'])
			#accept input
			for e in pygame.event.get():
				if not bird.dead:
					if e.type == QUIT or (e.type == KEYUP and e.key == K_ESCAPE):
						done = True
						again = False
						break
					elif e.type == KEYUP and e.key in (K_PAUSE, K_p):
						paused = not paused
					elif e.type == MOUSEBUTTONUP or (e.type == KEYUP and 
						e.key in (K_UP, K_RETURN, K_SPACE)) and not paused:
						bird.flying_time_left += bird.fly_time
						if pygame.time.get_ticks() - point_sound_time > 350:
							pygame.mixer.music.load('fly.mp3')
							pygame.mixer.music.play(1, 0.15)
				else:
					if e.type == QUIT or (e.type == KEYUP and e.key == K_ESCAPE):
						done = True
						again = False
						break

			if paused:
				continue
	
			# collision detection
			if not testing or not frame_clock:
				pipe_collision1 = pp1.collides_with(bird)
				pipe_collision2 = pp2.collides_with(bird)
			if (pipe_collision1 or pipe_collision2 or 0 >= bird.y) and not bird.dead: 
				bird.dead = True
				pygame.mixer.music.load('dead.mp3')
				pygame.mixer.music.play(1, 0.15)
				bird.flying_time_left = 0
				pygame.time.wait(500)
			#game over when bird hits ground
			if bird.y >= WIN_HEIGHT - Bird.HEIGHT:
				done = True
 
			for x in (0, WIN_WIDTH / 2):
				display_surface.blit(images['background'], (x, 0))

			if not bird.dead:
				pp1.update()
				if pp2.visible:
					pp2.update()
			display_surface.blit(pp1.image, pp1.rect)
			if pp2.visible:
				display_surface.blit(pp2.image, pp2.rect)

			bird.update()
			display_surface.blit(bird.image, bird.rect)

			# update score
			if pp2 and pp2.x + Pipes.WIDTH < bird.x and not pp2.score_counted and not bird.dead:
				score += 1
				if not frame_clock:
					score = 0
				else:
					pygame.mixer.music.load('point.mp3')
					pygame.mixer.music.play(1, 0.15)
					point_sound_time = pygame.time.get_ticks()
				pp2.score_counted = True

			if pp1.x + Pipes.WIDTH < bird.x and not pp1.score_counted and not bird.dead:
				score += 1
				if not frame_clock:
					score = 0
				else:
					pygame.mixer.music.load('point.mp3')
					pygame.mixer.music.play(1, 0.15)
					wt = pygame.time.get_ticks()
				pp1.score_counted = True

			display_surface.blit(score_surface, (score_x, Pipes.PIECE_HEIGHT))
			#Text displayed on screen
			if bird.dead:
	  			display_surface.blit(over_surface, (score_x - 100, 4 * Pipes.PIECE_HEIGHT))
			if not frame_clock:
				display_surface.blit(start_surface, (score_x - 210, 4 * Pipes.PIECE_HEIGHT))
				display_surface.blit(exit_surface, (score_x - 130, 6 * Pipes.PIECE_HEIGHT))
			pygame.display.flip()

			if not frame_clock:
				while not pygame.event.wait():
					continue
				bird.flying_time_left = 0
			frame_clock += 1
		done = True
		bird.dead = False
	pygame.quit()


if __name__ == '__main__':
	main()
