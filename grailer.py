#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Grailer - Get notified by Growl when new message arrive in your Gmail or Google Apps Gmail accounts.

version 0.3 29 mrt 2011
version 0.2 24 apr 2010
version 0.1 24 jul 2007

I might have reused some code from other similar projects but since it has been four years i can't remember. Please contact me if you see your code and I will give credit where credit is due.
'''

from __future__ import with_statement

__author__ = "Lars Wiegman <lars@namsral.com>"
__version__ = '0.3'
__docformat__ = 'plaintext'
__license__ = 'MIT'
__copyright__ = "Copyright (c) 2011, Lars Wiegman"

import os
import sys
import urllib2
from optparse import OptionParser

try:
    import feedparser
except ImportError:
    print "Could not import the the feedparser module, make sure it is installed."
    sys.exit(1)

try:
    import Growl
except ImportError:
    print "Could not import the the Growl module, make sure it is installed."
    sys.exit(1)

try:
    import json
except ImportError:
    import simplejson as json

class Inbox:
    '''Check multiple Gmail accounts for new email. Works with a cache
    to only return new emails since last check'''
    
    def __init__(self, accounts, cache, icon):
        self.accounts = accounts
        self.cache = cache
        self.icon = icon
        self.url = 'https://mail.google.com/gmail/feed/atom'
        self.uri = 'mail.google.com'
        self.realm = 'New mail feed'
    
    def fetch(self, username, password):
        auth = urllib2.HTTPBasicAuthHandler()
        auth.add_password(self.realm, self.uri, username, password)
        opener = urllib2.build_opener(auth)
        urllib2.install_opener(opener)
        return feedparser.parse(urllib2.urlopen(self.url).read())

    def sendgrowl(self, title, message):
        appicon = open(self.icon, 'r').read()
        notifications = ["new email"]
        notifier = Growl.GrowlNotifier('Gmail Notifier', notifications, applicationIcon=appicon)
        notifier.register()
        notifier.notify(notifications[0], title, message, sticky=True)
    
    def rotate_cache(self, new, old, limit=50):
        '''Rotating the cache prevents multiple notifications for unread messages.'''
        for k in new.keys():
            if k in old.keys() and len(old[k]) > 0:
                new[k] += old[k]
                new[k].sort()
                new[k] = new[k][-limit:]
        f = open(self.cache, 'w')
        json.dump(new, f)
        f.close()
        
    def notify(self):
        first_run = False
        new_cache = {}
        old_cache = {}
        for account in self.accounts:
            new_cache[account['username']] = []
            old_cache[account['username']] = []
        try:
            f = open(self.cache, 'r')
            old_cache = json.load(f)
            f.close()
        except:
            print "Could not read cache: %s" % self.cache
        if len(old_cache) < 1:
            first_run = True
        for account in self.accounts:
            d = self.fetch(account['username'], account['password'])
            for email in d.entries:
                email_id = email.id.split(':')[-1]
                if first_run or email_id not in old_cache[account['username']]:
                    title = account['username']
                    message = 'From: %s\n%s' % (email.author_detail['name'], email.summary)
                    if not first_run:
                        self.sendgrowl(title, message)
                new_cache[account['username']].append(email_id)
        self.rotate_cache(new_cache, old_cache)
    
def main():
    default_config_path = os.path.join(os.path.expanduser('~'), '.grailer')
    
    parser = OptionParser(version="grailer %s" % __version__)
    parser.add_option("-c", "--config-path", dest="config_path", default=default_config_path,
        help="path to alternative configuration directory, defaults to %s" % default_config_path)
    parser.add_option("-i", "--icon-path", dest="icon_path",
        help="path to alternative Growl icon for Gmail notifications")
    parser.add_option("-a", "--accounts-path", dest="accounts_path",
        help="path to alternative accounts JSON file")
    
    (options, args) = parser.parse_args()
    
    default_config_path = options.config_path
    cache_path = os.path.join(default_config_path, 'cache.json')
    
    if options.icon_path:
        icon_path = os.path.join(options.icon_path)
    else:
        icon_path = os.path.join(default_config_path, 'icon.png')
        
    if options.accounts_path:
        accounts_path = os.path.join(options.accounts_path)
    else:
        accounts_path = os.path.join(default_config_path, 'accounts.json')
    
    for file in [accounts_path, icon_path, cache_path]:
        if not os.access(file, 4):
            print "Could not access: %s" % file
            sys.exit(1)
    
    accounts = json.load(open(accounts_path, 'r'))
    email = Inbox(accounts, cache_path, icon_path)
    email.notify()

if __name__ == "__main__":
    main()