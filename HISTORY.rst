.. :changelog:

Changelog
=========

1.12.0 (2022-02-26)
*******************

- Add ENABLE_GLOBAL_MODEL_AUTO_REGISTRATION setting (#259)
- fix: checkpreferences command failed if MANAGER_ATTRIBUTE is changed (#258)
- Allow to skip preference creation when checkpreferences is invoked (#257)
- Use default django cache timeoout (#253)
- Fix signal handler doc (#250)
- Added htmlcov in .gitignore (#251)
- Use stdout in checkpreferences (#252)
- MAINT:dynamic_preferences serializers.py  - Exception handling for class ModelMultipleSerializer; types.py - handle queryset in api_reprs of ModelChoicePreference (#243)

1.11.0 (2021-10-09)
*******************

- Update quickstart.rst (#240)
- Fix model multiple choice preference to react correctly to deletion handler (#244)
- fix #234 (#235)
- Fix compatibility issues with python 3.10 and django 4.0 (#236)
- Fixed a typo in documentation (#229)
- Add polish translation (#227)
- Fix the typos in the comments and documents (#225)
- Update forms docs (#224)


1.10.1 (2020-08-21)
*******************

- Fix django 3.0 and 3.1 compat (#218)
- Generated missing user migrations (#221)
- Dropped support for python 2 and Django 1.11
- Updated test matrix

Contributors:

- @Natureshadow
- @agateblue

1.10 (2020-07-03)
*****************

- Add MultipleChoicePreference (#21)

Contributors:

- @Natureshadow

1.9 (2020-05-06)
****************

- Emit signal when a preference is updated (#207)
- Pass instance provided in form builder to manager (#212)
- Use PreferencesManager for saving preferences in forms (#211)
- Fixed wrong filename when using FilePreference and saving multiple times (#198)
- Fixed broken compat with restframework 3.11 (#200)
- Fixed typo in documentation (#204)

Contributors:

- @agateblue
- @hansegucker
- @Natureshadow
- @saemideluxe
- @timgates42

1.8.1 (2019-12-29)
******************

- Django 3.0 and Python 3.8 compatibility (#194)

Contributors:

- @dadoeyad


1.8 (2019-11-06)
******************

- Add time preference type (#187)
- Fix dependency conflict for issue (#183)
- fix(migrations): add missing `verbose_name` (#184)
- Fix crash: 'NoneType' object has no attribute 'name' (#190)
- Test under Django 2.2 and Python 3.7

Contributors:

- @capaci
- @exequiel09
- @NeolithEra
- @nourwolf
- @treemo

1.7.1 (2019-07-30)
******************

- Added djangorestframework 3.10.x compatibility (#180)
- Fixed direct access to ChoicePreference.choice (#177)
- German and missing translations (#175)
- Run makemigrations to add missing migrations file (#161)


Contributors:

- @JITdev
- @izimobil
- @jwaschkau
- @exequiel09


1.7 (2018-11-19)
****************

- Fix string format arguments in get_by_name error (#157)
- Fix UserPreferenceRegistry and its 'section_url_namespace' attribute (#152)
- Handle 'required' attribute for all inherited BasePreferenceType class (#153)
- add section filter in query string for DRF list endpoint (#154)
- Fix ModelChoicePreference when using with model attribute and not queryset (#151)
- Update outdated context_processors documentation (#149)
- Update README.rst (#147)
- Fixed ModelMultipleSerializer.to_python() (#146)
- Added ModelMultipleChoicePreference

Contributors:

- @eriktelepovsky
- @monkeywithacupcake
- @ptrstn
- @jordiromera
- @calvin620707
- @czlee
- @ElManaa

1.6 (2018-06-17)
****************

- Fixed #141 and #141: migrations issues (see below)
- Dropped support for django < 1.11
- Dropped support for Python 3.4
- Better namespaces for urls

Better namespaces for urls
--------------------------

Historically, the package included multiple urls. To ensure compatibility with django 2
and better namespacing, you should update any references to those urls as described below:

+-------------------------------------+-------------------------------------+
| Old url                             | New url                             |
+=====================================+=====================================+
| dynamic_preferences.global          | dynamic_preferences:global          |
+-------------------------------------+-------------------------------------+
| dynamic_preferences.global.section  | dynamic_preferences:global.section  |
+-------------------------------------+-------------------------------------+
| dynamic_preferences.user            | dynamic_preferences:user            |
+-------------------------------------+-------------------------------------+
| dynamic_preferences.user.section    | dynamic_preferences:user.section    |
+-------------------------------------+-------------------------------------+


Migration cleanup
-----------------

This version includes a proper fix for migration issues.
Full background is available at https://github.com/agateblue/django-dynamic-preferences/pull/142,
but here is the gist of it:

1. Early versions of dynamic_preferences included the user and global preferences models
   in the same app
2. The community requested a way to disable user preferences. The only way to do that
   was to move the user preference model in a dedicated app (dynamic_preferences_user
3. A migration was written to handle that transparently, but this was not actually possible
   to have something that worked for both existing and new installations
4. Thus, we ended up with issues such as #140 or #141, inconsistent db state, tables
   lying around in the database, etc.

I'd like to apologize to everyone impacted. By trying to make 3. completely transparent to everyone and
avoid a manual migration step for new installations, I actually made things worse.

This release should fix all that: any remains of the user app was removed from the main
app migrations. For any new user, it will be like nothing happened.

For existing installations with user preferences disabled, there is nothing to do,
apart from deleting the `dynamic_preferences_users_userpreferencemodel` table in your database.

For existing installations with user preferences enabled, there is nothing to do. You should have
``'dynamic_preferences.users.apps.UserPreferencesConfig'`` in your installed apps. If ``python manage.py migrate``
fails with ``django.db.utils.ProgrammingError: relation "dynamic_preferences_users_userpreferencemodel" already exists``,
this probably means you are upgrading for a really old release. In such event, simply skip the initial migration for the
``dynamic_preferences_user`` app by running ``python manage.py migrate dynamic_preferences_users 0001 --fake``.

Many thanks to all people who helped clearing this mess, especially @czlee.

1.5.1 (06-03-2018)
******************

This is a minor bugfix release:

* Get proper PreferenceModelsRegistry when preference is proxy model (#137)
* Add missing `format()` to IntegerSerializer exception text (#138)
* Add some attributes to PerInstancePreferenceAdmin (#135)

Contributors:

* @czlee
* @danie1k

1.5 (16-12-2017)
******************

From now on, django-dynamic-preferences should fully support Django 2.0.
This release should be fully backward-compatible with previous versions
of the module.

You will still have to upgrade your own code to work with Django 2, like
adding on_delete option to your ForeignKey fields.

* removed typo in API code that could cause a crash (#127)
* added on_dete=models.CASCADE to migrations for Django 2.0 compatibility (#129 and #131)
* Duration, date and datetime serialization issue in rest framework (#115)

Contributors:

* @rvignesh89
* @zamai


1.4.2 (06-11-2017)
******************

* Fix #121: reverted Section import missing from dynamic_preferences.types

Contributors:

* @okolimar
* @swalladge


1.4.1 (03-11-2017)
******************

* Section verbose name and filter in django admin (#114)
* Fixed wrong import in Quickstart documentation (#113)
* Fix #111: use path as returned by storage save method (#112)

Contributors:

* @okolimar
* @swalladge


1.4 (15-10-2017)
******************

* Fix #8: we now have date, datetime and duration preferences
* Fix #108: Dropped tests and guaranteed compatibility with django 1.8 and 1.9, though
* Fix #103: bugged filtering of user preferences via REST API
* Fix #78: removed ``create_default_per_instance_preferences``.
  This is *not* considered a backward-incompatible change as this method did nothing at all
  and was not documented

Contributors:

* @rvignesh89
* @haroon-sheikh


1.3.3 (25-09-2017)
******************

* Fix #97 where the API serializer could crash during preference update because of incomplete parsing

Contributors:

* @rvignesh89

1.3.2 (11-09-2017)
******************

* Should fix Python 3.3 complaints in CI, also add tests on Python 3.6 (#94)
* Fixed #75: Fix checkpreferences command that was not deleting obsolete preferences anymore (#93)
* Retrieve existing preferences in bulk (#92)
* Cache values when queried in all() (#91)

Contributors:

* @czlee

1.3.1 (30-07-2017)
******************

- Fix #84: serialization error for preferences with None value (@swalladge)
- More documentation about preferences form fields

1.3 (03-07-2017)
*******************

This release fix a critical bug in 1.2 that can result in data loss.

Please upgrade to 1.3 as soon as possible and never use 1.2 in production. See `#81 <https://github.com/agateblue/django-dynamic-preferences/pull/81>`_ for more details.

1.2 (06-07-2017)
*******************

.. warning::

    There is a critical bug in this that can result in dataloss. Please upgrade to 1.3 as
    soon as possible and never use 1.2 in production. See `#81 <https://github.com/agateblue/django-dynamic-preferences/pull/81>`_ for more details.

- important performance improvements (less database and cache queries)
- A brand new `REST API <https://django-dynamic-preferences.readthedocs.io/en/latest/rest_api.html>`_ based on Django REST Framework, to interact with preferences (this is an optionnal, opt-in feature)
- A new `FilePreference <https://django-dynamic-preferences.readthedocs.io/en/latest/preference_types.html#dynamic_preferences.types.FilePreference>`_ [original work by @macolo]

1.1.1 (11-05-2017)
*******************

Bugfix release to restore disabled user preferences admin (#77).

1.1 (06-03-2017)
*****************

* Fixed #49 and #71 by passing full section objects in templates (and not just the section identifiers). This means it's easier to write template that use sections, for example if you want have i18n in your project and want to display the translated section's name. URL reversing for sections is also more reliable in templates. If you subclassed `PreferenceRegistry`  to implement your own preference class and use the built-in templates, you need to add a ``section_url_namespace`` attribute to your registry class to benefit from the new URL reversing.

[Major release] 1.0 (21-02-2017)
***********************************

Dynamic-preferences was release more than two years ago, and since then, more than 20 feature and bugfixe releases have been published.
But even after two years the project was still advertised as in Alpha-state on PyPi, and  the tags used for the releases, were implicitly saying that the project was not production-ready.

Today, we're changing that by releasing the first major version of dynamic-preferences, the ``1.0`` release. We will stick to semantic versioning and keep backward compatibility until the next major version.

Dynamic-preferences is already used in various production applications .The implemented features are stable, working, and address many of the uses cases the project was designed for:

- painless and efficient global configuration for your project
- painless and efficient per-user (or any other model) settings
- ease-of-use, both for end-user (via the admin interface) and developpers (settings are easy to create and to manage)
- more than decent performance, thanks to caching

By making a major release, we want to show that the project is trustworthy and, in the end, to attract new users and develop the community around it. Development will goes on as before, with an increased focus on stability and backward compatibility.

**Because of the major version switch, some dirt was removed from the code, and manual intervention is required for the upgrade. Please have a for the detailed instructions:** https://django-dynamic-preferences.readthedocs.io/en/latest/upgrade.html

Thanks to all the people who contributed over the years by reporting bugs, asking for new features, working on the documentation or on implementing solutions!

0.8.4 (10-01-2017)
******************

This version is an emergency release to restore backward compatibility that was broken in 0.8.3, as
described in issue #67. Please upgrade as soon as possible if you use 0.8.3.

Special thanks to [czlee](https://github.com/czlee) for reporting this!


0.8.3 (06-01-2017) (**DO NOT USE: BACKWARD INCOMPATIBLE**)
**********************************************************

**This release introduced by mistake a backward incompatible change (commit 723f2e).**
**Please upgrade to 0.8.4 or higher to restore backward compatibility with earlier versions**

This is a small bugfix release. Happy new year everyone!

* Now fetch model default value using the get_default method
* Fixed #50: now use real apps path for autodiscovering, should fix some strange error when using AppConfig and explicit AppConfig path in INSTALLED_APPS
* Fix #63: Added initial doc to explain how to bind preferences to arbitrary models (#65)
* Added test to ensure form submission works when no section filter is applied, see #53
* Example project now works with latest django versions
* Added missing max_length on example model
* Fixed a few typos in example project


0.8.2 (23-08-2016)
******************

* Added django 1.10 compatibility [ricard33]
* Fixed tests for django 1.7
* Fix issue #57: PreferenceManager.get() returns value [ricard33]
* Fixed missing coma in boolean serializer [czlee]
* Added some documentations and example [JetUni]

0.8.1 (25-02-2016)
******************

* Fixed still inconsistend preference order in form builder (#44) [czlee]

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
