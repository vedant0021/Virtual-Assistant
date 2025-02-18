import datetime
import sqlite3
import requests

# OpenWeather API Key (Replace with your own key)
API_KEY = "f6a417ae1dbd8199ac4a95a65cd8e9e1"
BASE_URL = "https://api.openweathermap.org/data/2.5/weather"

# Database Setup
def initialize_database():
    conn = sqlite3.connect("assistant_history.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS AssistantHistory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task TEXT,
            result TEXT,
            timestamp TEXT
        )
    """)
    conn.commit()
    conn.close()

# Function to Save Data to Database
def save_to_database(task, result):
    initialize_database()  # Ensure table exists before inserting
    conn = sqlite3.connect("assistant_history.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO AssistantHistory (task, result, timestamp) VALUES (?, ?, ?)",
                   (task, result, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    conn.commit()
    conn.close()

# Fetch Weather Information
def get_weather(city):
    params = {"q": city, "appid": API_KEY, "units": "metric"}
    response = requests.get(BASE_URL, params=params)
    if response.status_code == 200:
        data = response.json()
        weather_info = {
            "City": data['name'],
            "Temperature": f"{data['main']['temp']}°C",
            "Humidity": f"{data['main']['humidity']}%",
            "Wind Speed": f"{data['wind']['speed']} m/s"
        }
        save_to_database(f"Weather in {city}", str(weather_info))
        return weather_info
    else:
        return {"Error": "Error fetching weather data."}

# Set Reminder
def set_reminder(task, time):
    reminder_info = {"Task": task, "Time": time, "Status": "Reminder set"}
    save_to_database("Reminder", str(reminder_info))
    return reminder_info

# Answer Simple Questions
def answer_question(question):
    answers = {
        "What is your name?": "I am your virtual assistant.",
        "How can you help me?": "I can fetch weather info, set reminders, and answer simple questions.",
        "What is the weather like?": "Please provide a city name to fetch weather details."
    }
    response = answers.get(question, "I am not sure about that. Try asking something else.")
    save_to_database("Question", response)
    return response

# Non-interactive API-based function
def run_assistant(task_type, param1=None, param2=None):
    if task_type == "weather":
        return get_weather(param1)
    elif task_type == "reminder":
        return set_reminder(param1, param2)
    elif task_type == "question":
        return answer_question(param1)
    else:
        return {"Error": "Invalid task type."}

# Example Usage
if __name__ == "__main__":
    initialize_database()  # Ensure database setup before running
    print(run_assistant("weather", "New York"))
    print(run_assistant("reminder", "Meeting", "10:00 AM"))
    print(run_assistant("question", "What is your name?"))
