class Field(object):
    def __init__(self, name, meta=False, default=False):
        self.name = name
        self.meta = meta
        self.default = default

    def __str__(self):
        return name

    def __repr__(self):
        return '<APIField {}>'.format(name)
