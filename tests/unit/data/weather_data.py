example_weather_1 = [
    {
            'time': '9:00',
            'weather_desc': 'broken clouds',
            'feels': '8°C'
    },
    {
            'time': '13:00',
            'weather_desc': 'clear sky',
            'feels': '17°C'
    },
    {
            'time': '17:00',
            'weather_desc': 'clear sky',
            'feels': '10°C'
    }
]

expected_weather_string = '''9:00☁️ 8°C
13:00☀️ 17°C
17:00☀️ 10°C
'''
