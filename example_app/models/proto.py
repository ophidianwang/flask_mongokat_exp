# -*- coding: utf-8 -*-
from mongokat import Collection, Document

class proto_document(Document):
    """document class that contains data
    """

    def __repr__(self):
        return '<proto %r>' % (self['name'])


class proto(Collection):
    """interface class which inherit mongokat Collection
    """
    document_class = proto_document
    structure = {
        'name': unicode,
        'email': unicode,
    }
