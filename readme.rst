Enhanced CoC Hotline
====================

.. image:: https://img.shields.io/travis/com/Mariatta/enhanced-coc-hotline/master.svg
    :target: https://travis-ci.com/Mariatta/enhanced-coc-hotline
.. image:: https://codecov.io/gh/mariatta/enhanced-coc-hotline/branch/master/graph/badge.svg
    :target: https://codecov.io/gh/mariatta/enhanced-coc-hotline
.. image:: https://img.shields.io/badge/code%20style-black-000000.svg
    :target: https://github.com/ambv/black

.. image:: https://img.shields.io/badge/Say%20Thanks-!-1EAEDB.svg
    :target: https://saythanks.io/to/Mariatta


This is an enhanced version of the `PyCascades Code of Conduct Hotline
<https://github.com/cache-rules/coc-hotline>`_.

This hotline uses `Nexmo Voice API <https://www.nexmo.com/products/voice>`_ +
`Zapier <https://zapier.com/>`_ integration.


Purpose
-------

When a caller calls the hotline, it will dial each of the PyCascades
Code of Conduct committee members, and the caller will be connected to the first person who answered.

Calls to the hotline can be (optionally) automatically recorded. By default, calls are not recorded.
To autorecord, set both the ``AUTO_RECORD`` and ``ZAPIER_CATCH_HOOK_RECORDING_URL`` environment variables.

For additional details of how to set up the hotline, please read my `Nexmo Developer Spotlight <https://www.nexmo.com/blog/2018/11/15/pycascades-code-of-conduct-hotline-nexmo-voice-api-dr/?sf95092442=1>`_
tutorial, posted November 15, 2018.

Requirements
------------

Python 3.6.5+ because of f-strings.  In reality, Python 3.7 is used (as specified in runtime.txt).


Library Dependencies
--------------------

- aiohttp
- nexmo
- click

Deployment
----------

|Deploy|

.. |Deploy| image:: https://www.herokucdn.com/deploy/button.svg
   :target: https://heroku.com/deploy?template=https://github.com/mariatta/enhanced-coc-hotline

In Heroku, set the environment variables:

- ``NEXMO_APP_ID``: The Nexmo App ID

- ``NEXMO_PRIVATE_KEY_VOICE_APP``: The content of the private key (from private.key file).
  
  It looks like the following:
  ``----- BEGIN PRIVATE KEY ----   blablahblah ---- END PRIVATE KEY ----``

- ``PHONE_NUMBERS``: A list of staff name and phone number dictionaries.

  Example::
  
  [{"name": "Mariatta", "phone": "16040000000"}, {"name": "Miss Islington", "phone": "1778111111"}]


- ``AUTO_RECORD``: set to ``True`` if you want to autorecord incoming calls. This is optional, and will default to ``False`` if not set.

- ``ZAPIER_CATCH_HOOK_RECORDING_URL``: The `Webhooks By Zapier <https://zapier.com/page/webhooks/>`_ url.
  This is only needed if ``AUTO_RECORD`` is ``True``.


Downloading the recording
-------------------------

Requires click 7.0+

Set the environment variables:

- ``NEXMO_APP_ID``: The Nexmo App ID
- ``NEXMO_PRIVATE_KEY_VOICE_APP``: The content of the private key (from private.key file).
  It looks like the following:
  ```----- BEGIN PRIVATE KEY ----   blablahblah ---- END PRIVATE KEY ----```

In the `enhanced-coc-hotline` directory, run::

   $ python3 -m download_recording url1 url2 url3 ...



License
-------

GNU General Public License v3.0.
