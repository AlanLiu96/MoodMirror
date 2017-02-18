import json
import random
import requests


def get_temperature():
    weather_url = 'https://api.forecast.io/forecast/cbf631a66c199dbfbe6e0a9bb547343a/41.3083,-72.9279'
    resp = requests.get(weather_url)
    if resp.status_code != 200:
        return None
    resp_json = json.loads(resp.text)
    return resp_json['currently']['apparentTemperature']

def determine_clothing_type():
    pass


def is_contained_in_elem_in_list(item, lst):
    return any([(item in e) for e in lst])

def get_comments(data):
    plural_known_clothing = ['pants', 'shorts', 'outerwear', 'pattern', 'fur']
    single_known_clothing = ['shirt', 'jacket', 'sweater', 't shirt']
    comments = []

    outerwear = False
    for label in data['labels']:
        # Glasses
        if label['name'] == 'glasses':
            comments.append('Your glasses look great!')

        # Fashion
        if label['name'] == 'fashion':
            comments.append('Your style is looking mighty fly.')

        if label['name'] == 'outerwear' or label['name'] == 'jacket' or label['name'] == 'fur':
            outerwear = True

    # Label clothing
    clothing_labels = []
    for label in data['labels']:
        if is_contained_in_elem_in_list(label['name'], plural_known_clothing + single_known_clothing):
            print("adding...{}".format(label['name']))
            clothing_labels.append(label)
    if len(clothing_labels) > 0:
        max_label = max(clothing_labels, key=lambda x: x['score'])
        comment = "I see that you're wearing "
        if is_contained_in_elem_in_list(max_label['name'], single_known_clothing):
            comment+="a "
        comment+=max_label['name']
        if max_label['name'] == 'pattern':
            comment += 'ed clothing'
        comment += "."
        comments.append(comment)
    else:
        comments.append("I see that you're wearing " + data['colors'][0]['name'] + ".")

    # Color rec
    comment = data['compColor'] + ' pants would go well with your outfit.'
    comments.append(comment)

    # Weather
    temp = get_temperature()
    if temp < 65:
        if outerwear:
            comments.append('You are well dressed for the weather.')
        else:
            comments.append('It is %d degrees outside.' % int(temp))
            comments.append('You might want to wear something warmer.')
    elif temp > 65:
        if outerwear:
            comments.append('It is warm today, perhaps wear a bit less?')
        else:
            comments.append('You are dressed well for the weather.')

    return comments

