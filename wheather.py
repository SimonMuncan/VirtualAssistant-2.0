import requests, geocoder, random

class Weather():
    # Get user's location based on IP address
    def checkLocation():
        g = geocoder.ip('me')
        lat = g.lat
        lon = g.lng
        return lat, lon 
        
    #Method to get current weather information
    def checkCurrentWeather():
        # API endpoint for current weather
        url = "https://weatherapi-com.p.rapidapi.com/current.json"
        # Get user's location 
        lat, lon = Weather.checkLocation()
        # Query parameters
        string = str(lat) + "," + str(lon)
        querystring = {"q":string}

        # Headers for API request
        headers = {
	        "x-rapidapi-key": "613fa57601msh56fa4a7e7a50b5cp1d7c22jsn333fa9d8aa13",
	        "x-rapidapi-host": "weatherapi-com.p.rapidapi.com"
        }
        # Send request to the API
        response = requests.get(url, headers=headers, params=querystring).json()
        # Extract and return the current weather summary
        return response
    
    def forecast3days():
        url = "https://weatherapi-com.p.rapidapi.com/forecast.json"
         # Get user's location 
        lat, lon = Weather.checkLocation()
        # Query parameters
        string = str(lat) + "," + str(lon)
        querystring = {"q":string,"days":"3"}

        headers = {
	        "x-rapidapi-key": "613fa57601msh56fa4a7e7a50b5cp1d7c22jsn333fa9d8aa13",
	        "x-rapidapi-host": "weatherapi-com.p.rapidapi.com"
        }

        response = requests.get(url, headers=headers, params=querystring).json()

        return response
    
    #get weather alerts
    def weatherAlerts():
        url = "https://ai-weather-by-meteosource.p.rapidapi.com/alerts"

        lat, lon = Weather.checkLocation()

        querystring = {"lat":lat,"lon":lon,"timezone":"auto","language":"en"}
        
        headers = {
	        "x-rapidapi-key": "613fa57601msh56fa4a7e7a50b5cp1d7c22jsn333fa9d8aa13",
	        "x-rapidapi-host": "ai-weather-by-meteosource.p.rapidapi.com"   
        }

        response = requests.get(url, headers=headers, params=querystring).json()
        return response 

    #air quality
    def weatherAirQuality():
        url = "https://air-quality.p.rapidapi.com/current/airquality"

        lat, lon = Weather.checkLocation()

        querystring = {"lon":lon,"lat":lat}

        headers = {
	        "x-rapidapi-key": "613fa57601msh56fa4a7e7a50b5cp1d7c22jsn333fa9d8aa13",
	        "x-rapidapi-host": "air-quality.p.rapidapi.com"
        }

        response = requests.get(url, headers=headers, params=querystring).json()
        print(response['data'][0]['aqi'])
        return response['data'][0]['aqi']
    
    def airQuality():
        return 142
    
    def airQualityString():
        aqi = Weather.airQuality()
        if aqi <= 50:
            string = "Good"
        elif aqi >50 and aqi <= 100:
            string = "Moderate"
        elif aqi >100 and aqi <= 150:
            string = "Unhealthy for \nsensitive groups"
        elif aqi >150 and aqi <= 200:
            string = "Unhealthy"
        elif aqi >200 and aqi <= 250:
            string = "Very unhealthy" 
        elif aqi >250 and aqi <= 300:
            string = "Hazardous" 
        return string
    
    def airQualityHeightWidth():
        aqi = Weather.airQuality()
        if aqi <= 50:
            height = 28
            width = 405
        elif aqi >50 and aqi <= 100:
            height = 66
            width = 380
        elif aqi >100 and aqi <= 150:
            height = 110
            width = 330
        elif aqi >150 and aqi <= 200:
            height = 152
            width = 378
        elif aqi >200 and aqi <= 250:
            height = 187
            width = 335
        elif aqi >250 and aqi <= 300:
            height = 231 
            width=372
        return height, width