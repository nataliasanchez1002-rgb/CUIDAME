CuidaME App

An interactive application built with Python and Kivy/KivyMD designed to teach children about personal safety, emotions, and risk prevention through games, chat, and real-time body detection using AI.
--------------------------------------------------------------------------------

# Tech Stack

* Python
* Kivy / KivyMD
* OpenCV
* TensorFlow Lite (MoveNet)
* JSON
---------------------------------------------------------------------------------
 Requirements

* Python 3.9 – 3.11 recommended
* Visual Studio Code installed
-----------------------------------------------------------------------------------
 Setup in Visual Studio Code

Open the project

* Open Visual Studio Code
* Click on **File → Open Folder**
* Select your project folder

------------------------------------
Install dependencies

Open the terminal in VS Code and run:

pip install kivy kivymd opencv-python numpy tensorflow

-------------------------------------------------------------------

 Add the MoveNet model

Make sure this folder exists in your project:


movenet-tflite-singlepose-lightning-v1/
    └── 3.tflite
--------------------------------------------------------------------
 Project structure

project/
│
├── main.py
├── cuidaME.kv
├── usuarios.json
├── usuario_deteccion_riesgo.json
│
├── Imagenes/
│   └── (game images)
│
└── movenet-tflite-singlepose-lightning-v1/
    └── 3.tflite
--------------------------------------------------------

Run the App

In the VS Code terminal:

python cuidaME.py
---------------------------------------------------------

 Notes

* The app is designed to run on desktop using Python (not as an APK)
* A webcam is required for the body detection feature
* Make sure all files and folders are correctly placed
* If the model file is missing, the detection feature will not work

---
