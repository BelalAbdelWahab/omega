"""Print working directory

SYNOPSIS:
    pwd

DESCRIPTION:
    Print the absolute path name of current/working remote
    directory on target server.

    * PASSIVE PLUGIN:
    No requests are sent to server, as current directory
    is known by $PWD environment variable (`env PWD`)

AUTHOR:
    entynetproject <http://goo.gl/kb2wf>
"""

from api import environ

print(environ['PWD'])
