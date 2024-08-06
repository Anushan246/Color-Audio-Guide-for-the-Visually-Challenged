import cv2
import numpy as np
import pandas as pd
import pyttsx3
import threading
import time
from tkinter import Tk, Label, Entry, Button, StringVar
import speech_recognition as sr

# Initialize text-to-speech engine
engine = pyttsx3.init()
engine.setProperty('rate', 150)  # Adjust speech rate (default is 200)
engine.setProperty('volume', 1)  # Adjust volume (default is 1.0)

# Read the CSV file containing color names
colors_csv = 'colors.csv'

# Load color names
def load_colors(csv_file):
    index = ['color', 'color_name', 'hex', 'R', 'G', 'B']
    colors = pd.read_csv(csv_file, names=index, header=None)
    return colors

colors = load_colors(colors_csv)

# Function to get the color name from RGB values #Nearest Neighbor Color Matching
def get_color_name(R, G, B):
    R, G, B = int(R), int(G), int(B)
    minimum = float('inf')
    cname = "Unknown"
    for i in range(len(colors)):
        d = abs(R - int(colors.loc[i, "R"])) + abs(G - int(colors.loc[i, "G"])) + abs(B - int(colors.loc[i, "B"]))
        if d < minimum:
            minimum = d
            cname = colors.loc[i, "color_name"]
    return cname

# Function to speak the color name asynchronously
def speak_color_async(color_name):
    threading.Thread(target=speak_color, args=(color_name,)).start()

def speak_color(color_name):
    engine.say(color_name)
    engine.runAndWait()

# Function to speak text asynchronously
def speak_async(text):
    threading.Thread(target=speak, args=(text,)).start()

def speak(text):
    engine.say(text)
    engine.runAndWait()

# Function for voice input
def voice_input(prompt):
    r = sr.Recognizer()
    with sr.Microphone() as source:
        speak(prompt)
        audio = r.listen(source)
        try:
            text = r.recognize_google(audio)
            speak(f"You said: {text}. Is this correct?")
            confirmation = input("Type 'yes' to confirm or 'no' to try again: ")
            if confirmation.lower() == 'yes':
                return text
            else:
                return voice_input(prompt)
        except sr.UnknownValueError:
            speak("Sorry, I didn't catch that. Please try again.")
            return voice_input(prompt)

# Function to handle registration
registered_username = None
registered_password = None

def register():
    global registered_username, registered_password
    registered_username = username_var.get()
    registered_password = password_var.get()
    speak("Registration Successful!")
    register_window.destroy()
    # Optionally start face detection or other functionalities
    # start_face_detection()

# Function to create the registration window
def create_register_window():
    global register_window, username_var, password_var

    register_window = Tk()
    register_window.title("Register")

    username_var = StringVar()
    password_var = StringVar()

    speak("Welcome to the registration page.")

    username_label = Label(register_window, text="Username")
    username_label.grid(row=0, column=0)
    username_entry = Entry(register_window, textvariable=username_var)
    username_entry.grid(row=0, column=1)
    username_entry.bind("<FocusIn>", lambda e: speak("Enter username"))

    password_label = Label(register_window, text="Password")
    password_label.grid(row=1, column=0)
    password_entry = Entry(register_window, textvariable=password_var, show='*')
    password_entry.grid(row=1, column=1)
    password_entry.bind("<FocusIn>", lambda e: speak("Enter password"))

    register_button = Button(register_window, text="Register", command=register)
    register_button.grid(row=2, column=0, columnspan=2)
    register_button.bind("<FocusIn>", lambda e: speak("Press Enter to register"))

    voice_button = Button(register_window, text="Use Voice Input", command=lambda: use_voice_input())
    voice_button.grid(row=3, column=0, columnspan=2)
    voice_button.bind("<FocusIn>", lambda e: speak("Press Enter to use voice input"))

    speak("Use Tab to navigate between fields. Press Enter to activate buttons.")
    register_window.mainloop()

def use_voice_input():
    username = voice_input("Please say your username")
    username_var.set(username)
    password = voice_input("Please say your password")
    password_var.set(password)

# Start capturing video for color detection
def start_color_detection():
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW) 
    cap.set(cv2.CAP_PROP_FPS, 10)  # Adjust the FPS as needed

    # Define the frequency of TTS updates (in seconds)
    tts_update_interval = 5  # Adjust as needed to make speech slower
    last_spoken_time = time.time()

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Resize the frame for faster processing
        small_frame = cv2.resize(frame, (320, 240))

        # Convert the image to RGB
        img_rgb = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

        # Get the center pixel
        height, width, _ = img_rgb.shape
        cx, cy = width // 2, height // 2
        center_pixel = img_rgb[cy, cx]
        R, G, B = center_pixel

        # Get the color name
        color_name = get_color_name(R, G, B)

        # Draw a rectangle and text
        cv2.rectangle(frame, (cx - 100, cy - 100), (cx + 100, cy + 100), (255, 255, 255), 2)
        cv2.putText(frame, f'{color_name}', (cx - 40, cy - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)

        # Display the frame
        cv2.imshow('Color Detection', frame)

        # Voice feedback at a controlled interval
        current_time = time.time()
        if current_time - last_spoken_time > tts_update_interval:
            speak_color_async(color_name)
            last_spoken_time = current_time

        # Exit on 'q' key
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Release the capture
    cap.release()
    cv2.destroyAllWindows()

# Main function
if __name__ == '__main__':
    create_register_window()
    start_color_detection()
