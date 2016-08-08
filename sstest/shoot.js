let tests = [
    {
        name: 'components/main-menu',
        path: '/admin/',
        user: 'admin',
        selector: 'div.nav-wrapper',
        sizes: [
            [1024, 768],
        ]
    },

    {
        name: 'pages/login',
        path: '/admin/login/',
        user: null,
        sizes: [
            [1024, 768],
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
        name: 'pages/dashboard',
        path: '/admin/',
        user: 'admin',
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
