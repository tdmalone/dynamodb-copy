"""
Custom data enrichments for the copied rows.

This is (currently) heavily customised to my use-case - so it might not be of direct use to you, at
least without editing it. It's currently used to enrich geolocation events submitted by my phone,
to determine how far I am from home and work either by car or public transport.

Note that when accessing existing attributes here, you should ideally check for their existence
first, in case unexpected things happen with the data you're copying from.

@author Tim Malone <tim@timmalone.id.au>
"""

from os import getenv
from geopy.distance import geodesic
from googlemaps import Client as client

HOME_LATLNG = getenv('HOME_LATLNG')
WORK_LATLNG = getenv('WORK_LATLNG')
GOOGLE_API_KEY = getenv('GOOGLE_API_KEY')

googlemaps = client(key=GOOGLE_API_KEY)

def enrich(item):

  # Simplify this known attribute by rounding it.
  if 'event_accuracy_m' in item:
    item['event_accuracy_m']['S'] = str(round(float(item['event_accuracy_m']['S'])))

  # The rest of this function depends on latitude and longitude - return early if we don't have it.
  if 'event_latitude' not in item or 'event_longitude' not in item:
    return item

  # Each new attribute added to this dict will be submitted to DynamoDB as a number (N) type.
  new_number_attrs = {}

  # Prepare location co-ordinates.
  home_coords = HOME_LATLNG
  work_coords = WORK_LATLNG
  current_coords = item['event_latitude']['S'] + ',' + item['event_longitude']['S']
  home_coords_list = home_coords.split(',')
  work_coords_list = work_coords.split(',')
  current_coords_list = current_coords.split(',')

  # Determine the proximity to both work and home.
  new_number_attrs['distance_from_home'] = round(geodesic(home_coords_list, current_coords_list).m)
  new_number_attrs['distance_from_work'] = round(geodesic(work_coords_list, current_coords_list).m)

  # Determine the distance to work and home both for driving & on public transport.
  # @see https://developers.google.com/maps/documentation/distance-matrix/intro
  # @see https://github.com/googlemaps/google-maps-services-python

  args = {
    'origins': current_coords,
    'departure_time': 'now',
    'transit_mode': 'train' # Only applies when we set 'mode' to 'transit'
  }

  args = {**args, 'destinations': home_coords, 'mode': 'driving'}
  to_home_driving = googlemaps.distance_matrix(**args)['rows'][0]['elements'][0]

  args = {**args, 'destinations': work_coords, 'mode': 'driving'}
  to_work_driving = googlemaps.distance_matrix(**args)['rows'][0]['elements'][0]

  args = {**args, 'destinations': home_coords, 'mode': 'transit'}
  to_home_transit = googlemaps.distance_matrix(**args)['rows'][0]['elements'][0]

  args = {**args, 'destinations': work_coords, 'mode': 'transit'}
  to_work_transit = googlemaps.distance_matrix(**args)['rows'][0]['elements'][0]

  new_number_attrs['time_from_home_driving'] = to_home_driving['duration_in_traffic']['value']
  new_number_attrs['time_from_work_driving'] = to_work_driving['duration_in_traffic']['value']
  new_number_attrs['time_from_home_public_transport'] = to_home_transit['duration']['value']
  new_number_attrs['time_from_work_public_transport'] = to_work_transit['duration']['value']

  # Add new attributes as DynamoDB number (N) types.
  for key, value in new_number_attrs.items():
    item[key] = {'N': str(value)}

  return item

# Uncomment for testing only.
#print(enrich({'event_latitude':{'S':'-37.824554'},'event_longitude':{'S':'145.090092'}}))
