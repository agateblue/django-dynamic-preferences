try:
    from collections.abc import Mapping
except ImportError:
    from collections import Mapping

from .settings import preferences_settings
from .exceptions import CachedValueNotFound, DoesNotExist
from .signals import preference_updated


class PreferencesManager(Mapping):

    """Handle retrieving / caching of preferences"""

    def __init__(self, model, registry, **kwargs):
        self.model = model
        self.registry = registry
        self.instance = kwargs.get("instance")

    @property
    def queryset(self):
        qs = self.model.objects.all()
        if self.instance:
            qs = qs.filter(instance=self.instance)
        return qs

    @property
    def cache(self):
        from django.core.cache import caches

        return caches[preferences_settings.CACHE_NAME]

    def __getitem__(self, key):
        return self.get(key)

    def __setitem__(self, key, value):
        section, name = self.parse_lookup(key)
        preference = self.registry.get(section=section, name=name, fallback=False)
        preference.validate(value)
        self.update_db_pref(section=section, name=name, value=value)

    def __repr__(self):
        return repr(self.all())

    def __iter__(self):
        return self.all().__iter__()

    def __len__(self):
        return len(self.all())

    def by_name(self):
        """Return a dictionary with preferences identifiers and values, but without the section name in the identifier"""
        return {
            key.split(preferences_settings.SECTION_KEY_SEPARATOR)[-1]: value
            for key, value in self.all().items()
        }

    def get_by_name(self, name):
        return self.get(self.registry.get_by_name(name).identifier())

    def get_cache_key(self, section, name):
        """Return the cache key corresponding to a given preference"""
        if not self.instance:
            return "dynamic_preferences_{0}_{1}_{2}".format(
                self.model.__name__, section, name
            )
        return "dynamic_preferences_{0}_{1}_{2}_{3}".format(
            self.model.__name__, self.instance.pk, section, name, self.instance.pk
        )

    def from_cache(self, section, name):
        """Return a preference raw_value from cache"""
        cached_value = self.cache.get(
            self.get_cache_key(section, name), CachedValueNotFound
        )

        if cached_value is CachedValueNotFound:
            raise CachedValueNotFound

        if cached_value == preferences_settings.CACHE_NONE_VALUE:
            cached_value = None
        return self.registry.get(section=section, name=name).serializer.deserialize(
            cached_value
        )

    def many_from_cache(self, preferences):
        """
        Return cached value for given preferences
        missing preferences will be skipped
        """
        keys = {p: self.get_cache_key(p.section.name, p.name) for p in preferences}
        cached = self.cache.get_many(list(keys.values()))

        for k, v in cached.items():
            # we replace dummy cached values by None here, if needed
            if v == preferences_settings.CACHE_NONE_VALUE:
                cached[k] = None

        # we have to remap returned value since the underlying cached keys
        # are not usable for an end user
        return {
            p.identifier(): p.serializer.deserialize(cached[k])
            for p, k in keys.items()
            if k in cached
        }

    def to_cache(self, pref):
        """
        Update/create the cache value for the given preference model instance
        """
        key = self.get_cache_key(pref.section, pref.name)
        value = pref.raw_value
        if value is None or value == "":
            # some cache backends refuse to cache None or empty values
            # resulting in more DB queries, so we cache an arbitrary value
            # to ensure the cache is hot (even with empty values)
            value = preferences_settings.CACHE_NONE_VALUE
        self.cache.set(key, value)

    def pref_obj(self, section, name):
        return self.registry.get(section=section, name=name)

    def parse_lookup(self, lookup):
        try:
            section, name = lookup.split(preferences_settings.SECTION_KEY_SEPARATOR)
        except ValueError:
            name = lookup
            section = None
        return section, name

    def get(self, key, no_cache=False):
        """Return the value of a single preference using a dotted path key
        :arg no_cache: if true, the cache is bypassed
        """
        section, name = self.parse_lookup(key)
        preference = self.registry.get(section=section, name=name, fallback=False)
        if no_cache or not preferences_settings.ENABLE_CACHE:
            return self.get_db_pref(section=section, name=name).value

        try:
            return self.from_cache(section, name)
        except CachedValueNotFound:
            pass

        db_pref = self.get_db_pref(section=section, name=name)
        self.to_cache(db_pref)
        return db_pref.value

    def get_db_pref(self, section, name):
        try:
            pref = self.queryset.get(section=section, name=name)
        except self.model.DoesNotExist:
            pref_obj = self.pref_obj(section=section, name=name)
            pref = self.create_db_pref(
                section=section, name=name, value=pref_obj.get("default")
            )

        return pref

    def update_db_pref(self, section, name, value):
        try:
            db_pref = self.queryset.get(section=section, name=name)
            old_value = db_pref.value
            db_pref.value = value
            db_pref.save()
            preference_updated.send(
                sender=self.__class__,
                section=section,
                name=name,
                old_value=old_value,
                new_value=value,
            )
        except self.model.DoesNotExist:
            return self.create_db_pref(section, name, value)

        return db_pref

    def create_db_pref(self, section, name, value):
        kwargs = {
            "section": section,
            "name": name,
        }
        if self.instance:
            kwargs["instance"] = self.instance

        # this is a just a shortcut to get the raw, serialized value
        # so we can pass it to get_or_create
        m = self.model(**kwargs)
        m.value = value
        raw_value = m.raw_value

        db_pref, created = self.model.objects.get_or_create(**kwargs)
        if created and db_pref.raw_value != raw_value:
            db_pref.raw_value = raw_value
            db_pref.save()

        return db_pref

    def all(self):
        """Return a dictionary containing all preferences by section
        Loaded from cache or from db in case of cold cache
        """
        if not preferences_settings.ENABLE_CACHE:
            return self.load_from_db()

        preferences = self.registry.preferences()

        # first we hit the cache once for all existing preferences
        a = self.many_from_cache(preferences)
        if len(a) == len(preferences):
            return a  # avoid database hit if not necessary

        # then we fill those that miss, but exist in the database
        # (just hit the database for all of them, filtering is complicated, and
        # in most cases you'd need to grab the majority of them anyway)
        a.update(self.load_from_db(cache=True))
        return a

    def load_from_db(self, cache=False):
        """Return a dictionary of preferences by section directly from DB"""
        a = {}
        db_prefs = {p.preference.identifier(): p for p in self.queryset}
        for preference in self.registry.preferences():
            try:
                db_pref = db_prefs[preference.identifier()]
            except KeyError:
                db_pref = self.create_db_pref(
                    section=preference.section.name,
                    name=preference.name,
                    value=preference.get("default"),
                )
            else:
                # cache if create_db_pref() hasn't already done so
                if cache:
                    self.to_cache(db_pref)

            a[preference.identifier()] = db_pref.value

        return a
