#Origin: starting point, where the user is at the beggining. 
# Distance to run
#Finishing point: a point verifying:  origin+distance=finishing point

from geopy import Point
import googlemaps
import random 
import geopy.distance
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Get the Google Maps API key from the environment
API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")


DISTANCE = 5  # Target distance in km
TOLERANCE = 0.6  # Tolerance for walking route (to account for longer paths)
NBR_TRAILS=5

gmaps = googlemaps.Client(key=API_KEY)


# Function to find random destinations within a given distance from the origin
def find_destinations(origin_point,distance,destinations_found, nbr_dest):
    
    # Define a general distance object with a slightly reduced target distance
    d = geopy.distance.distance(kilometers=distance*0.9)

    #pick randomly 4 destinations in a radius of 5000 from the origin
    for i in range(nbr_dest):

        #bearing (float) – Bearing in degrees: 0 – North, 90 – East, 180 – South, 270 or -90 – West.
        bearing = random.uniform(0, 360)
        new_dest = d.destination(point=origin_point, bearing=bearing)
        destinations_found.append(new_dest)

    return destinations_found # they are of type points of geopy


# transform the geopy destinations to a list of (latitude, longitude) tuples 
def adapt_form_of_destinations(dests):
    return [(element.latitude,element.longitude)for element in dests]


#function using the distance_matrix to remove destinations that are not respecting the chosen distance 
def filter_destinations_by_distance(origin_tuple,destinations, distance, tolerance):
    filtered_destinations= []
    matrix_returned = gmaps.distance_matrix( origin_tuple, destinations,
                    mode="walking", avoid="highways", )

    for i,element in enumerate(matrix_returned['rows'][0]['elements']):
        if element['status']=='OK':
            distance_km=element['distance']['value']/1000
            if distance - tolerance<=distance_km<=distance+tolerance:
                filtered_destinations.append(destinations[i])
        
    return filtered_destinations


def main():
    #get directions
    origin='Châtillon - Montrouge, 92320 Châtillon'

    #geocode the origin
    geocode_origin= gmaps.geocode(origin)
    latitude_origin = geocode_origin[0]['geometry']['location']['lat']
    longitude_origin = geocode_origin[0]['geometry']['location']['lng']

    print(f" The origin adress: {origin},\n The corresponding coordinates: ({latitude_origin}, {longitude_origin})")

    # prepare the origin point for geopy
    origin_point=Point(latitude_origin,longitude_origin)
    origin_tuple=(latitude_origin,longitude_origin)

    #find random destinations
    destinations= adapt_form_of_destinations(find_destinations(origin_point,DISTANCE,[],20))

    #find filtered destinations
    filtered_destinations=filter_destinations_by_distance(origin_tuple,destinations, DISTANCE, TOLERANCE)


    #Used to debug, in order to see the returned destinations
    #print("filtered destinations found",filtered_destinations)


    final_matrix_return=gmaps.distance_matrix( origin_tuple, filtered_destinations,
                        mode="walking", avoid="highways")
    
    
    # Create a list of dictionaries to store the desired number of trails
    dest_distance = [
        {
            'destination': final_matrix_return['destination_addresses'][i],
            'distance': final_matrix_return['rows'][0]['elements'][i]['distance']['text']
        }
        for i in range(min(NBR_TRAILS, len(filtered_destinations)))
    ]

    print("Final destinations and their distances:")
    for item in dest_distance:
        print(f"Destination: {item['destination']}, Distance: {item['distance']}")

if __name__=="__main__":
    main()