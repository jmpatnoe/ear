#!/usr/bin/env python3

import logging
import uuid

default_logger = logging.getLogger('ear.mixer')

class Bus(object):
	pass

class InputBus(object):
	pass

class OutputBus(object):
	def __init__(self, logger=default_logger):
		self.logger = logger

		self.logger.info('OutputBus created')

class SpeakerBus(OutputBus):
	def __init__(self, index, attrs, logger=default_logger):
		super(OutputBus).__init__()

		self.index = index
		self.attrs = attrs
		self.id = uuid.uuid5(uuid.NAMESPACE_DNS, 'ear.drivers.' + str(self.attrs.guid.data1))
		self.logger = logger

		self.logger.info('SpeakerBus created', self)

	def __eq__(self, rhs):
		return self.id == rhs.id

	def __str__(self):
		return json.dumps(self.obj())

	def __repr__(self):
		return self.__str__()

	def obj(self):
		return {
			'id': str(self.id),
			'name': self.attrs.name.decode("utf-8") ,
			'rate': self.attrs.system_rate,
			'mode': self.attrs.speaker_mode,
			'channels': self.attrs.speaker_mode_channels
		}

class System(object):
	def __init__(self, num_speakers, logger=default_logger):
		self.num_speakers = num_speakers
		self.logger = logger

		self.logger('Creating system with {} channels'.format(num_speakers))

		self.fmod = fmod.System()
		self.output = None

		format = self.fmod.software_format
		format.raw_speakers = num_speakers
		format.speaker_mode = fmod.enums.SPEAKERMODE.RAW.value
		self.fmod.software_format = format

		self.speaker_busses = []
		num_drivers = self.fmod.num_drivers
		for i in range(num_drivers):
			d = self.fmod.get_driver_info(i)

			self.speaker_busses.append(SpeakerBus(i, d))

		self.logger('System created')

	def release(self):
		self.logger('Releasing system')
		self.fmod.release()

	def set_output(self, speaker_bus):
		if not isinstance(speaker_bus, SpeakerBus):
			raise ValueError("SpeakerBus not provided")

		self.logger.info('Setting output bus to {}'.format(speaker_bus))

		self.output = speaker_bus

		self.fmod.driver = speaker_bus.index

	def init(self):
		self.fmod.init()

if __name__ == "__main__":
	import sys
	sys.exit(main(sys.argv))
