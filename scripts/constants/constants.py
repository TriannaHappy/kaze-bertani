import os
from dotenv import load_dotenv
load_dotenv()

OPENWEATHERMAP_API_KEY=os.getenv('OPENWEATHERMAP_API_KEY')
GOOGLE_WEATHER_API_KEY=os.getenv('GOOGLE_WEATHER_API_KEY')
basepath=os.getenv('BASEPATH')