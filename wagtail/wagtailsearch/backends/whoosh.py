from __future__ import absolute_import

from whoosh import index, fields

from .base import BaseSearch


class WhooshSchema(object):
    TYPE_MAP = {
        'AutoField': 'integer',
        'BinaryField': 'binary',
        'BooleanField': 'boolean',
        'CharField': 'string',
        'CommaSeparatedIntegerField': 'string',
        'DateField': 'date',
        'DateTimeField': 'date',
        'DecimalField': 'double',
        'FileField': 'string',
        'FilePathField': 'string',
        'FloatField': 'double',
        'IntegerField': 'integer',
        'BigIntegerField': 'long',
        'IPAddressField': 'string',
        'GenericIPAddressField': 'string',
        'NullBooleanField': 'boolean',
        'OneToOneField': 'integer',
        'PositiveIntegerField': 'integer',
        'PositiveSmallIntegerField': 'integer',
        'SlugField': 'string',
        'SmallIntegerField': 'integer',
        'TextField': 'string',
        'TimeField': 'date',
    }

    def __init__(self, model):
        self.model = model

    def get_document_type(self):
        return self.model.indexed_get_content_type()

    def get_document_id(self, obj):
        return obj.indexed_get_toplevel_content_type() + ':' + str(obj.pk)

    def get_fields(self):
        return {
            field.get_index_name(model), fields.TEXT()
            for field in self.model.get_search_fields()
        }

    def get_document(self, obj):
        return

    def __repr__(self):
        return '<WhooshSchema: %s>' % (self.model.__name__, )


class WhooshSearch(BaseSearch):
    def __init__(self, params):
        super(ElasticSearch, self).__init__(params)

        self.ix = get_or_create_index('search_index')

    def get_or_create_index(self, index_dir):
        if not index.exists_in(index_dir):
            index.create_in(index_dir)

        return index.open_dir(index_dir)

    def reset_index(self):
        pass

    def add_type(self, model):
        # Get mapping
        mapping = WhooshMapping(model)

        with self.ix.writer() as writer:
            for field_name, field_config in mapping.get_fields().items():
                writer.add_field(field_name, field_config)
            writer.commit()

    def refresh_index(self):
        pass

    def add(self, obj):
        # Make sure the object can be indexed
        if not self.object_can_be_indexed(obj):
            return

        # Get mapping
        mapping = WhooshMapping(obj.__class__)


    def add_bulk(self, obj_list):
        pass

    def delete(self, obj):
        # Object must be a decendant of Indexed and be a django model
        if not isinstance(obj, Indexed) or not isinstance(obj, models.Model):
            return

        pass

    def _search(self, queryset, query_string, fields=None):
        return #ElasticSearchResults(self, ElasticSearchQuery(queryset, query_string, fields=fields))
