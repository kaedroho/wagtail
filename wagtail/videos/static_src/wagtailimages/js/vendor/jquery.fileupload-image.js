/*
 * jQuery File Upload Video Preview & Resize Plugin 1.7.2
 * https://github.com/blueimp/jQuery-File-Upload
 *
 * Copyright 2013, Sebastian Tschan
 * https://blueimp.net
 *
 * Licensed under the MIT license:
 * http://www.opensource.org/licenses/MIT
 */

/* jshint nomen:false */
/* global define, window, Blob */

(function (factory) {
    'use strict';
    if (typeof define === 'function' && define.amd) {
        // Register as an anonymous AMD module:
        define([
            'jquery',
            'load-video',
            'load-video-meta',
            'load-video-exif',
            'load-video-ios',
            'canvas-to-blob',
            './jquery.fileupload-process'
        ], factory);
    } else {
        // Browser globals:
        factory(
            window.jQuery,
            window.loadVideo
        );
    }
}(function ($, loadVideo) {
    'use strict';

    // Prepend to the default processQueue:
    $.blueimp.fileupload.prototype.options.processQueue.unshift(
        {
            action: 'loadVideoMetaData',
            disableVideoHead: '@',
            disableExif: '@',
            disableExifThumbnail: '@',
            disableExifSub: '@',
            disableExifGps: '@',
            disabled: '@disableVideoMetaDataLoad'
        },
        {
            action: 'loadVideo',
            // Use the action as prefix for the "@" options:
            prefix: true,
            fileTypes: '@',
            maxFileSize: '@',
            noRevoke: '@',
            disabled: '@disableVideoLoad'
        },
        {
            action: 'resizeVideo',
            // Use "video" as prefix for the "@" options:
            prefix: 'video',
            maxWidth: '@',
            maxHeight: '@',
            minWidth: '@',
            minHeight: '@',
            crop: '@',
            orientation: '@',
            forceResize: '@',
            disabled: '@disableVideoResize'
        },
        {
            action: 'saveVideo',
            quality: '@videoQuality',
            type: '@videoType',
            disabled: '@disableVideoResize'
        },
        {
            action: 'saveVideoMetaData',
            disabled: '@disableVideoMetaDataSave'
        },
        {
            action: 'resizeVideo',
            // Use "preview" as prefix for the "@" options:
            prefix: 'preview',
            maxWidth: '@',
            maxHeight: '@',
            minWidth: '@',
            minHeight: '@',
            crop: '@',
            orientation: '@',
            thumbnail: '@',
            canvas: '@',
            disabled: '@disableVideoPreview'
        },
        {
            action: 'setVideo',
            name: '@videoPreviewName',
            disabled: '@disableVideoPreview'
        },
        {
            action: 'deleteVideoReferences',
            disabled: '@disableVideoReferencesDeletion'
        }
    );

    // The File Upload Resize plugin extends the fileupload widget
    // with video resize functionality:
    $.widget('blueimp.fileupload', $.blueimp.fileupload, {

        options: {
            // The regular expression for the types of videos to load:
            // matched against the file type:
            loadVideoFileTypes: /^video\/(gif|jpeg|png|svg\+xml)$/,
            // The maximum file size of videos to load:
            loadVideoMaxFileSize: 10000000, // 10MB
            // The maximum width of resized videos:
            videoMaxWidth: 1920,
            // The maximum height of resized videos:
            videoMaxHeight: 1080,
            // Defines the video orientation (1-8) or takes the orientation
            // value from Exif data if set to true:
            videoOrientation: false,
            // Define if resized videos should be cropped or only scaled:
            videoCrop: false,
            // Disable the resize video functionality by default:
            disableVideoResize: true,
            // The maximum width of the preview videos:
            previewMaxWidth: 80,
            // The maximum height of the preview videos:
            previewMaxHeight: 80,
            // Defines the preview orientation (1-8) or takes the orientation
            // value from Exif data if set to true:
            previewOrientation: true,
            // Create the preview using the Exif data thumbnail:
            previewThumbnail: true,
            // Define if preview videos should be cropped or only scaled:
            previewCrop: false,
            // Define if preview videos should be resized as canvas elements:
            previewCanvas: true
        },

        processActions: {

            // Loads the video given via data.files and data.index
            // as img element, if the browser supports the File API.
            // Accepts the options fileTypes (regular expression)
            // and maxFileSize (integer) to limit the files to load:
            loadVideo: function (data, options) {
                if (options.disabled) {
                    return data;
                }
                var that = this,
                    file = data.files[data.index],
                    dfd = $.Deferred();
                if (($.type(options.maxFileSize) === 'number' &&
                            file.size > options.maxFileSize) ||
                        (options.fileTypes &&
                            !options.fileTypes.test(file.type)) ||
                        !loadVideo(
                            file,
                            function (img) {
                                if (img.src) {
                                    data.img = img;
                                }
                                dfd.resolveWith(that, [data]);
                            },
                            options
                        )) {
                    return data;
                }
                return dfd.promise();
            },

            // Resizes the video given as data.canvas or data.img
            // and updates data.canvas or data.img with the resized video.
            // Also stores the resized video as preview property.
            // Accepts the options maxWidth, maxHeight, minWidth,
            // minHeight, canvas and crop:
            resizeVideo: function (data, options) {
                if (options.disabled || !(data.canvas || data.img)) {
                    return data;
                }
                options = $.extend({canvas: true}, options);
                var that = this,
                    dfd = $.Deferred(),
                    img = (options.canvas && data.canvas) || data.img,
                    resolve = function (newImg) {
                        if (newImg && (newImg.width !== img.width ||
                                newImg.height !== img.height ||
                                options.forceResize)) {
                            data[newImg.getContext ? 'canvas' : 'img'] = newImg;
                        }
                        data.preview = newImg;
                        dfd.resolveWith(that, [data]);
                    },
                    thumbnail;
                if (data.exif) {
                    if (options.orientation === true) {
                        options.orientation = data.exif.get('Orientation');
                    }
                    if (options.thumbnail) {
                        thumbnail = data.exif.get('Thumbnail');
                        if (thumbnail) {
                            loadVideo(thumbnail, resolve, options);
                            return dfd.promise();
                        }
                    }
                    // Prevent orienting the same video twice:
                    if (data.orientation) {
                        delete options.orientation;
                    } else {
                        data.orientation = options.orientation;
                    }
                }
                if (img) {
                    resolve(loadVideo.scale(img, options));
                    return dfd.promise();
                }
                return data;
            },

            // Saves the processed video given as data.canvas
            // inplace at data.index of data.files:
            saveVideo: function (data, options) {
                if (!data.canvas || options.disabled) {
                    return data;
                }
                var that = this,
                    file = data.files[data.index],
                    dfd = $.Deferred();
                if (data.canvas.toBlob) {
                    data.canvas.toBlob(
                        function (blob) {
                            if (!blob.name) {
                                if (file.type === blob.type) {
                                    blob.name = file.name;
                                } else if (file.name) {
                                    blob.name = file.name.replace(
                                        /\..+$/,
                                        '.' + blob.type.substr(6)
                                    );
                                }
                            }
                            // Don't restore invalid meta data:
                            if (file.type !== blob.type) {
                                delete data.videoHead;
                            }
                            // Store the created blob at the position
                            // of the original file in the files list:
                            data.files[data.index] = blob;
                            dfd.resolveWith(that, [data]);
                        },
                        options.type || file.type,
                        options.quality
                    );
                } else {
                    return data;
                }
                return dfd.promise();
            },

            loadVideoMetaData: function (data, options) {
                if (options.disabled) {
                    return data;
                }
                var that = this,
                    dfd = $.Deferred();
                loadVideo.parseMetaData(data.files[data.index], function (result) {
                    $.extend(data, result);
                    dfd.resolveWith(that, [data]);
                }, options);
                return dfd.promise();
            },

            saveVideoMetaData: function (data, options) {
                if (!(data.videoHead && data.canvas &&
                        data.canvas.toBlob && !options.disabled)) {
                    return data;
                }
                var file = data.files[data.index],
                    blob = new Blob([
                        data.videoHead,
                        // Resized videos always have a head size of 20 bytes,
                        // including the JPEG marker and a minimal JFIF header:
                        this._blobSlice.call(file, 20)
                    ], {type: file.type});
                blob.name = file.name;
                data.files[data.index] = blob;
                return data;
            },

            // Sets the resized version of the video as a property of the
            // file object, must be called after "saveVideo":
            setVideo: function (data, options) {
                if (data.preview && !options.disabled) {
                    data.files[data.index][options.name || 'preview'] = data.preview;
                }
                return data;
            },

            deleteVideoReferences: function (data, options) {
                if (!options.disabled) {
                    delete data.img;
                    delete data.canvas;
                    delete data.preview;
                    delete data.videoHead;
                }
                return data;
            }

        }

    });

}));
