from django.shortcuts import render
import requests
import datetime



API_KEY_FILE_PATH = "C:\\users\\user\\Test\\weather_project\\weather_app\\API_KEY"
CURRENT_WEATHER_URL = "https://api.openweathermap.org/data/2.5/weather?q={}&appid={}"
FORECAST_URL = "https://api.openweathermap.org/data/2.5/onecall?lat={}&lon={}&exclude=current,minutely,hourly,alerts&appid={}"

def read_api_key(api_key_file_path):

    try:
        with open(api_key_file_path, "r") as file:
            return file.read().strip()
    except FileNotFoundError:
        raise FileNotFoundError(f"API key file not found at {api_key_file_path}")

def get_weather_data_and_forecast(city, api_key, current_weather_url, forecast_url):

    try:
        # Fetch current weather data
        response = requests.get(current_weather_url.format(city, api_key)).json()
        lat, lon = response['coord']['lat'], response['coord']['lon']

        # Fetch forecast data
        forecast_response = requests.get(forecast_url.format(lat, lon, api_key)).json()

        # Extract relevant information
        weather_data = {
            "city": city,
            "temperature": round(response['main']['temp'] - 273.15, 2),
            "description": response['weather'][0]['description'],
            "icon": response['weather'][0]['icon']
        }

        daily_forecasts = [
            {
                "day": datetime.datetime.fromtimestamp(daily_data['dt']).strftime("%A"),
                "min_temp": round(daily_data['temp']['min'] - 273.15, 2),
                "max_temp": round(daily_data['temp']['max'] - 273.15, 2),
                "description": daily_data['weather'][0]['description'],
                "icon": daily_data['weather'][0]['icon']
            }
            for daily_data in forecast_response.get('daily',[])[:5]
        ]

        return weather_data, daily_forecasts

    except requests.RequestException as e:
        # Handle API request errors
        raise RuntimeError(f"Error fetching data from OpenWeatherMap API: {e}")

def index(request):
    try:
        API_KEY = read_api_key(API_KEY_FILE_PATH)

        if request.method == "POST":
            city1 = request.POST.get('city1', '')
            city2 = request.POST.get('city2', '')

            weather_data1, daily_forecasts1 = get_weather_data_and_forecast(city1, API_KEY, CURRENT_WEATHER_URL, FORECAST_URL)
            weather_data2, daily_forecasts2 = get_weather_data_and_forecast(city2, API_KEY, CURRENT_WEATHER_URL, FORECAST_URL) if city2 else (None, None)

            context = {
                "weather_data1": weather_data1,
                "daily_forecasts1": daily_forecasts1,
                "weather_data2": weather_data2,
                "daily_forecasts2": daily_forecasts2
            }

            return render(request, "weather_app/index.html", context)
        else:
            return render(request, "weather_app/index.html")

    except Exception as e:
        # Handle other unexpected errors
        context = {"error_message": str(e)}
        return render(request, "weather_app/error.html", context)