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
import time

def make_choice(item_list, prompt):

	for index, item in enumerate(item_list):
		print index, item
	choice = -1
	while choice < 0 or choice > len(item_list) - 1:
		try:
			choice = int(raw_input(prompt))
		except ValueError:
			print "Input must be a valid integer."
	return item_list[choice]

def choose_attribute(provider, attr_name = None, prompt = 'Choose an item: '):

    if attr_name is None:
        return make_choice(provider.list(), prompt)
    else:
        attributes = [attr for attr in provider.list() if attr_name in attr.name]
        if attributes is None or len(attributes) < 1:
            print 'Matching attribute not found'
            return make_choice(provider.list(), prompt)
        elif len(attributes) == 1:
            return attributes[0]
        else:
            print 'More than one attribute match found'
            return make_choice(attributes, prompt)

def print_server(server):

	print 'Name:', server.name
	print 'ID:', server.id
	print 'Status:', server.status
	print 'Networks:', server.networks

def print_flavor(flavor):
	print "ID:", flavor.id
	print "Name:", flavor.name
	print "RAM:", flavor.ram
	print "Disk:", flavor.disk
	print "vCPUs:", flavor.vcpus

def set_creds(filename):

	pyrax.set_setting('identity_type', 'rackspace')
	creds_file = os.path.expanduser(filename)
	pyrax.set_credential_file(creds_file)

def choose_region(region):

	regions = list(pyrax.regions)
	while region not in pyrax.regions:
		region = raw_input('Please supply a valid region.\n[' 
			+ ' '.join(regions) + ']: ')
	return region

'''
def track_servers(cs, new_servers, update_freq = 20):
	
	completed = []
	errored = []
	
	total_servers = len(new_servers)
	
	while new_servers:
		time.sleep(update_freq)
		new_servers_copy = list(new_servers)
		for server, admin_pass in new_servers_copy:
			server = cs.servers.get(server.id)
			if server.status == 'ERROR':
				print '{} - Error in server creation.'.format(server.name)
				errored.append((server, admin_pass))
				new_servers.remove((server, admin_pass))
				continue
			print '{} - {}% complete'.format(server.name, server.progress)
			if server.status == 'ACTIVE':
				completed.append((server, admin_pass))
				new_servers.remove((server, admin_pass))
		print '{} of {} server(s) completed.'.format(len(completed), total_servers)
				
	print '{} of {} server(s) completed successfully.'.format(len(completed), total_servers)
	print
	
	for server, admin_pass in sorted(completed, key= lambda item: item[0].name):
		print_server(server)
		print 'Admin Password:', admin_pass
		print
		
	print 'Servers with build errors:', ', '.join([server.name for server in errored])
	
	return (completed, errored)
'''

def track_servers(cs, new_servers, update_freq = 10):
    
    completed = []
    failed = []
    
    total_servers = len(new_servers)
    
    admin_passwords = {}
    for server in new_servers:
        admin_passwords[server.id] = server.adminPass
    
    #admin_passwords = {}
    
    while new_servers:
        
        time.sleep(update_freq)
        new_servers_copy = list(new_servers)
        for server in new_servers_copy:
            server = cs.servers.get(server.id)
            if server.status == 'ERROR':
                print '{} - Error in creation.'.format(server.name)
                failed.append(server)
                new_servers.remove(server)
                continue
            if server.status == 'ACTIVE':
                completed.append(server)
                new_servers.remove(server)
            print '{} - {}% complete'.format(server.name, server.progress)
    
    print '{} of {} server(s) completed successfully.'.format(len(completed), total_servers)
    
    completed.sort(key = lambda item: item.name)
    for server in completed:
        print_server(server)
        print 'Admin Password:', admin_passwords[server.id]
        print
        server.adminPass = admin_passwords[server.id]
        
    print 'Servers with build errors:', ', '.join(sorted([server.name for server in failed]))
    
    return (completed, failed)

def create_servers(cs, servers):

	new_servers = []
	default_nics = {'net-id': pyrax.cloudnetworks.PUBLIC_NET_ID,
					'net-id': pyrax.cloudnetworks.SERVICE_NET_ID}

	for server in servers:
		print 'Creating server "{}" from "{}"...'.format(server['name'], 
			server['image'].name)
		try:
			server_object = cs.servers.create(server['name'], server['image'],
				server['flavor'], files = server.get('files', None), 
				nics = server.get('nics', default_nics))
		except Exception, e:
			print 'Error in server creation: {}'.format(e)
		else:
			new_servers.append((server_object, server_object.adminPass))

	print '\nCredentials:'
	for server, admin_pass in new_servers:
		print server.name, admin_pass
	print

	return new_servers
