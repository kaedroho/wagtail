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

    return fetch(url, {headers: {'X-Requested-With': 'WagtailShell'}}).then(response => response.json());
}
