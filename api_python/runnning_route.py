#Origin: starting point, where the user is at the beggining. 
# Distance to run
#Finishing point: a point verifying:  origin+distance=finishing point

from geopy import Point
import googlemaps
import random 
import geopy.distance

DISTANCE = 5  # Target distance in km
TOLERANCE = 0.5  # Tolerance for walking route (to account for longer paths)

gmaps = googlemaps.Client(key='AIzaSyAdDt0McS7gFqTAdHL1RxP4b2Sx7su1QrA')


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
                    mode="walking", avoid="highways")

    for i,element in enumerate(matrix_returned['rows'][0]['elements']):
        if element['status']=='OK':
            distance_km=element['distance']['value']/1000
            if distance - tolerance<=distance_km<=distance+tolerance:
                filtered_destinations.append(destinations[i])
        
    return filtered_destinations


def main():
    #get directions
    origin='28 Bd Gaspard Monge, 91120 Palaiseau'
    destination='7 Av. Carnot, 91300 Massy'

    #geocode the origin
    geocode_origin= gmaps.geocode(origin)
    latitude_origin = geocode_origin[0]['geometry']['location']['lat']
    longitude_origin = geocode_origin[0]['geometry']['location']['lng']

    print(f"latitude: {latitude_origin}, longitude: {longitude_origin}")

    # prepare the origin point for geopy
    origin_point=Point(latitude_origin,longitude_origin)
    origin_tuple=(latitude_origin,longitude_origin)

    #find random destinations
    destinations= adapt_form_of_destinations(find_destinations(origin_point,DISTANCE,[],20))

    #find filtered destinations
    filtered_destinations=filter_destinations_by_distance(origin_tuple,destinations, DISTANCE, TOLERANCE)


    print("filtered destinations found",filtered_destinations)


    final_matrix_return=gmaps.distance_matrix( origin_tuple, filtered_destinations,
                        mode="walking", avoid="highways")

    print("Final matrix return", final_matrix_return)

if __name__=="__main__":
    main()