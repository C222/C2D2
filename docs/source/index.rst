.. C2D2 documentation master file, created by
   sphinx-quickstart on Fri Feb 26 02:56:53 2016.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

C2D2
====
`Source Code`_

Builtin Commands
----------------

:ban: A cheeky fake ban command.
  
  Usable by owners, mods, and subs.
  
:streamer: Fetch the bio, channel age, previously streamed game, and channel
  link of a given streamer. Results in three chat lines from the bot.
  
  Usable by owners, mods, and subs.

:status: Fetch the current game, resolution, framerate, and viewer count of a
  given stream.
   
  Usable by owners, mods, and subs.

:potatoes: Writes ``Potatoes Potatoes Potatoes <3`` to chat.

:botlove: Writes ``!hug Nightbot`` to chat.

:about: Writes ``I am C2D2, an experimental bot. I have a select few commands
  available and I expand shortened links. My source code is at
  https://github.com/C222/C2D2 . If I break, complain to C222_. Channel owners
  can make me leave with '~part'`` to chat.
  
:part: Forces the bot to leave a stream.
  
  Usable by owners.

Safety
------

The bot can detect shortened and redirect links and finds what the point to.

As of now it writes the following in chat:

``[Shortened link to www(.)example(.)com detected MrDestructoid ]``

Logging
-------

When enabled, all chat from all joined channels is logged into an Apache
Cassandra database. A `schema`_ and a `log viewer`_ Flask applet is provided.

Versitiliy
----------

It's easy to add new commands to the command list. [1]_

Scalable
--------

You can easily install it and run it from multiple servers using the `installation script`_.

API
===

.. toctree::
   :maxdepth: 2

   wsirc
   message
   config
   credentials
   handlers
   hooks
   cassandra_connection


Indices and Tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

.. _Source Code: https://github.com/C222/C2D2
.. _installation script: https://github.com/C222/C2D2/blob/master/utils/get-c2d2.sh
.. _schema: https://github.com/C222/C2D2/blob/master/utils/cassandra-schema.sql
.. _log viewer: https://github.com/C222/C2D2/blob/master/src/logviewer.py

.. [1] If you know Python or are willing to learn.