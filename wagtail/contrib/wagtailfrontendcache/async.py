class BaseQueue(object):
    def __init__(self, params):
        pass

    def enqueue(self, backend_name, urls):
        raise NotImplementedError

    def dequeue(self, backend_name, min=None, max=None):
        raise NotImplementedError


class RedisQueue(BaseQueue):
    def enqueue(self, backend_name, urls):
        pass  # TODO

    def dequeue(self, backend_name, min=None, max=None):
        pass  # TODO


class Worker(object):
    def __init__(self, backend_settings, queue_settings, backends=None):
        self.backends = {
            name: backend
            for name, backend in get_backends(backend_settings, backends).items()
            if backend.async_enabled
        }

        self.queues = {
            name: queue
            for name, queue in get_queues(queue_settings).items()
        }

    def poll(self):
        for backend_name, backend in self.backends.items():
            queue = self.queues[backend.async_queue]
            urls = queue.dequeue(backend_name)

            if urls:
                backend.purge_batch(urls)
