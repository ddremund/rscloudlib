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
    parser.add_argument('-c', '--creds_file', default = default_creds_file, 
        help = 'Location of credentials file; '
        'defaults to {}'.format(default_creds_file))

    args = parser.parse_args()

    rscloudlib.set_creds(args.creds_file)
    region = rscloudlib.choose_region(args.region)

    cs = pyrax.connect_to_cloudservers(region = region)	

    flavor = rscloudlib.fuzzy_choose_flavor(cs, prompt, args.flavor_ram)
    image = rscloudlib.fuzzy_choose_image(cs, prompt, args.image_name)

    if args.networks is not None:
    	cnw = pyrax.connect_to_cloud_networks(region = region)
    	

    servers = []
    for i in range(args.start, args.start + args.number)
    	servers.append({'name': '{}{}'.format(args.base, i),
    					'image': iamge,
    					'flavor': flavor,
    					})
    rscloudlib.create_servers(cs, servers)

if __name__ == '__main__':
	main()