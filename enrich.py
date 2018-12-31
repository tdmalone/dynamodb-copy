"""
Custom data enrichments for the copied rows.

@author Tim Malone <tim@timmalone.id.au>
"""

def enrich(item):

  new_attributes = {}

  new_attributes['distance_from_home'] = 0
  new_attributes['distance_from_work'] = 0

  new_attributes['time_from_home_driving'] = 0
  new_attributes['time_from_work_driving'] = 0

  new_attributes['time_from_home_public_transport'] = 0
  new_attributes['time_from_work_public_transport'] = 0

  for key, value in new_attributes.items():
    item[key] = {'N': str(value)}

  item['public_transport_disruption'] = {'S': 'n/a'}

  return item
