import pygame
import logging
from cortex.client import CortexClient

class Game:
	cortex_connection = None
	queued_inputs = []
	cortex_connection = None
	cortex_command_min_weight = 0.1
	cortex_compute_interval = 300
	cortex_time_last_compute = 0
	def __init__(self):
		pygame.init()
		self.cortex_connection = CortexClient(self)

	def on_receive_cortex_data(self, data):
		logging.debug("received cortex data: " + str(data))
		self.queued_inputs.append(data["com"])

	def compute_cortex_event(self):
		time_passed = pygame.time.get_ticks() - self.cortex_time_last_compute
		if time_passed < self.cortex_compute_interval:
		    return None
		self.cortex_time_last_compute = pygame.time.get_ticks()
		logging.debug("computing cortex event")
		if len(self.queued_inputs) > 0:
		    while len(self.queued_inputs) > 0:
		        data = self.queued_inputs.pop()
		        # log data
		        logging.debug(data)
		return None

def main():
	logging.basicConfig(level=logging.DEBUG)
	game = Game()
	while(1):
		game.compute_cortex_event()

if __name__ == "__main__":
    main()