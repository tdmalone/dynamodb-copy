"""
Custom data enrichments for the copied rows.

@author Tim Malone <tim@timmalone.id.au>
"""

from os import getenv
from geopy import distance

HOME_LATLNG = getenv('HOME_LATLNG')
WORK_LATLNG = getenv('WORK_LATLNG')

def enrich(item):

  new_attributes = {}

  # Determine the current proximity to both work and home.
  home_coords = HOME_LATLNG.split(',')
  work_coords = WORK_LATLNG.split(',')
  current_coords = (item['event_latitude']['S'], item['event_longitude']['S'])
  new_attributes['distance_from_home'] = distance.geodesic(home_coords, current_coords).m
  new_attributes['distance_from_work'] = distance.geodesic(work_coords, current_coords).m

  new_attributes['time_from_home_driving'] = 0
  new_attributes['time_from_work_driving'] = 0

  new_attributes['time_from_home_public_transport'] = 0
  new_attributes['time_from_work_public_transport'] = 0

  for key, value in new_attributes.items():
    item[key] = {'N': str(value)}

  item['public_transport_disruption'] = {'S': 'n/a'}

  return item
