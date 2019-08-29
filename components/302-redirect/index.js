'use strict';

const path = require('path')

function redirect301(url) {
    return {
        status: '301',
        statusDescription: 'Moved Permanently',
        headers: {
            location: [{
                key: 'Location',
                value: url,
            }],
        },
    };
}

exports.handler = (event, context, callback) => {
    const {
        request
    } = event.Records[0].cf
    const url = request.uri;

    if (url.endsWith('/')) {
        return callback(null, request);
    }

    if (url.endsWith('/index.html')) {
        return callback(null, redirect301(url.replace('/index.html', '/')));
    }

    if (path.extname(url).length > 0) {
        return callback(null, request);
    }

    return callback(null, redirect301(url + '/'));
};