# this file is a math utilities file. any functions strictly
# math related are here so simHandler doesn't get plugged up
# with too much crap
import math

# Constants:

METER_LAT_DEG = 111,200
METER_LAT_MINUTES = 1853

def degreeToRadian(degree, minute = 0): # optional minute arg
    return math.pi/180 * (degree + minute / 60)


def radianToDegree(radian):
    return radian * 180 / math.pi


def deg2meters(sim, object_origin, object_dest):
    # given an object, calculates the degrees to meters conversion 
    # between the rover and an object. returns meters
    olat_deg, olat_min, olon_deg, olon_min = object_dest.get_coords()
    rlat_deg, rlat_min, rlon_deg, rlon_min = object_origin.get_coords()
    # gets change in degrees from obejct_origin to object_dest
    dlat_deg = olat_deg-rlat_deg
    dlat_min = olat_min - rlat_min
    dlon_deg = olon_deg - rlon_deg
    dlon_min = olon_min - rlon_min
    lat_meters = dlat_deg*METER_LAT_DEG + dlat_min*METER_LAT_MINUTES
    lon_deg_length = 111412.84*math.cos(2*olat_deg)-93.5*math.cos(3*olat_deg) + 0.118*math.cos(5*olat_deg)
    # used wikipedia for the longitude deg size in meters
    # olat_deg was use as opposed to rlat_deg arbitrarily, since it has no significant bearing
    # on calculations, but hypothetically either could be used
    # https://en.wikipedia.org/wiki/Geographic_coordinate_system#Length_of_a_degree
    lon_meters = lon_deg_length*dlon_deg + (lon_deg_length*dlon_min / 60)
    # returns a scalar in meters
    return math.hypot(lat_meters, lon_meters)


def meters2deg(sim, distance, angle):
    # angle should be relative to the 0th degree of the coord system, NOT the rover or another object
    # returns the delta of degrees and minutes from meters
    # first need to get length of longitudinal degree, using the rover's coords as a reference
    lat_deg, lat_min, lon_deg, lon_min = sim.rover.get_coords()
    lon_deg_length = 111412.84*math.cos(2*lat_deg)-93.5*math.cos(3*lat_deg) + 0.118*math.cos(5*lat_deg)
    meters_lon = distance * math.sin(angle) # component of meters in the up and down m80
    meters_lat = distance * math.cos(angle) # component of meters in the left and right boyo
    
    lon_deg =  (meters_lon // lon_deg_length)
    lon_min = (meters_lon % lon_deg_length) / lon_deg_length
    lat_deg = (meters_lat // METER_LAT_DEG)
    lat_min = (meters_lat % METER_LAT_DEG) / METER_LAT_MINUTES

    return lat_deg, lat_min, lon_deg, lon_min




