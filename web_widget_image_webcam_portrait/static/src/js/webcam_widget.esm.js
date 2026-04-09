/*
    Copyright 2016 Siddharth Bhalgami <siddharth.bhalgami@gmail.com>
    License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
*/

import {ImageField, imageField} from "@web/views/fields/image/image_field";

ImageField.defaultProps = {
    ...ImageField.defaultProps,
    webcamWidth: 315,
    webcamHeight: 417,
};
const imageExtractProps = imageField.extractProps;
imageField.extractProps = (fieldInfo) => {
    return Object.assign(imageExtractProps(fieldInfo), {
        webcamWidth:
            fieldInfo.options.webcam_size && Boolean(fieldInfo.options.webcam_size[0])
                ? Number(fieldInfo.options.webcam_size[0])
                : 315,
        webcamHeight:
            fieldInfo.options.webcam_size && Boolean(fieldInfo.options.webcam_size[1])
                ? Number(fieldInfo.options.webcam_size[1])
                : 417,
    });
};
