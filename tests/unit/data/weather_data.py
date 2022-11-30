example_weather_1 = [
    {
            'time': '9:00',
            'weather_desc': 'Cloudy',
            'feels': '8'
    },
    {
            'time': '13:00',
            'weather_desc': 'Sunny',
            'feels': '12'
    },
    {
            'time': '17:00',
            'weather_desc': 'Sunny',
            'feels': '10'
    }
]

expected_weather_string = '''9:00☁️ 8C
13:00☀️ 12C
17:00☀️ 10C
'''
