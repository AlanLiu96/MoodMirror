import os
import uuid
from pprint import pprint

import requests
from PIL import Image, ExifTags


def crop(srcfile, destfile):
    url = {
        "url": "https://storage.googleapis.com/fashion-bucket/test?u=" + str(uuid.uuid4())
    }
    headers = {
        'Ocp-Apim-Subscription-Key': 'be37019dfbdb413cba3d67b0ed8f3cf8'
    }

    r = requests.post('https://api.projectoxford.ai/face/v1.0/detect?returnFaceId=false&returnFaceLandmarks=true',
                      json=url,
                      headers=headers)

    maxArea = 0
    bestTop = 0

    pprint(r.json())

    for face in r.json():
        rect = face[u'faceRectangle']
        left = rect[u'left']
        top = rect[u'top']
        width = rect[u'width']
        height = rect[u'height']
        underLipBottom = face[u'faceLandmarks'][u'noseTip'][u'y']

        faceBottom = underLipBottom + height * 0.1

        area = width * height

        if area > maxArea:
            pprint(face)

            maxArea = area
            bestTop = min(faceBottom, top + height)

    # Cropper

    im = Image.open(srcfile)

    # Rotate image correctly
    if im._getexif():
        exif = dict((ExifTags.TAGS[k], v) for k, v in im._getexif().items() if k in ExifTags.TAGS)
        if 'Orientation' in exif:
            if exif['Orientation'] == 3:
                im = im.rotate(180, expand=True)
            elif exif['Orientation'] == 6:
                im = im.rotate(270, expand=True)
            elif exif['Orientation'] == 8:
                im = im.rotate(90, expand=True)

    # Do the crop
    (imWidth, imHeight) = im.size
    im = im.crop((0, bestTop, imWidth, imHeight))

    im.save(destfile)


# curPath = os.path.dirname(os.path.realpath(__file__))
# srcfile = os.path.join(curPath, 'harrison.jpg')
# destfile = os.path.join(curPath, 'harrison_cropped.jpg')
# crop(srcfile, destfile)
