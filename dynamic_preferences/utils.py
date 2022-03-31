try:
    from collections.abc import Mapping
except ImportError:
    from collections import Mapping


def update(d, u):
    """
    Custom recursive update of dictionary
    from http://stackoverflow.com/questions/3232943/update-value-of-a-nested-dictionary-of-varying-depth
    """
    for k, v in u.iteritems():
        if isinstance(v, Mapping):
            r = update(d.get(k, {}), v)
            d[k] = r
        else:
            d[k] = u[k]
    return d
