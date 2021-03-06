from pymoqy.node import Node
from pymoqy.utils import dict_update



class IgnoreValue(object):
    pass



class Path(object):

    _data = None
    _query = None

    def __init__(self, query=None):
        self._data = list()
        self._query = query

    def __repr__(self):
        return '.'.join(self._data)
    __str__ = __repr__

    def __getattr__(self, item):
        if item[:2] == '__':
            return object.__getattribute__(self, item)
        self._data.append(item)
        return self

    def __setattr__(self, key, value):
        if key[0] == '_':
            object.__setattr__(self, key, value)
        elif value is not IgnoreValue:
            parent_key = str(self)
            if parent_key:
                key = parent_key + '.' + key
            self._query and dict_update(self._query.update, {'$set': {key: value}})

    def __delattr__(self, item):
        parent_key = str(self)
        if parent_key:
            item = parent_key + '.' + item
        self._query and dict_update(self._query.update, {'$unset': {item: ''}})


    def __iadd__(self, other):
        try:
            self._query.update['$inc'][str(self)] += other
        except KeyError:
            self._query and dict_update(self._query.update, {'$inc': {str(self): +other}})
        #prevent for setting a value
        return IgnoreValue

    def __isub__(self, other):
        try:
            self._query.update['$inc'][str(self)] -= other
        except KeyError:
            self._query and dict_update(self._query.update, {'$inc': {str(self): -other}})
        #prevent for setting a value
        return IgnoreValue

    def __gt__(self, other):
        return Node({str(self): {'$gt': other}})

    def __ge__(self, other):
        return Node({str(self): {'$gte': other}})

    def __lt__(self, other):
        return Node({str(self): {'$lt': other}})

    def __le__(self, other):
        return Node({str(self): {'$lte': other}})

    def __mod__(self, other):
        return Node({str(self): {'$mod': other}})

    def __eq__(self, other):
        if self._data[-1][:3] == 's__':
            return Node({'.'.join(self._data[:-1]): {'$%s' % self._data[-1][3:]: other}})
        if hasattr(other, 'pattern'):
            #TODO: options for regex
            return Node({str(self): {'$regex': other.pattern}})
        return Node({str(self): {'$eq': other}})

    def __ne__(self, other):
        return Node({str(self): {'$ne': other}})