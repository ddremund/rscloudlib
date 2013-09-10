#!/usr/bin/python -tt

# Copyright 2013 Derek Remund (derek.remund@rackspace.com)

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import pyrax
import os
import sys
import argparse
import time
import rscloudlib
from pyrax.utils import wait_until


def main():

	default_creds_file = os.path.join(os.path.expanduser('~'), 
		'.rackspace_cloud_credentials')

	parser = argparse.ArgumentParser(
		description = 'Builds multiple cloud servers given a flavor, image, '
		'and base name.',
		epilog = 'Ex: {} -r DFW -b web -n 3 -i 'Ubuntu 11.10' -f 512 - builds '
		'web1, web2, and web3 in DFW'.format(__file__))

	parser.add_argument('-r', '--region', help = 'Cloud Servers region to ' 
		'connect to.  Menu provided if absent.')
	parser.add_argument('-b', '--base', required = True, 
		help = "Base name for servers.")
	parser.add_argument('-n', '--number', type = int, default = 1, 
		help = "Number of servers to build; defaults to 1.")
	parser.add_argument('-s', '--start', type = int, default = 1, 
		help = 'Server index to start with; defaults to 1.')
	parser.add_argument('-i', '--image_name', 
		help = "Image name to use to build server.  Menu provided if absent.")
	parser.add_argument('-f', '--flavor_ram', type = int, 
		help = "RAM of flavor to use in MB.  Menu provided if absent.")
	parser.add_argument('-m', '--networks', default = None,  
		help = 'Additional Cloud Networks to attach to the server.  Supply '
		' as a comma-separated list, e.g. network1,network2,network3')
	parser.add_argument('-d', '--block_storage', type = int, default = None, 
		help = 'Amount of block storage to auto-attach; defaults to none.')
	parser.add_argument('-v', '--volume_base', default = 'Volume-',
		help = 'Base name for CBS volumes; defaults to "Volume-"')
	parser.add_argument('-y', '--volume_type', default = 'SATA', 
		choices = ['SATA', 'SSD'], help = 'Volume type for CBS; '
		'defaults to SATA.')
	parser.add_argument('-p', '--mount_point', default = '/dev/xvdb', 
		help = 'Mount point for CBS volumes; defaults to /dev/xvdb.')
	parser.add_argument('-c', '--creds_file', default = default_creds_file, 
		help = 'Location of credentials file; '
		'defaults to {}'.format(default_creds_file))

	args = parser.parse_args()

	rscloudlib.set_creds(args.creds_file)
	region = rscloudlib.choose_region(args.region)

	cs = pyrax.connect_to_cloudservers(region = region)	

	flavor = rscloudlib.fuzzy_choose_flavor(cs, prompt, args.flavor_ram)
	image = rscloudlib.fuzzy_choose_image(cs, prompt, args.image_name)

	nics = {'net-id': pyrax.cloudnetworks.PUBLIC_NET_ID,
			'net-id': pyrax.cloudnetworks.SERVICE_NET_ID}

	if args.networks is not None:
		cnw = pyrax.connect_to_cloud_networks(region = region)
		network_names = args.networks.split(',')
		for network_name in network_names:
			network = cnw.find_network_by_name(network_name)
			if network is None:
				choice = raw_input('Network "{}" not found.  Create it? [y/N]')
				if choice.capitalize != 'Y':
					continue
				cidr = raw_input('CIDR block to use: ')
				try:
					network = cnw.create(network_name, cidr = cidr)
				except Exception, e:
					print 'Error creating network:', e
					continue
			nics.append({'net-id': network.id})

	servers = []
	for i in range(args.start, args.start + args.number)
		servers.append({'name': '{}{}'.format(args.base, i),
						'image': image,
						'flavor': flavor,
						'nics': nics})

	print 'Building {} servers with base name "{}", flavor "{}", and image "{}".'.format(len(servers), 
										args.base, flavor.name, image.name)
	choice = raw_input('Proceed? [y/N]: ')
	if choice.capitalize() != 'Y':
		print "Exiting..."
		sys.exit(0)

	created_servers = rscloudlib.create_servers(cs, servers)

	if args.block_storage is not None:

		print 'Creating and attaching block storage volumes...'
		cbs = pyrax.connect_to_cloud_blockstorage(region = region)
		for server, admin_pass in created_servers:
			try:
				volume = cbs.create(name = '{}{}'.format(args.volume_base, 
					server.name), size = args.block_storage, volume_type = 
					args.volume_type)
			except Exception, e:
				print 'Error creating volume for server "{}":'.format(server.name), e
				continue
			print 'Created volume {}.'.format(volume.name)
			volue.attach_to_instance(server, mountpoint = args.mount_point)
			volume = wait_until(volume, 'status', 'in-use', interval = 5, 
				attempts = 24, verbose = True)
			if volume is None:
				print 'Error attaching volume to "{}".'.format(server.name)
			else:
				print 'Volume "{}" attached to "{}".\n'.format(volume.name,
																server.name)



if __name__ == '__main__':
	main()
