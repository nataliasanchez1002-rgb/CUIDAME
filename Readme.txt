# CuidaME App

CuidaME is an interactive desktop application built with Python and Kivy/KivyMD.
It is designed to teach children about personal safety, emotions, and risk prevention through games, an AI-powered chatbot, and real-time body detection.

---------------------------------------

## Features

* Educational mini-games for children
* Chatbot that detects risky or sensitive language
* Real-time body pose detection using AI (MoveNet)
* User data storage using JSON

---------------------------------------------------

## Tech Stack

* Python
* Kivy / KivyMD
* OpenCV
* TensorFlow Lite (MoveNet)
* JSON

-----------------------------------------

## Requirements

* Python 3.9 – 3.11
* Visual Studio Code
* Webcam (required for body detection)

----------------------------------------

## Installation

### 1. Open the project

* Open Visual Studio Code
* Go to **File → Open Folder**
* Select the project folder

--------------------------------------

### 2. Install dependencies

Open the terminal in VS Code and run:

pip install kivy kivymd opencv-python numpy tensorflow

Or create a file named `requirements.txt` with the following content:

kivy
kivymd
opencv-python
numpy
tensorflow

Then install using:

pip install -r requirements.txt

-------------------------------------------------

### 3. Add the MoveNet model

Make sure the following folder exists in your project:

movenet-tflite-singlepose-lightning-v1/
└── 3.tflite

This model is used for real-time body pose detection.

------------------------------------------------

## Project Structure

project/
│
├── cuidaME.py
├── cuidaME.kv
├── usuarios.json
├── usuario_deteccion_riesgo.json
│
├── Imagenes/
│   └── (game images)
│
└── movenet-tflite-singlepose-lightning-v1/
└── 3.tflite

------------------------------------------------

## Run the App

In the VS Code terminal:

python cuidaME.py

-----------------------------------------------

## Notes

* This application runs on desktop using Python (not as an APK)
* A webcam / laptop camera is required for the AI detection feature
* Make sure all files are correctly placed
* If the model file is missing, the detection feature will not work

