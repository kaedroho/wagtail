let tests = [
    {
        name: 'components/main-menu',
        path: '/admin/',
        user: 'admin',
        selector: 'div.nav-wrapper',
        sizes: [
            [1024, 768],
            [1024, 500],
        ]
    },

    {
        name: 'pages/login',
        path: '/admin/login/',
        user: null,
        sizes: [
            [1024, 768],
            [640, 480],
            [1920, 1200],
        ]
    },
    {
        name: 'pages/login--redirected-from-dashboard',
        path: '/admin/',
        user: null,
        sizes: [
            [1024, 768],
        ]
    },
    {
        name: 'pages/password-reset',
        path: '/admin/password_reset/',
        user: null,
        sizes: [
            [1024, 768],
        ]
    },
    {
        name: 'pages/dashboard',
        path: '/admin/',
        user: 'admin',
        sizes: [
          [1024, 768],
          [640, 480],
          [1920, 1200],
        ]
    },
    {
        name: 'pages/page-explorer-root',
        path: '/admin/pages/',
        user: 'admin',
        sizes: [
          [1024, 768],
          [640, 480],
          [1920, 1200],
        ]
    },
    {
        name: 'pages/page-explorer',
        path: '/admin/pages/2/',
        user: 'admin',
        sizes: [
          [1024, 768],
        ]
    },
    {
        name: 'pages/edit-page',
        path: '/admin/pages/2/edit/',
        user: 'admin',
        sizes: [
          [1024, 768],
          [640, 480],
          [1920, 1200],
        ]
    },
    {
        name: 'pages/add-page',
        path: '/admin/pages/2/add_subpage/',
        user: 'admin',
        sizes: [
          [1024, 768],
          [640, 480],
          [1920, 1200],
        ]
    },
    {
        name: 'pages/add-page-editor',
        path: '/admin/pages/add/demosite/homepage/1/',
        user: 'admin',
        sizes: [
          [1024, 768],
          [640, 480],
          [1920, 1200],
        ]
    },
    {
        name: 'pages/image-index',
        path: '/admin/images/',
        user: 'admin',
        sizes: [
          [1024, 768],
          [640, 480],
          [1920, 1200],
        ]
    },
    {
        name: 'pages/document-index',
        path: '/admin/documents/',
        user: 'admin',
        sizes: [
          [1024, 768],
          [640, 480],
          [1920, 1200],
        ]
    },
];

let BASE_URL = 'http://localhost:8000';

let webshot = require('webshot');


for (let {name, path, user, sizes, selector=false} of tests) {
    for (let [width, height] of sizes) {
        webshot(BASE_URL + path, `screenshots/${name}-${width}x${height}.png`, {
            screenSize: {width, height},
            shotSize: {width, height},
            customHeaders: {
                AUTHUSER: user,
            },
            captureSelector: selector,
        }, function() {});
    }
}
