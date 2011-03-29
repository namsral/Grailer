## Grailer

Get notified by Growl when new message arrive in your Gmail or Google Apps Gmail accounts.

**Setup**

1. Download or clone this project to a safe location:

        mv Grailer ~/.grailer

2. Add your Gmail or Google Apps Gmail accounts to accounts.json and make sure this file is readable only by you:

        chmod 600 accounts.json

3. Add a cronjob to check for new messages every 10 minutes:

        */10 * * * * /usr/bin/env python ~/.grailer/grailer.py --config-path ~/.grailer


!On the first run Growl messages are suppressed to prevent Growl notifications overload.
