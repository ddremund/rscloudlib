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

def make_choice(item_list, prompt):

	for index, item in enumerate(item_list):
		print index, item
	selection = -1
	while selection < 0 or selection > len(item_list) - 1:
		selection = raw_input(prompt)
	return item_list[selection]

def flavor_menu(cs, prompt, min_id=2):

	flavors = cs.flavors.list()
	minimum_ram = cs.flavors.get(min_id).ram
	flavors = [flavor for flavor in flavors if flavor.ram >= minimum_ram]
	
	print '\nValid flavors: \n'
	for index, flavor in enumerate(flavors):
		print 'Choice ', index
		print 'ID | Name:', '{} | {}'.format(flavor.id, flavor.name)
		print 'RAM:', flavor.ram
		print 'Disk:', flavor.disk
		print 'vCPUs:', flavor.vcpus
		print

	choice = -1
	while choice < 0 or choice > len(flavors) - 1:
		if choice is not None:
			print ' ** Not a valid flavor ID ** '
		choice = raw_input(prompt)
	return flavors[choice]

def fuzzy_choose_image(cs, prompt, image_name = None):

	if image_name is None:
		return make_choice(cs.images.list(), prompt)
	else:
		images = [img for img in cs.images.list() if image_name in img.name]
		if image == None or len(image) < 1:
			print 'Matching image not found'
			return make_choice(cs.images.list(), prompt)
		elif len(images) == 1:
			return images[0]
		else:
			print 'More than one image match found'
			return make_choice(images, prompt)

def print_server(server):

	print 'Name:', server.name
	print 'ID:', server.id
	print 'Status:', server.status
	print 'Networks:', server.networks

def set_creds(filename):

	pyrax.set_setting('identity_type', 'rackspace')
	creds_file = os.path.expanduser(filename)
	pyrax.set_credential_file(creds_file)

def choose_region(region):

	regions = list(pyrax.regions)
	while region not in pyrax.regions:
		region = raw_input('Please supply a valid region.\n[' 
			+ ' '.join(regions) + ']: ')

def create_servers(cs, servers):

	new_servers = []
	default_nics = {'net-id': pyrax.cloudnetworks.PUBLIC_NET_ID,
					'net-id': pyrax.cloudnetworks.SERVICE_NET_ID}

	for server in server_list:
		print 'Creating server "{}" from "{}"...'.format(server['name'], 
			server['image'].name)
		try:
			server_object = cs.servers.create(server['name'], server['image'],
				server['flavor'], files = server.get(files, None), 
				nics = server.get(nics, default_nics), 
				meta = server.get(meta, None))
		except Exception, e:
			print 'Error in server creation: {}'.format(e)
		else:
			new_servers.append((server_object, server_object.adminPass))

	completed = []
	errored = []
	total_servers = len(new_servers)

	while new_servers:
		time.sleep(20)
		new_servers_copy = list(new_servers)
		for server, admin_pass in new_servers_copy:
			server = cs.servers.get(server.id)
			if server.status == 'ERROR':
				print '{} - Error in server creation.'.format(server.name)
				errored.append((server, admin_pass))
				new_servers.remove((server, admin_pass))
				total_servers -= 1
				continue
			print '{} - {}% complete'.format(server.name, server.progress)
			if server.status == 'ACTIVE':
				completed.append((server, admin_pass))
				new_servers.remove((server, admin_pass))
			
		print '{} of {} servers completed'.format(len(completed), total_servers)
				

	print '\n{} Server(s) created.\n'.format(len(completed))
	for server, admin_pass in sorted(completed, key= lambda item: item[0].name): 
		print_server(server)
		print 'Admin Password:', admin_pass
		print

	print 'Servers with build errors:', ' '.join([server.name 
												for server in errored])

	return completed