# app.py
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from geopy import Point
import googlemaps
import random
import geopy.distance
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()
API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")
gmaps = googlemaps.Client(key=API_KEY)

app = FastAPI()

class DestinationRequest(BaseModel):
    origin: str
    distance: float
    tolerance: float
    nbr_trails: int

@app.get("/", response_class=HTMLResponse)
async def read_root():
    with open("index.html") as f:
        html_content = f.read().replace("Your_GOOGLE_MAPS_API_KEY", API_KEY)
        return HTMLResponse(content=html_content)

@app.post("/get_destinations")
async def get_destinations(request: DestinationRequest):
    origin = request.origin
    distance = request.distance
    tolerance = request.tolerance
    nbr_trails = request.nbr_trails

    # Geocode the origin
    geocode_origin = gmaps.geocode(origin)
    latitude_origin = geocode_origin[0]['geometry']['location']['lat']
    longitude_origin = geocode_origin[0]['geometry']['location']['lng']

    # Prepare the origin point
    origin_point = Point(latitude_origin, longitude_origin)
    origin_tuple = (latitude_origin, longitude_origin)

    # Find random destinations
    destinations = adapt_form_of_destinations(find_destinations(origin_point, distance, [], 20))
    filtered_destinations = filter_destinations_by_distance(origin_tuple, destinations, distance, tolerance)

    # Get distance matrix
    final_matrix_return = gmaps.distance_matrix(origin_tuple, filtered_destinations, mode="walking", avoid="highways")

    # Create a list of dictionaries to store the destinations and distances
    dest_distance = [
        {
            'destination': final_matrix_return['destination_addresses'][i],
            'distance': final_matrix_return['rows'][0]['elements'][i]['distance']['text'],
            'duration': final_matrix_return['rows'][0]['elements'][i]['duration']['text']
        }
        for i in range(min(nbr_trails, len(filtered_destinations))) 
    ] # we used min here just in case the filtered destinations are less than the desired number of trails :)

    return dest_distance

# Including helper functions
def find_destinations(origin_point, distance, destinations_found, nbr_dest):
    # Define a general distance object with a slightly reduced target distance
    d = geopy.distance.distance(kilometers=distance * 0.9)

    # Pick randomly destinations in a radius of 5000 from the origin
    for i in range(nbr_dest):
        # Bearing (float) – Bearing in degrees: 0 – North, 90 – East, 180 – South, 270 or -90 – West.
        bearing = random.uniform(0, 360)
        new_dest = d.destination(point=origin_point, bearing=bearing)
        destinations_found.append(new_dest)

    return destinations_found  # they are of type points of geopy

# Transform the geopy destinations to a list of (latitude, longitude) tuples 
def adapt_form_of_destinations(dests):
    return [(element.latitude, element.longitude) for element in dests]

# Function using the distance_matrix to remove destinations that are not respecting the chosen distance 
def filter_destinations_by_distance(origin_tuple, destinations, distance, tolerance):
    filtered_destinations = []
    matrix_returned = gmaps.distance_matrix(origin_tuple, destinations,
                    mode="walking", avoid="highways")

    for i, element in enumerate(matrix_returned['rows'][0]['elements']):
        if element['status'] == 'OK':
            distance_km = element['distance']['value'] / 1000
            if distance - tolerance <= distance_km <= distance + tolerance:
                filtered_destinations.append(destinations[i])
        
    return filtered_destinations