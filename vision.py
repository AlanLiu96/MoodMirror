from googleapiclient import discovery
from oauth2client.client import GoogleCredentials


def vision():
    credentials = GoogleCredentials.get_application_default()
    service = discovery.build('vision', 'v1', credentials=credentials)

    service_request = service.images().annotate(body={
        'requests': [{
            'image': {
                'source': {
                    "gcsImageUri": "gs://fashion-bucket/test"
                }
            },
            'features': [
                {'type': 'LABEL_DETECTION'},
                {'type': 'IMAGE_PROPERTIES'}
            ]
        }]
    })

    response = service_request.execute()['responses'][0]
    print(response)
    labels = response['labelAnnotations'] if "labelAnnotations" in response else {}
    colors = response['imagePropertiesAnnotation']['dominantColors']['colors']

    print(labels)
    print(colors)

    # Make color HTML
    html = '<style>'
    boxes = ''
    for i, color in enumerate(colors):
        red = color['color']['red']
        green = color['color']['green']
        blue = color['color']['blue']

        score = color['score']
        pixelFraction = color['pixelFraction']
        width = score * pixelFraction * 1000 + 10

        html += """
            box%d {
                display: inline-block;
                background: rgb(%d, %d, %d);
                height: 50px;
                width: %dpx;
            }
        """ % (
            i, red, green, blue, width)

        boxes += '<box%d></box%d>' % (i, i)
    html += '</style>' + boxes

    f = open('colors.html', 'w+')
    f.write(html)
    f.close()

    return {
        'labels': labels,
        'colors': colors
    }
