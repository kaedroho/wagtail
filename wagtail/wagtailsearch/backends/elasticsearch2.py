from .elasticsearch import ElasticsearchSearchBackend


def get_model_root(model):
    if model._meta.parents:
        return list(model._meta.parents.items())[0][0]

    return model


class Elasticsearch2SearchBackend(ElasticsearchSearchBackend):
    def get_index_for_model(self, model):
        root_model = get_model_root(model)
        index_suffix = '__' + root_model._meta.app_label.lower() + '_' + root_model.__name__.lower()

        return self.index_class(self, self.index_name + index_suffix)

SearchBackend = Elasticsearch2SearchBackend
