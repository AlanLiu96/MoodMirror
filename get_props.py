import os
import sys
from pprint import pprint
from colorName2 import colorName, colorRec

def getProps(fname):
    dname = fname.split('/')[0]
    fname = fname.split('/')[1]

    imgPath = os.path.join(os.path.dirname(os.path.realpath(__file__)), dname)
    fpath = os.path.join(imgPath, fname)
    croppedPath = os.path.join(imgPath, 'cropped.' + fname)
    bwPath = os.path.join(imgPath, 'bw.' + fname)

    # Upload image
    import storage

    def upload(fpath):
        try:
            f = open(fpath, 'r')
        except:
            print('cannot open file')
            sys.exit(0)

        fileStream = f.read()
        storage.upload(fileStream, 'test')
        f.close()

    upload(fpath)

    # Crop image

    import face_ms
    print(croppedPath)
    face_ms.crop(fpath, croppedPath)

    # Upload cropped image

    upload(croppedPath)

    # Pass through vision API
    import vision

    visionRes = vision.vision()
    pprint(visionRes)

    # Upload BW image
    # import bw
    # bw.thresholdImage(croppedPath, bwPath)
    # upload(bwPath)

    # Compile data
    data = {
        'labels': [],
        'colors': [],
    }

    for label in visionRes['labels']:
        data['labels'].append({
            'name': label[u'description'],
            'score': label[u'score']
        })

    totalColorScore = 0
    for color in visionRes['colors']:
        r = color[u'color'][u'red']
        g = color[u'color'][u'green']
        b = color[u'color'][u'blue']
        score = color[u'score'] * color[u'pixelFraction']
        totalColorScore += score

    bestColor = None
    bestScore = 0

    for color in visionRes['colors']:
        r = color[u'color'][u'red']
        g = color[u'color'][u'green']
        b = color[u'color'][u'blue']
        score = color[u'score'] * color[u'pixelFraction'] / totalColorScore

        if score > bestScore:
            bestScore = score
            bestColor = (r, g, b)

        name = colorName(r, g, b)

        data['colors'].append({
            'rgb': (r, g, b),
            'score': score,
            'name': name
        })

    compColor = colorRec(bestColor[0], bestColor[1], bestColor[2])
    data['compColor'] = compColor

    print('---------------------')
    pprint(data)

    return data
