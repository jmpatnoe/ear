#!/usr/bin/env python3

import pyfmodex as fmod

import os
import sys
import time

def main(argv):
	system = fmod.System()
	num_drivers = system.num_drivers
	for i in range(num_drivers):
		d = system.get_driver_info(i)
		vals = {}
		for key in d.keys():
			vals[key] = d[key]
		print("driver", vals)

	system.init()

	sounds = []
	for root, dirs, files in os.walk('./media'):
		for f in files:
			file = os.path.join(root, f)

			sound = system.create_sound(file, fmod.flags.MODE.ACCURATETIME)
			format = sound.format
			attrs = {
				'type': format.type,
				'channels': format.channels,
				'format': format.format,
				'length': sound.get_length(fmod.flags.TIMEUNIT.MS)
			}

			print(len(sounds), ':', file, attrs)

			sounds.append({
				'sound': sound,
				'attrs': attrs
			})

	master_group = system.master_channel_group

	sound_group = system.create_channel_group('sound')
	left_group = system.create_channel_group('left')
	right_group = system.create_channel_group('right')

	left_group.add_group(sound_group, True)
	left_group.set_mix_matrix([0, 1, 0, 0], 2, 2)
	#right_group.add_group(sound_group, True)
	#right_group.set_mix_matrix([0, 0, 1, 0], 2, 2)

	#left_group.volume = .3
	#right_group.volume = .3

	parent = sound_group.parent_group
	print('parent name', parent.name)
	print('parent is master', parent is master_group)

	s = sounds[1]['sound']
	channel = s.play(sound_group)

	while channel.is_playing:
		time.sleep(0)

	return 0

if __name__ == "__main__":
	sys.exit(main(sys.argv))
