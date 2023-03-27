import collections

def dict_value_by_flatten_key(dict_record, flatten_key):
    return reduce(lambda d, k: d.get(k) if isinstance(d, dict) else None,
                  flatten_key.split('.'),
                  dict_record)


def flatten_dict(d, parent_key='', sep='_'):
    items = []
    for k, v in d.items():
        new_key = parent_key + sep + k if parent_key else k
        if isinstance(v, collections.abc.MutableMapping):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)