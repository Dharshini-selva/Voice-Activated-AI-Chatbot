from flask import Flask, render_template, request, jsonify
import speech_recognition as sr
import pyttsx3
import wikipedia
import webbrowser
import os
import datetime
import requests
import json
import subprocess
import threading
import time

app = Flask(__name__)

# Initialize text-to-speech engine
try:
    engine = pyttsx3.init()
    voices = engine.getProperty('voices')
    if len(voices) > 1:
        engine.setProperty('voice', voices[1].id)  # 0 for male, 1 for female
    engine.setProperty('rate', 150)
except Exception as e:
    print(f"Error initializing TTS engine: {e}")
    engine = None

# Function to convert text to speech
def speak(text):
    if engine is None:
        print(f"TTS not available: {text}")
        return
        
    def speak_thread(text):
        engine.say(text)
        engine.runAndWait()
    
    thread = threading.Thread(target=speak_thread, args=(text,))
    thread.start()

# Function to recognize speech
def recognize_speech():
    r = sr.Recognizer()
    try:
        with sr.Microphone() as source:
            print("Listening...")
            r.adjust_for_ambient_noise(source, duration=0.5)
            r.pause_threshold = 1
            audio = r.listen(source, timeout=5)
        
        try:
            print("Recognizing...")
            query = r.recognize_google(audio, language='en-in')
            print(f"User said: {query}\n")
            return query.lower()
        except sr.UnknownValueError:
            return "None"
        except sr.RequestError as e:
            print(f"Could not request results from Google Speech Recognition service; {e}")
            return "None"
    except Exception as e:
        print(f"Error in speech recognition: {e}")
        return "None"

# Function to process commands
def process_command(command):
    response = ""
    exit_flag = False
    
    if 'wikipedia' in command:
        command = command.replace("wikipedia", "").strip()
        try:
            results = wikipedia.summary(command, sentences=2)
            response = f"According to Wikipedia: {results}"
        except wikipedia.exceptions.DisambiguationError as e:
            response = f"There are multiple results for {command}. Please be more specific."
        except wikipedia.exceptions.PageError:
            response = f"Sorry, I couldn't find information about {command} on Wikipedia."
        except Exception as e:
            response = "Sorry, I encountered an error while searching Wikipedia."
    
    elif 'open youtube' in command:
        webbrowser.open("https://youtube.com")
        response = "Opening YouTube"
    
    elif 'open google' in command:
        webbrowser.open("https://google.com")
        response = "Opening Google"
    
    elif 'open stackoverflow' in command:
        webbrowser.open("https://stackoverflow.com")
        response = "Opening Stack Overflow"
    
    elif 'time' in command:
        strTime = datetime.datetime.now().strftime("%H:%M:%S")
        response = f"The time is {strTime}"
    
    elif 'date' in command:
        strDate = datetime.datetime.now().strftime("%B %d, %Y")
        response = f"Today is {strDate}"
    
    elif 'search' in command:
        command = command.replace("search", "").strip()
        webbrowser.open(f"https://www.google.com/search?q={command}")
        response = f"Searching for {command} on Google"
    
    elif 'exit' in command or 'quit' in command or 'goodbye' in command:
        response = "Goodbye! Have a great day!"
        exit_flag = True
    
    elif 'who are you' in command or 'what can you do' in command:
        response = "I am your voice assistant. I can search the web, tell you the time and date, look up information on Wikipedia, and more!"
    
    elif 'hello' in command or 'hi' in command:
        response = "Hello! How can I help you today?"
    
    else:
        response = "I'm sorry, I didn't understand that command. Please try again."
    
    return response, exit_flag

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/voice_command', methods=['POST'])
def voice_command():
    try:
        command = recognize_speech()
        if command == "None":
            return jsonify({"response": "I didn't catch that. Please try again.", "exit": False})
        
        response, exit_flag = process_command(command)
        return jsonify({"response": response, "exit": exit_flag})
    except Exception as e:
        return jsonify({"response": f"An error occurred: {str(e)}", "exit": False})

@app.route('/text_command', methods=['POST'])
def text_command():
    try:
        data = request.get_json()
        command = data.get('command', '').lower()
        
        if not command:
            return jsonify({"response": "No command received", "exit": False})
        
        response, exit_flag = process_command(command)
        return jsonify({"response": response, "exit": exit_flag})
    except Exception as e:
        return jsonify({"response": f"An error occurred: {str(e)}", "exit": False})

@app.route('/speak', methods=['POST'])
def speak_text():
    try:
        data = request.get_json()
        text = data.get('text', '')
        if text:
            speak(text)
        return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

if __name__ == '__main__':
    app.run(debug=True)