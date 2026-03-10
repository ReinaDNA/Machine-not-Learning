from flask import Flask, render_template, request, jsonify
import requests
import os
from dotenv import load_dotenv
from datetime import datetime, timezone, timedelta
import math
from openai import OpenAI
from flask_cors import CORS
load_dotenv()

app = Flask(__name__)
API_KEY = os.getenv("OPENWEATHER_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=OPENAI_API_KEY)
CORS(app)
conversation = [
    {
    "role": "system", 
    "content": "You are an AI assistant that helps farmer to provide agricultural advices."
    }
]

@app.route("/")
def home():
    city="Kuala Lumpur"
    
    url=f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"

    response = requests.get(url)
    data = response.json()
    
    temperature = round(data["main"]["temp"],1)
    feel = data["main"]["feels_like"]
    humidity= data["main"]["humidity"]
    pressure= data["main"]["pressure"]
    weather = data["weather"][0]["description"]
    visibility = data["visibility"]
    wind = data["wind"]["speed"]

    a = 17.27
    b = 237.7

    alpha = ((a * temperature) / (b + temperature)) + math.log(humidity / 100)
    dew_point = round((b * alpha) / (a - alpha),1)

    timestamp = data["dt"]
    offset = data["timezone"]
    local_time = datetime.fromtimestamp(timestamp, timezone.utc) + timedelta(seconds=offset)
    time_str = local_time.strftime("%H:%M")
    return render_template(
        "main_page.html",
        city=city,
        temperature=temperature,
        feel=feel,
        visibility=visibility,
        weather=weather,
        wind=wind,
        humidity=humidity,
        pressure=pressure,
        time=time_str,
        dew_point=dew_point
    )

@app.route("/chatbot", methods=["GET", "POST"])
def chatbot():
    question = request.args.get("question")
    answer = None
    
    if question:
        answer = get_chatbot_response(question)

    return render_template("InteractGreg.html", question=question, answer=answer)

def get_chatbot_response(question):
    conversation.append(
        {"role" : "user", 
         "content": question
        }
    )
    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=conversation
    )
    answer = response.choices[0].message.content
    conversation.append(
        {"role" : "assistant", 
         "content": answer
        }
    )

    return answer

@app.route("/chatbot-conversations", methods = ["POST"])
def ask_ai():

    data = request.get_json()
    question = data["question"]

    answer = get_chatbot_response(question)

    return jsonify({"reply": answer})
    

if __name__ == "__main__":
    app.run(debug=True)
