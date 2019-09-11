#!/usr/bin/env python3

import asyncio
import websockets

server = None
GLOBAL_DISPATCHER = {}
SYSTEM_DISPATCHER = {}

def global_method(fn):
	GLOBAL_DISPATCHER[fn.__name__] = fn
	return fn

def system_method(fn):
	SYSTEM_DISPATCHER[fn.__name__] = fn
	return fn

def error(message, data=None):
	e = {"error": message}
	if data is not None:
		e['data'] = data
	return json.dumps(e)


class Server(object):
	def __init__(self, logger):
		self.logger = logger
		self.systems = {}

		self.logger.info('Server created')

	def create(self, driver):
		system = System(driver, self.logger)
		system.driver = driver.index
		system.init()
		self.systems[system.id] = system
		return system

	def destroy(self, system):
		if system.id in self.systems:
			del system

@global_method
async def create_system(req, socket):
	driver_id = req.get("driver", None)
	driver = get_driver(driver_id)
	if not driver:
		await socket.send(error("Unknown driver", driver_id))
	else:
		system = server.create(driver)
		await socket.send(json.dumps({
			"system": system.id
		}))

@global_method
async def list_drivers(req, socket):
	s = fmod.System()

	drivers = []

	num_drivers = s.num_drivers
	for i in range(num_drivers):
		d = s.get_driver_info(i)
		driver = Driver(i, d)

		drivers.append(driver.json_obj())

	await socket.send(json.dumps(drivers))

@system_method
async def get_usage(system, req, socket):
	await socket.send(json.dumps(system.usage()))

def main(argv):
	parser = argparse.ArgumentParser(description='Process some integers.')
	parser.add_argument('--sum', dest='accumulate', action='store_const',
		const=sum, default=max,
		help='sum the integers (default: find the max)')

	args = parser.parse_args()
	#print(args)

	logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)
	logger = logging.getLogger('ear')

	server = Server(logger)

	logging.getLogger('websockets.server').setLevel(logging.ERROR)
	async def server_socket(socket, path):
		async for message in socket:
			message = message.strip()

			try:
				req = json.loads(message)
				method = req.get('method', None)

				if method in GLOBAL_DISPATCHER:
					await GLOBAL_DISPATCHER[method](req, socket)
				elif method in SYSTEM_DISPATCHER:
					if 'system' not in req:
						await socket.send(error("Missing system id"))
					else:
						system = server.systems.get(req['system'], None)
						if not system:
							await socket.send(error("Unknown system", req['system']))
						else:
							await SYSTEM_DISPATCHER[method](system, req, socket)
				else:
					await socket.send(error("Unknown method", method))
			except json.decoder.JSONDecodeError:
				await socket.send(error("JSON payload required"))

	websocket_server = websockets.serve(server_socket, "localhost", 8765)

	try:
		asyncio.get_event_loop().run_until_complete(websocket_server)
		asyncio.get_event_loop().run_forever()
	except KeyboardInterrupt as e:
		pass

	return 0

if __name__ == "__main__":
	sys.exit(main(sys.argv))
