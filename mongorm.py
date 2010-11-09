# Todo: make this a threadlocal
identity_map = {}

def identity_map_hit(result):
    return result

class Record(object):
    def __new__(class_, *args, **kwargs):
        # TODO: handle the case of ObjectId vs non-ObjectId in the _id field
        if '_id' in kwargs and kwargs['_id'] in identity_map:
            return identity_map[id]

        instance = super(Record, class_).__new__(class_)

        if '_id' in kwargs:
            identity_map[id] = instance

        return instance

    def __init__(self, **kwargs):
        self._data = kwargs

    def __repr__(self, **kwargs):
        return "<%s %s>" % (self.__class__, self._data)

    @classmethod
    def _resolve_collection(cls, collection=None):
        if not collection:
            collection = getattr(cls, '_collection', None)
            if not collection:
                raise Exception, "No collection selected"

        # Collection may be a name, or an actual collection
        if isinstance(collection, basestring):
            collection = db[collection]

        return collection

    def save(self, _collection=None):
        collection = self._resolve_collection(_collection)
        id = collection.save(self._data)
        identity_map[id] = self
        return id

    @classmethod
    def find(cls, _collection=None, **kwargs):
        collection = cls._resolve_collection(_collection)
        results = collection.find(kwargs)
        return [cls(**result) for result in results]

    @classmethod
    def find_one(cls, _collection=None, **kwargs):
        collection = cls._resolve_collection(_collection)
        result = collection.find_one(kwargs)
        if result:
            return cls(**result)

    @classmethod
    def count(cls, _collection=None, **kwargs):
        collection = cls._resolve_collection(_collection)
        return collection.count(kwargs)

class User(Record):
    _collection = 'user'


if __name__ == "__main__":
    a = User(name='bob')
    a.save()
    b = User.find_one(name='bob')
    #assert a == b
