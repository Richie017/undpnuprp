__author__ = 'root'

import urllib

import anyjson


class GEOFinder(object):
    def __init__(self):
        self.googleGeocodeUrl = 'http://maps.googleapis.com/maps/api/geocode/json?'

    def get_coordinates(self,query, from_sensor=False):
        query = query.encode('utf-8')
        params = {
            'address': query,
            'sensor': "true" if from_sensor else "false"
        }
        url = self.googleGeocodeUrl + urllib.parse.urlencode(params)
        json_response = urllib.request.urlopen(url)
        response = anyjson.deserialize(json_response.read().decode("utf-8"))
        if response['results']:
            location = response['results'][0]['geometry']['location']
            latitude, longitude = location['lat'], location['lng']
        else:
            latitude, longitude = None, None
        return latitude, longitude
