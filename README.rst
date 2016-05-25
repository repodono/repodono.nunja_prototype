==============
repodono.nunja
==============

A minimum framework to allow the sharing of common templates required by
Python-based backends with client side updates done in JavaScript.  This
is achieved by making use of minimum Jinja2 templates with the `Jinja2`_
Python package and the `Nunjucks`_ JavaScript package.

This package also ships with some useful templates to address the most
commonly applied use cases where template duplication is typically seen
in systems that do not make use of a unified system like this one.

.. _Jinja2: http://jinja.pocoo.org/
.. _Nunjucks: http://mozilla.github.io/nunjucks/


Features
--------

The package provides a single framework to develop and test templates
that target the Jinja2 templating engine in both python and javascript.


Installation
------------

Currently under development, please install by cloning this repository
and run ``python setup.py develop`` within your environment, or follow
your framework's method on installation of development packages.


Contribute
----------

- Issue Tracker: https://github.com/repodono/repodono.nunja/issues
- Source Code: https://github.com/repodono/repodono.nunja


License
-------

The project is licensed under the GPLv2.
