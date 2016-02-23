.. :changelog:

Changelog
=========

0.8 (23-02-2016)
****************

**Warning**: there is a backward incompatbile change in this release. To address #45 and #46, an
import statement was removed from __init__.py. Please refer to the documentation for upgrade instructions:
http://django-dynamic-preferences.readthedocs.org/en/stable/upgrade.html

0.7.2 (23-02-2016)
******************

* Fix #45: importerrror on pip install, and removed useless import
* Replaced built-in registries by persisting_theory, this will maintain a consistent order for preferences, see #44

0.7.1 (12-02-2016)
******************

* Removed useless sections and fixed typos/structure in documentation, fix #39
* Added setting to disable user preferences admin, see #33
* Added setting to disable preference caching, fix #7
* Added validation agains sections and preferences names, fix #28, it could raise backward incompatible behaviour, since invalid names will stop execution by default

0.7 (12-01-2016)
****************

* Added by_name and get_by_name methods on manager to retrieve preferences without using sections, fix #34
* Added float preference, fix #31 [philipbelesky]
* Made name, section read-only in django admin, fix #36 [what-digital]
* Fixed typos in documentation [philipbelesky]

0.6.6 (23-12-2015)
******************

* Fixed #23 (again bis repetita): Fixed second migration to create section and name columns with correct length

0.6.5 (23-12-2015)
******************

* Fixed #23 (again): Fixed initial migration to create section and name columns with correct length

0.6.4 (23-12-2015)
******************

* Fixed #23: Added migration for shorter names and sections

0.6.3 (09-12-2015)
******************

* Fixed #27: AttributeError: 'unicode' object has no attribute 'name' in preference `__repr__` [pomerama]

0.6.2 (24-11-2015)
******************

* Added support for django 1.9, [yurtaev]
* Better travic CI conf (which run tests against two version of Python and three versions of django up to 1.9), fix #22 [yurtaev]

0.6.1 (6-11-2015)
*****************

* Added decimal field and serializer

0.6 (24-10-2015)
****************

* Fixed #10 : added model choice preference
* Fixed #19 : Sections are now plain python objects, the string notation is now deprecated

0.5.4 (06-09-2015)
******************

* Merged PR #16 that fix a typo in the code

0.5.3 (24-08-2015)
******************

* Added switch for list_editable in admin and warning in documentation, fix #14
* Now use Textarea for LongStringPreference, fix #15

0.5.2 (22-07-2015)
******************

* Fixed models not loaded error

0.5.1 (17-07-2015)
******************

* Fixed pip install (#3), thanks @willseward
* It's now easier to override preference form field attributes on a preference (please refer to `Preferences attributes <http://django-dynamic-preferences.readthedocs.org/en/latest/quickstart.html#preferences-attributes>`_  for more information)
* Cleaner serializer api

0.5 (12-07-2015)
****************

This release may involves some specific upgrade steps, please refer to the ``Upgrade`` section of the documentation.

0.5 (12-07-2015)
****************

This release may involves some specific upgrade steps, please refer to the ``Upgrade`` section of the documentation.

* Migration to CharField for section and name fields. This fix MySQL compatibility issue #2
* Updated example project to the 0.4 API

0.4.2 (05-07-2015)
******************

* Minor changes to README / docs

0.4.1 (05-07-2015)
******************

* The cookiecutter part was not fully merged

0.4 (05-07-2015)
****************

* Implemented cache to avoid database queries when possible, which should result in huge performance improvements
* Whole API cleanup, we now use dict-like objects to get preferences values, which simplifies the code a lot (Thanks to Ryan Anguiano)
* Migrated the whole app to cookiecutter-djangopackage layout
* Docs update to reflect the new API

0.3.1 (10-06-2015)
******************

* Improved test setup
* More precise data in setup.py classifiers

0.2.4 (14-10-2014)
******************

* Added Python 3.4 compatibility

0.2.3 (22-08-2014)
******************

* Added LongStringPreference

0.2.2 (21-08-2014)
******************

* Removed view that added global and user preferences to context. They are now replaced by template context processors

0.2.1 (09-07-2014)
******************

* Switched from GPLv3 to BSD license
