"""
This might be a somewhat controversial module because of the conscientious
choice of attempting to extract some kind of unique identifier from a user.

Obviously, anyone can modify whatever is in this module. They can make it
return a `1`, return empty, return something completely random every time
they start the game. The point is that most people do not modify this code
and therefore this module can be used as a deterministic method of creating
a unique identifier for use by servers, alongside IP addresses.

This was not an easy decision. Nevertheless, the unique identifier is good
for the following purposes:
    - Bans
    - Permissions
    - Authentication
    - Registering names

That is about all they are good for; unique identifiers must not be misapplied
or assumed to be more secure than they really are (not secure at all).
"""

import sys
import uuid

NAMESPACE_ANIMATED_CHATROOM = uuid.UUID('8cf1e494-e052-4507-bf88-b7d25004d5d8')

if sys.platform == 'win32':
    import os, subprocess
    def unique_id():
        """
        Get the hexadecimal string of the volume serial by
        invoking the vol command provided by Windows.
        This is a solution that does not require platform-specific
        modules.
        """
        process = subprocess.Popen('vol {}'.format(os.getenv('SystemDrive')), stdout=subprocess.PIPE,
                                   shell=True)
        data = process.communicate()[0].decode("utf-8").split()
        return str(uuid.uuid5(NAMESPACE_ANIMATED_CHATROOM, data[-1]))
else:
    def unique_id():
        return uuid.uuid5(NAMESPACE_ANIMATED_CHATROOM, str(uuid.getnode()))