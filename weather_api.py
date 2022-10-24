import requests


def get_wind_direction(degrees):
    if 350 <= degrees <= 10:
        return 'North'
    elif 10 < degrees < 80:
        return 'North-East'
    elif 80 <= degrees <= 100:
        return 'East'
    elif 100 < degrees < 170:
        return 'South-East'
    elif 170 <= degrees <= 190:
        return 'South'
    elif 190 < degrees < 260:
        return 'South-West'
    elif 260 <= degrees <= 280:
        return 'West'
    elif 280 < degrees < 350:
        return 'North-West'


def get_weather_info(c_name):
    """
    get weather information from www.openweathermap.org
    :param c_name: string  - name of the city to get the forecast for
    :return: a list of strings comprising the weather forecast.
    """
    API_KEY = 'f2c8b1dae6135bc74ca9d95ab020d77a'
    BASE_URL = 'http://api.openweathermap.org/data/2.5/weather'

    request_url = f'{BASE_URL}?appid={API_KEY}&q={c_name}'
    response = requests.get(request_url)

    if response.status_code == 200:
        data = response.json()
        print(data)
        a = f'Current weather for {c_name}:'
        b = data['weather'][0]['main']
        c = data['weather'][0]['description']
        d = f"Temperature: {round(data['main']['temp'] - 273.15, 2)} degrees celsius"
        e = f"Feels like: {round(data['main']['feels_like'] - 273.15, 2)} degrees celsius"
        f = f"Pressure: {data['main']['pressure']} kilopascals"
        g = f"Humidity: {data['main']['humidity']} percent"
        h = f"Visibility: {data['visibility']} metres"
        i = f"Wind speed: {data['wind']['speed']} meters per second"
        j = f"Wind direction: {get_wind_direction(data['wind']['deg'])}"

        return [a, b, c, d, e, f, g, h, i, j]
    else:
        return f'weather forecast unsuccessful'
