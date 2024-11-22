from flask import Flask, request, jsonify
import pandas as pd
import speech_recognition as sr

app = Flask(__name__)

# Load menu
menu = pd.read_csv("menu.csv")
cart = []

@app.route('/menu', methods=['GET'])
def get_menu():
    return menu.to_json(orient="records")

@app.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    global cart
    item_name = request.json.get("item_name")
    matching_items = menu[menu['Item Name'].str.contains(item_name, case=False)]
    if not matching_items.empty:
        item = matching_items.iloc[0]
        cart.append(item)
        return jsonify({"message": f"Added {item['Item Name']} - ${item['Price']} to cart."})
    else:
        return jsonify({"message": "Item not found in the menu."})

@app.route('/bill', methods=['GET'])
def get_bill():
    global cart
    if cart:
        total = sum(item['Price'] for item in cart)
        return jsonify({"cart": [{"Item Name": i['Item Name'], "Price": i['Price']} for i in cart], "total": total})
    else:
        return jsonify({"message": "Your cart is empty."})

@app.route('/voice_command', methods=['POST'])
def process_voice_command():
    global cart
    recognizer = sr.Recognizer()
    try:
        audio_file = request.files['audio']
        with sr.AudioFile(audio_file) as source:
            audio = recognizer.record(source)
        command = recognizer.recognize_google(audio).lower()
        if "bill please" in command:
            return get_bill()
        elif "add" in command or "order" in command:
            item_name = command.replace("add", "").replace("order", "").strip()
            matching_items = menu[menu['Item Name'].str.contains(item_name, case=False)]
            if not matching_items.empty:
                item = matching_items.iloc[0]
                cart.append(item)
                return jsonify({"message": f"Added {item['Item Name']} - ${item['Price']} to cart."})
            else:
                return jsonify({"message": "Item not found in the menu."})
        else:
            return jsonify({"message": "Invalid command or no items mentioned."})
    except Exception as e:
        return jsonify({"error": str(e)})

# Main entry point for Vercel
if __name__ == "__main__":
    app.run()
