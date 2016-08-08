let tests = [
    {
        name: 'login',
        path: '/admin/login/',
        user: null,
        sizes: [
            [1024, 768],
        ]
    },
    {
        name: 'login-redirected-from-dashboard',
        path: '/admin/',
        user: null,
        sizes: [
            [1024, 768],
        ]
    },
    {
        name: 'dashboard',
        path: '/admin/',
        user: 'admin',
        sizes: [
            [1024, 768],
        ]
    },
    {
        name: 'password-reset',
        path: '/admin/password_reset/',
        user: null,
        sizes: [
            [1024, 768],
        ]
    },
];

let BASE_URL = 'http://localhost:8000';

let webshot = require('webshot');


for (let {name, path, user, sizes} of tests) {
    for (let [width, height] of sizes) {
        webshot(BASE_URL + path, `screenshots/${name}-${width}x${height}.png`, {
            screenSize: {width, height},
            shotSize: {width, height}
        }, function() {});
    }
}
