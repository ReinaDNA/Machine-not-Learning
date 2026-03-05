from flask import Flask, render_template
import requests
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
API_KEY = os.getenv("OPENWEATHER_API_KEY")

@app.route("/")
def home():
    city="Kuala Lumpur"

    url=f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"

    response = requests.get(url)
    data = response.json()

    temperature = data["main"]["temp"]
    weather = data["weather"][0]["description"]

    return render_template(
        "index.html",
        city=city,
        temperature=temperature,
        weather=weather
    )

# @app.route("/forecast")
# def forecast():
#     city="Kuala Lumpur"

#     url=f"https://api.openweathermap.org/data/2.5/forecast?q={city}&appid={API_KEY}&units=metric"

#     response = requests.get(url)
#     data = response.json()


if __name__ == "__main__":
    app.run(debug=True)
