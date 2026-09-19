from flask import Flask, request, jsonify
from flask_cors import CORS
import pyautogui


app = Flask(__name__)

CORS(app)


@app.route("/control", methods=["POST"])
def control():

    data = request.get_json()

    action = data.get("action")


    if action == "play_pause":

        pyautogui.press("playpause")


    elif action == "mute":

        pyautogui.press("volumemute")


    elif action == "volume_up":

        pyautogui.press("volumeup")


    elif action == "volume_down":

        pyautogui.press("volumedown")


    elif action == "next":

        pyautogui.press("nexttrack")


    elif action == "previous":

        pyautogui.press("prevtrack")


    else:

        return jsonify({
            "success": False,
            "message": "Unknown action"
        }), 400


    return jsonify({
        "success": True,
        "action": action
    })


@app.route("/")
def home():

    return "AI Gesture Music Controller is running!"


if __name__ == "__main__":

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )