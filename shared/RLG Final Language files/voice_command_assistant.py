import speech_recognition as sr
import pyttsx3
import datetime
import webbrowser
import os
import json
import requests

# Define supported voice commands
COMMANDS = {
    "time": "tell the current time",
    "date": "tell today's date",
    "open website": "open a specified website",
    "search": "perform a web search",
    "read notifications": "read out notifications",
    "post update": "post an update to social media",
    "fetch insights": "fetch analytics insights",
    "exit": "exit the assistant"
}

class VoiceCommandAssistant:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.speaker = pyttsx3.init()
        self.speaker.setProperty('rate', 150)
        self.api_base_url = "https://rlgdata-api.com"

    def speak(self, text):
        """
        Converts text to speech.
        """
        self.speaker.say(text)
        self.speaker.runAndWait()

    def listen(self):
        """
        Captures audio and converts to text.
        """
        with sr.Microphone() as source:
            print("🎤 Listening...")
            self.recognizer.adjust_for_ambient_noise(source)
            try:
                audio = self.recognizer.listen(source, timeout=5)
                command = self.recognizer.recognize_google(audio).lower()
                print(f"✅ Recognized Command: {command}")
                return command
            except sr.UnknownValueError:
                self.speak("Sorry, I didn't understand that.")
            except sr.RequestError:
                self.speak("Network issue. Please check your connection.")
        return None

    def execute_command(self, command):
        """
        Processes recognized voice commands.
        """
        if "time" in command:
            now = datetime.datetime.now().strftime("%H:%M")
            self.speak(f"The current time is {now}")

        elif "date" in command:
            today = datetime.datetime.now().strftime("%A, %B %d, %Y")
            self.speak(f"Today is {today}")

        elif "open" in command:
            self.speak("Which website should I open?")
            site = self.listen()
            if site:
                url = f"https://{site}.com"
                webbrowser.open(url)
                self.speak(f"Opening {site}")

        elif "search" in command:
            self.speak("What would you like to search for?")
            query = self.listen()
            if query:
                webbrowser.open(f"https://www.google.com/search?q={query}")
                self.speak(f"Searching Google for {query}")

        elif "read notifications" in command:
            notifications = self.get_notifications()
            if notifications:
                self.speak(f"You have {len(notifications)} new notifications.")
                for note in notifications:
                    self.speak(note)
            else:
                self.speak("No new notifications.")

        elif "post update" in command:
            self.speak("What would you like to post?")
            update = self.listen()
            if update:
                self.post_social_update(update)
                self.speak("Your update has been posted.")

        elif "fetch insights" in command:
            insights = self.fetch_analytics()
            if insights:
                self.speak(f"Your top insight: {insights[0]}")
            else:
                self.speak("No new insights available.")

        elif "exit" in command:
            self.speak("Goodbye!")
            exit()

        else:
            self.speak("I'm sorry, I didn't understand that command.")

    def get_notifications(self):
        """
        Fetches user notifications from RLG Data API.
        """
        try:
            response = requests.get(f"{self.api_base_url}/notifications")
            return response.json().get("notifications", [])
        except requests.exceptions.RequestException:
            return []

    def post_social_update(self, update):
        """
        Posts an update to social media.
        """
        data = {"content": update}
        try:
            requests.post(f"{self.api_base_url}/post-update", json=data)
        except requests.exceptions.RequestException:
            pass

    def fetch_analytics(self):
        """
        Fetches social media insights.
        """
        try:
            response = requests.get(f"{self.api_base_url}/analytics")
            return response.json().get("insights", [])
        except requests.exceptions.RequestException:
            return []

if __name__ == "__main__":
    assistant = VoiceCommandAssistant()
    assistant.speak("Hello! Voice Assistant is now active.")

    while True:
        command = assistant.listen()
        if command:
            assistant.execute_command(command)
