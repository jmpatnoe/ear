#!/usr/bin/env python3

import argparse
import json
import logging
import pyfmodex as fmod
import sys
import time
import uuid

default_logger = logging.getLogger('ear')

class Matrix(object):
	def __init__(self, inputs, outputs, assign=0):
		self.inputs = inputs
		self.outputs = outputs
		self.matrix = [[assign for x in range(inputs)] for y in range(outputs)]

	def fill(self, matrix):
		if len(matrix) != self.inputs:
			raise Exception("Inputs length does not match matrix")

		for input in range(self.inputs):
			if len(matrix[input]) != self.outputs:
				raise Exception("Outputs length does not match matrix")

		self.matrix = matrix

	def flatten(self):
		return [y for x in self.matrix for y in x]

	def set_input_vector(self, input, outputs):
		if len(outputs) != self.outputs:
			raise Exception("Outputs length does not match expected")

		self.matrix[input] = outputs

	def set_input(self, input, output, value):
		self.matrix[input][output] = value

	def get_input_vector(self, input):
		return self.matrix[input]

	def set_output_vector(self, output, inputs):
		if len(inputs) != self.inputs:
			raise Exception("Inputs length does not match expected")

		for i in range(self.inputs):
			self.matrix[i][output] = inputs[i]

	def set_output(self, output, input, value):
		self.matrix[input][output] = value

	def get_output_vector(self, output):
		inputs = []

		for i in range(self.inputs):
			inputs.append(self.matrix[i][output])

		return inputs

class Driver(object):
	def __init__(self, index, fmod_driver):
		self.index = index
		self.fmod_driver = fmod_driver
		self.id = uuid.uuid5(uuid.NAMESPACE_DNS, 'ear.drivers.' + str(self.fmod_driver.guid.data1))

	def __eq__(self, rhs):
		return self.id == rhs.id

	def __str__(self):
		return json.dumps(self.obj())

	def __repr__(self):
		return self.__str__()

	def obj(self):
		return {
			'id': str(self.id),
			'name': self.fmod_driver.name.decode("utf-8") ,
			'rate': self.fmod_driver.system_rate,
			'mode': self.fmod_driver.speaker_mode,
			'channels': self.fmod_driver.speaker_mode_channels
		}

class Speaker(object):
	def __init__(self, index):
		self.index = index

		self.name = None
		self.volume = 0

class SpeakerGroup(object):
	def __init__(self, router, speakers):
		self.router = router
		self.speakers = speakers
		self.mix_recipes = {}

	def play(file):
		sound = self.router.fmod_system.create_sound(file)
		format = sound.format
		channels = format.channels

		channel_group = self.router.fmod_system.create_channel_group("test")
		sound.add_group(channel_group)
		self.router.output.add_group(channel_group)

		matrix = Matrix(channels, router.num_speakers, 1)
		channel_group.set_mix_matrix(matrix.flatten())

		sound.play()

class Zone(object):
	def __init__(self, group, name):
		self.group = group
		self.name = name
		self.children = []

	def add_zone(self, zone):
		if zone in self.children:
			raise Exception("Zone already has child " + zone)

		self.children.append(zone)

	def remove_zone(self, zone):
		if zone not in self.children:
			raise Exception("Zone does not have child " + zone)

		self.children.remove(zone)

class ChannelZone(object):
	def __init__(self, channel, zone):
		self.channel = channel
		self.zone = zone
		self.volume = 1

class Channel(object):
	def __init__(self, router):
		self.id = uuid.uuidv4()
		self.router = router
		self.output = self.router.fmod_system.create_channel_group()
		self.zones = []

	def _update_mix(self):
		"""Recompute output mix matrix based on currently attached zones"""

		mix = [0 for i in range(self.router.num_speakers * self.router.num_speakers)]



		self.output.set_mix_matrix(mix, self.router.num_speakers, self.router.num_speakers)

	def attach_zone(self, zone):
		for cz in self.zones:
			if cz.zone is zone:
				return cz

		cz = ChannelZone(self, zone)
		self.zones.append(cz)

		return cz

	def detach_zone(self, cz):
		self.zones.remove(cz)

	def play(file):
		sound = self.system.create_sound(file)
		sound.channel_group = self.output

		#speakers = group.get_speakers()

class Router(object):
	def __init__(self, num_speakers, logger=default_logger):
		self.num_speakers = num_speakers
		self.speakers = SpeakerGroup([Speaker(i) for i in range(num_speakers)])
		self.logger = logger

		self.running = False

		self.fmod_system = fmod.System()
		self.output = None

		format = self.fmod_system.software_format
		format.raw_speakers = num_speakers
		format.speaker_mode = fmod.enums.SPEAKERMODE.RAW.value
		self.fmod_system.software_format = format

		#self.update_driver_cache()

	def _update_volume(self):
		mix_matrix = [0 for i in range(self.num_speakers * self.num_speakers)]

		for index, speaker in enumerate(self.speakers.speakers):
			mix_matrix[index][index] = speaker.volume

		self.output.set_mix_matrix(mix_matrix, self.num_speakers, self.num_speakers)

	def play(self, file, group):
		sound = self.fmod_system.create_sound(file)
		sound.channel_group = self.output

		speakers = group.get_speakers()

		mix = [0 for i in range(self.num_speakers * self.num_speakers)]


	def get_all_drivers(self):
		drivers = []

		num_drivers = self.fmod_system.num_drivers
		for i in range(num_drivers):
			d = self.fmod_system.get_driver_info(i)

			drivers.append(Driver(i, d))

		return drivers

	def get_driver_from_index(self, index):
		return Driver(index, self.fmod_system.get_driver_info(index))

	def get_index_from_driver(self, driver):
		num_drivers = self.fmod_system.num_drivers
		for i in range(num_drivers):
			d = Driver(i, self.fmod_system.get_driver_info(i))
			if d == driver:
				return i

		return None

	def get_driver(self):
		"""
		Return current driver object configured in Mixer
		"""
		print("driver_index", self.fmod_system.driver)
		return self.get_driver_from_index(self.fmod_system.driver)

	def set_driver(self, driver):
		self.fmod_system.driver = driver.get_index()

	def get_speaker(index):
		return self.speakers.get_speaker(index)

	def start(self):
		if self.running:
			raise Exception("Mixer already running")

		self.fmod_system.init()

		if self.output is None:
			self.output = self.fmod_system.create_channel_group("main_mix")
			self._update_volume()

		self.running = True

	def stop(self):
		if not self.running:
			raise Exception("Mixer is not running")

		self.fmod_system.close()

		self.running = False

	def usage(self):
		cpu_usage = self.fmod_system.cpu_usage
		return {
			'dsp': usage.dsp,
			'stream': usage.stream,
			'geometry': usage.geometry,
			'update': usage.update,
			'total': usage.total
		}

def main(argv):
	parser = argparse.ArgumentParser(description='Process some integers.')
	parser.add_argument('--sum', dest='accumulate', action='store_const',
		const=sum, default=max,
		help='sum the integers (default: find the max)')

	args = parser.parse_args()
	#print(args)

	logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)
	logger = default_logger

if __name__ == "__main__":
	sys.exit(main(sys.argv))
