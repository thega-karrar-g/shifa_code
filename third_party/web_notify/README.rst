==========
Web Notify
==========

.. !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
   !! This file is generated by oca-gen-addon-readme !!
   !! changes will be overwritten.                   !!
   !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

.. |badge1| image:: https://img.shields.io/badge/maturity-Production%2FStable-green.png
    :target: https://odoo-community.org/page/development-status
    :alt: Production/Stable
.. |badge2| image:: https://img.shields.io/badge/licence-AGPL--3-blue.png
    :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
    :alt: License: AGPL-3
.. |badge3| image:: https://img.shields.io/badge/github-OCA%2Fweb-lightgray.png?logo=github
    :target: https://github.com/OCA/web/tree/14.0/web_notify
    :alt: OCA/web
.. |badge4| image:: https://img.shields.io/badge/weblate-Translate%20me-F47D42.png
    :target: https://translation.odoo-community.org/projects/web-14-0/web-14-0-web_notify
    :alt: Translate me on Weblate
.. |badge5| image:: https://img.shields.io/badge/runbot-Try%20me-875A7B.png
    :target: https://runbot.odoo-community.org/runbot/162/14.0
    :alt: Try me on Runbot

|badge1| |badge2| |badge3| |badge4| |badge5| 

Send instant notification messages to the user in live.

This technical module allows you to send instant notification messages from the server to the user in live.
Two kinds of notification are supported.

* Success: Displayed in a `success` theme color flying popup div
* Danger: Displayed in a `danger` theme color flying popup div
* Warning: Displayed in a `warning` theme color flying popup div
* Information: Displayed in a `info` theme color flying popup div
* Default: Displayed in a `default` theme color flying popup div

**Table of contents**

.. contents::
   :local:

Installation
============

This module is based on the Instant Messaging Bus. To work properly, the server must be launched in gevent mode.

Usage
=====


To send a notification to the user you just need to call one of the new methods defined on res.users:

.. code-block:: python

   self.env.user.notify_success(message='My success message')

or

.. code-block:: python

   self.env.user.notify_danger(message='My danger message')

or

.. code-block:: python

   self.env.user.notify_warning(message='My warning message')

or

.. code-block:: python

   self.env.user.notify_info(message='My information message')

or

.. code-block:: python

   self.env.user.notify_default(message='My default message')

.. figure:: https://raw.githubusercontent.com/OCA/web/14.0/web_notify/static/description/notifications_screenshot.png
   :scale: 80 %
   :alt: Sample notifications

You can test the behaviour of the notifications by installing this module in a demo database.
Access the users form through Settings -> Users & Companies. You'll see a tab called "Test web notify", here you'll find two buttons that'll allow you test the module.

.. figure:: https://raw.githubusercontent.com/OCA/web/14.0/web_notify/static/description/test_notifications_demo.png
   :scale: 80 %
   :alt: Sample notifications

Bug Tracker
===========

Bugs are tracked on `GitHub Issues <https://github.com/OCA/web/issues>`_.
In case of trouble, please check there if your issue has already been reported.
If you spotted it first, help us smashing it by providing a detailed and welcomed
`feedback <https://github.com/OCA/web/issues/new?body=module:%20web_notify%0Aversion:%2014.0%0A%0A**Steps%20to%20reproduce**%0A-%20...%0A%0A**Current%20behavior**%0A%0A**Expected%20behavior**>`_.

Do not contact contributors directly about support or help with technical issues.

Credits
=======

Authors
~~~~~~~

* ACSONE SA/NV
* AdaptiveCity

Contributors
~~~~~~~~~~~~

* Laurent Mignon <laurent.mignon@acsone.eu>
* Serpent Consulting Services Pvt. Ltd.<jay.vora@serpentcs.com>
* Aitor Bouzas <aitor.bouzas@adaptivecity.com>
* Shepilov Vladislav <shepilov.v@protonmail.com>
* Kevin Khao <kevin.khao@akretion.com>

Maintainers
~~~~~~~~~~~

This module is maintained by the OCA.

.. image:: https://odoo-community.org/logo.png
   :alt: Odoo Community Association
   :target: https://odoo-community.org

OCA, or the Odoo Community Association, is a nonprofit organization whose
mission is to support the collaborative development of Odoo features and
promote its widespread use.

This module is part of the `OCA/web <https://github.com/OCA/web/tree/14.0/web_notify>`_ project on GitHub.

You are welcome to contribute. To learn how please visit https://odoo-community.org/page/Contribute.
