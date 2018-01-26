"""
Crawl script

Usage:
    crawl [--ghostery] <site_limit> <sites_files>

--ghostery  Load ghostery extension
"""
from docopt import docopt
import sys
import itertools
from automation import TaskManager, CommandSequence

opts = docopt(__doc__)

# Number of sites to crawl
site_limit = int(opts['<site_limit>'])
sites_files = opts['<sites_files>'].split(',')

def iterate_sites():
    for site_file in sites_files:
        with open(site_file) as fp:
            for line in fp:
                site = line.strip()
                if not site.startswith('http'):
                    site = 'http://' + site
                if not site.endswith('/'):
                    site = site + '/'
                yield site

NUM_BROWSERS = 1
manager_params, browser_params = TaskManager.load_default_params(NUM_BROWSERS)

# Update browser configuration (use this for per-browser settings)
for i in xrange(NUM_BROWSERS):
    browser_params[i]['http_instrument'] = True # Record HTTP Requests and Responses
    browser_params[i]['disable_flash'] = False #Enable flash for all three browsers
    browser_params[i]['screen_res'] = '800x500'
    browser_params[i]['ghostery'] = opts['--ghostery'] == True

# second browser has no third party cookies
# browser_params[1]['tp_cookies'] = 'never'

# Update TaskManager configuration (use this for crawl-wide settings)
manager_params['data_directory'] = '~/'
manager_params['log_directory'] = '~/'

# Instantiates the measurement platform
manager = TaskManager.TaskManager(manager_params, browser_params)

# Visits the sites with all browsers simultaneously
for site in itertools.islice(iterate_sites(), site_limit):
    command_sequence = CommandSequence.CommandSequence(site)

    # Start by visiting the page
    command_sequence.get(sleep=0, timeout=60)

    manager.execute_command_sequence(command_sequence, index='*') # ** = synchronized browsers

# Shuts down the browsers and waits for the data to finish logging
manager.close()
