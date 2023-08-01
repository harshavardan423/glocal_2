from flask import render_template, send_from_directory, request, jsonify
import json
import os
import smtplib
from glocal_2 import app

# Your email server and credentials
EMAIL_SERVER = "smpt.gmail.com"
EMAIL_PORT = 587
EMAIL_USERNAME = "glocalsmtp@gmail.com" #ENTER EMAIL HERE
EMAIL_PASSWORD = "glocalsmtp" #ENTER PASSWORD HERE

# Path to the JSON file
JSON_FILE_PATH = "tracking_data.json"

# Function to load tracking data from the JSON file
def load_tracking_data():
    if os.path.exists(JSON_FILE_PATH):
        with open(JSON_FILE_PATH, "r") as file:
            return json.load(file)
    return {
        "123456": [("In transit", "Hub A")],
        "789012": [("Delivered", "Hub B")],
        "345678": [("Out for delivery", "Hub C")],
    }

# Function to save tracking data to the JSON file
def save_tracking_data(tracking_data):
    with open(JSON_FILE_PATH, "w") as file:
        json.dump(tracking_data, file)

# Load initial tracking data from the JSON file
tracking_data = load_tracking_data()

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")


def send_email(name, email, selected_options):
    subject = "Received Quote - We'll call you back"
    options_text = "\n".join(f"- {option}" for option in selected_options)
    body = f"Dear {name},\n\nThank you for contacting us. We have received your quote.\n\nSelected options:\n{options_text}\n\nWe'll call you back soon.\n\nBest regards,\nYour Company Name"

    # Connect to the SMTP server
    with smtplib.SMTP(EMAIL_SERVER, EMAIL_PORT) as server:
        server.starttls()
        # Login to the server
        server.login(EMAIL_USERNAME, EMAIL_PASSWORD)

        # Create the email message
        message = f"Subject: {subject}\n\n{body}"

        # Send the email
        server.sendmail(EMAIL_USERNAME, email, message)


@app.route("/update_status", methods=["GET"])
def update_status():
    tracking_id = request.args.get("tracking_id")
    status_data = tracking_data.get(tracking_id)

    if status_data:
        status, hub = status_data[-1]  # Get the latest status update
        status_message = f"{status} - Currently at {hub}"
    else:
        status_message = "Invalid tracking ID"

    return status_message

@app.route("/GLOX7MBQRX5MU7GCAL", methods=["GET", "POST"])
def company():
    if request.method == "POST":
        tracking_id = request.form.get("tracking_id")
        status = request.form.get("status")
        hub = request.form.get("hub")

        if tracking_id and status and hub:
            if tracking_id in tracking_data:
                tracking_data[tracking_id].append((status, hub))
            else:
                tracking_data[tracking_id] = [(status, hub)]

            # Save the updated tracking data to the JSON file
            save_tracking_data(tracking_data)

            return "Status update added successfully."
        else:
            return "Missing tracking ID, status, or hub.", 400

    return render_template("company.html")


@app.route("/test")
def test():
    return render_template("test.html")


@app.route("/about")
def about():
    return "This is the about page."





# Serve static files (images, CSS, JS, etc.)
@app.route('/static/<path:path>')
def serve_static(path):
    return send_from_directory('static', path)
