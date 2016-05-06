from .elasticsearch import ElasticsearchSearchBackend


class Elasticsearch2SearchBackend(ElasticsearchSearchBackend):
    pass

SearchBackend = Elasticsearch2SearchBackend
