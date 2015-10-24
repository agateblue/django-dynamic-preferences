.. :changelog:

Changelog
=========


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
