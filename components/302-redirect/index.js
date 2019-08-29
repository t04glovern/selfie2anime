'use strict';

const path = require('path')

exports.handler = (event, context, callback) => {
    //get request object
    const { request } = event.Records[0].cf

    const url = request.uri;

    //we need to determine if this request has an extension.
    const extension = path.extname(url);

    //path.extname returns an empty string when there's no extension.
    //if there is an extension on this request, continue without doing anything!
    if(extension && extension.length > 0){
        return callback(null, request);
    }
    
    //there is no extension, so that means we want to add a trailing slash to the url.
    //let's check if the last character is a slash.
    const last_character = url.slice(-1);
    
    //if there is already a trailing slash, return.
    if(last_character === "/"){
        return callback(null, request);
    }

    //add a trailing slash.    
    const new_url = `${url}/`;


    //create HTTP redirect...
    const redirect = {
        status: '301',
        statusDescription: 'Moved Permanently',
        headers: {
            location: [{
                key: 'Location',
                value: new_url,
            }],
        },
    };
    
    return callback(null, redirect);
};