export interface Stylesheet {
    type: 'text/css',
    src: string,
}

interface ShellResponseLoadIt {
    status: 'load-it';
}

interface ShellResponseRenderHtml {
    status: 'render-html';
    title: string;
    html: string;
    stylesheets: Stylesheet[];
}

interface ShellResponseRenderClientSideView {
    status: 'render-client-side-view';
    view: string;
    context: any;
}

interface ShellResponseNotFound {
    status: 'not-found';
}

interface ShellResponsePermissionDenied {
    status: 'permission-denied';
}

export type ShellResponse = ShellResponseLoadIt
                          | ShellResponseRenderHtml
                          | ShellResponseRenderClientSideView
                          | ShellResponseNotFound
                          | ShellResponsePermissionDenied;

export function shellFetch(url: string): Promise<ShellResponse> {
    if (!url.startsWith('/admin/')) {
        return Promise.resolve({
            status: 'load-it',
        });
    }

    return fetch(url, {headers: {'X-Requested-With': 'WagtailShell'}})
    .then(response => {
        if (!response.headers.get('X-WagtailShellStatus')) {
            console.warn("WagtailShell Warning: A non-JSON response was returned from the server. Did you forget to add the 'download' attribute to an '<a>' tag?")
            return {
                status: 'load-it',
            };
        }

        return response.json()
    });
}
