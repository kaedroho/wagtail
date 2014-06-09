from django.http import Http404


def get_pages_for_path(page, path_components):
    while page is not None:
        # Yield this page
        yield page.specific, path_components

        # If there are no more path components 
        if len(path_components) == 0:
            return

        # Get next page
        page = page.get_children().filter(slug=path_components[0]).first()

        # Remove first path component
        path_components = path_components[1:]


def serve(request, path):
    # we need a valid Site object corresponding to this request (set in wagtail.wagtailcore.middleware.SiteMiddleware)
    # in order to proceed
    if not request.site:
        raise Http404

    path_components = [component for component in path.split('/') if component]

    for page, remaining_components in get_pages_for_path(request.site.root_page, path_components):
        print page, remaining_components
        response = page.process_request(request, remaining_components)

        if response is not None:
            return response
