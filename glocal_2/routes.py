from flask import render_template, request,send_from_directory
import json
import os
import smtplib
from twilio.rest import Client  # Twilio library for sending SMS
from glocal_2 import app

# Your email server and credentials
EMAIL_SERVER = "smtp.gmail.com"
EMAIL_PORT = 587
EMAIL_USERNAME = "glocalsmtp@gmail.com"  # ENTER EMAIL HERE
EMAIL_PASSWORD = "glocalsmtp"  # ENTER PASSWORD HERE

# Twilio credentials
TWILIO_ACCOUNT_SID = "YOUR_TWILIO_ACCOUNT_SID"
TWILIO_AUTH_TOKEN = "YOUR_TWILIO_AUTH_TOKEN"
TWILIO_PHONE_NUMBER = "YOUR_TWILIO_PHONE_NUMBER"

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
    body = f"Dear {name},\n\nThank you for contacting us. We have received your quote.\n\nSelected options:\n{options_text}\n\nWe'll call you back soon.\n\nBest regards,\nGlocal"

    # Connect to the SMTP server
    with smtplib.SMTP(EMAIL_SERVER, EMAIL_PORT) as server:
        server.starttls()
        # Login to the server
        server.login(EMAIL_USERNAME, EMAIL_PASSWORD)

        # Create the email message
        message = f"Subject: {subject}\n\n{body}"

        # Send the email
        server.sendmail(EMAIL_USERNAME, email, message)

def send_sms(phone_number, selected_options):
    client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

    options_text = "\n".join(f"- {option}" for option in selected_options)
    body = f"Thank you for contacting us. We have received your quote.\n\nSelected options:\n{options_text}\n\nWe'll call you back soon.\n\nBest regards,\nYour Company Name"

    # Send the SMS message
    client.messages.create(
        body=body,
        from_=TWILIO_PHONE_NUMBER,
        to=phone_number
    )

@app.route("/submit_quote", methods=["POST"])
def submit_quote():
    name = request.form.get("name")
    email = request.form.get("email")
    phone_number = request.form.get("phonenumber")
    website = request.form.get("website")
    branding = request.form.get("branding")
    ecommerce = request.form.get("ecommerce")
    seo = request.form.get("seo")

    selected_options = []
    if website:
        selected_options.append("Glocal City Express")
    if branding:
        selected_options.append("Glocal Parcel Express")
    if ecommerce:
        selected_options.append("Glocal Transportation")
    if seo:
        selected_options.append("Glocal Premium Express")

    send_email(name, email, selected_options)
    send_sms(phone_number, selected_options)

    # Save the submitted data to the JSON file (You can modify this part as needed)
    tracking_data[name] = selected_options
    save_tracking_data(tracking_data)

    return "Quote submitted successfully!"

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
