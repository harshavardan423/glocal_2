from flask import render_template, request,send_from_directory,jsonify,send_file,flash,redirect,url_for
import json
import os
import smtplib
from twilio.rest import Client  # Twilio library for sending SMS
from glocal_2 import app
from functools import wraps
import pandas as pd
from datetime import datetime
from urllib.parse import quote, unquote
from run import TRACKING_EXCEL_FILE_PATH,QUOTES_EXCEL_FILE_PATH  # Import the variable from run.py
from glocal_2 import app 



app.secret_key = "672f8c533cd0e61d35ab2c2b38c57850"
# Your email server and credentials
EMAIL_SERVER = "smtp.gmail.com"
EMAIL_PORT = 587
EMAIL_USERNAME = "glocalsmtp@gmail.com"  # ENTER EMAIL HERE
EMAIL_PASSWORD = "glocalsmtp"  # ENTER PASSWORD HERE

# Twilio credentials
TWILIO_ACCOUNT_SID = "ACa3f60b67ac2ec927bec20d66199a8e21"
TWILIO_AUTH_TOKEN = "e55bedcecaa51c9fc3549742fc275f71"
TWILIO_PHONE_NUMBER = "+14707480048"

# Path to the JSON file
JSON_FILE_PATH = "tracking_data.json"

password = "Guru"



@app.route('/download_ts_excel')
def download_ts_excel():
    return send_file(TRACKING_EXCEL_FILE_PATH, as_attachment=True)

@app.route('/download_q_excel')
def download_q_excel():
    return send_file(QUOTES_EXCEL_FILE_PATH, as_attachment=True)



def load_tracking_data_excel():
    try:
        tracking_data = pd.read_excel(TRACKING_EXCEL_FILE_PATH)
    except FileNotFoundError:
        tracking_data = pd.DataFrame(columns=["Tracking ID", "Status", "Hub", "Timestamp"])
    return tracking_data

tracking_data_excel = load_tracking_data_excel()



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

@app.route("/", methods=["GET","POST"])
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


# @app.route("/update_status", methods=["GET"])
# def update_status():
#     tracking_id = request.args.get("tracking_id")
#     status_data = tracking_data.get(tracking_id)

#     if status_data:
#         status, hub = status_data[-1]  # Get the latest status update
#         status_message = f"{status} - Currently at {hub}"
#     else:
#         status_message = "Invalid tracking ID"

#     return status_message

#EXCEL VERSION
@app.route("/update_status", methods=["GET"])
def update_status():
    tracking_id = request.args.get("tracking_id")
    # print("Received Tracking ID (Raw):", tracking_id)  # Debug print

    # Strip any leading/trailing whitespaces
    tracking_id = tracking_id.strip()

    # print("Stripped Tracking ID:", tracking_id)  # Debug print

    # Convert the "Tracking ID" column to strings and then perform .str.strip()
    tracking_data_excel["Tracking ID"] = tracking_data_excel["Tracking ID"].astype(str)
    status_row = tracking_data_excel[tracking_data_excel["Tracking ID"].str.strip() == tracking_id]

    # print("Matching Rows:", status_row)  # Debug print

    if not status_row.empty:
        status = status_row["Status"].iloc[-1]
        hub = status_row["Hub"].iloc[-1]
        timestamp = status_row["Timestamp"].iloc[-1]  # Extract timestamp for the matching row
        
        # Determine progress steps based on status
        progress_steps = ['step0', 'step0', 'step0', 'step0']
        if status == "Order Placed":
            progress_steps[0] = 'active'
        elif status == "In Transit":
            progress_steps[0] = 'active'
            progress_steps[1] = 'active'
        elif status == "Out for delivery":
            progress_steps[0] = 'active'
            progress_steps[1] = 'active'
            progress_steps[2] = 'active'
        elif status == "Delivered":
            progress_steps = ['active', 'active', 'active', 'active']
        
        # Load the tracking_status.html template and render it
        rendered_html = render_template(
            "tracking_status.html",
            status=status,
            timestamp=timestamp,
            hub=hub,
            progress_steps=progress_steps,
            tracking_id = tracking_id
        )
        
        response_data = {
            "html": rendered_html,
            "progressSteps": progress_steps
        }
        print(response_data)
        return jsonify(response_data)
    else:
        return jsonify({"error": "Invalid tracking ID"})

def send_sms(phone_number, selected_options):
    
    account_sid = TWILIO_ACCOUNT_SID
    auth_token = TWILIO_AUTH_TOKEN
    client = Client(account_sid, auth_token)



    body = f"Thank you for contacting us. We have received your quote.\n\n\nOur representatives will call you back soon.\n\nBest regards,\nGlocal"

    # Send the SMS message
    client.messages.create(
        body=body,
        from_= TWILIO_PHONE_NUMBER,
        to=f"+91{phone_number}"
    )
    print("sent sms")


def load_quotes_data_excel():
    try:
        quotes_data = pd.read_excel(QUOTES_EXCEL_FILE_PATH)
    except FileNotFoundError:
        quotes_data = pd.DataFrame(columns=["Name", "Phone Number", "Selected Options"])
    return quotes_data

quotes_data_excel = load_quotes_data_excel()


# JSON VERSION
# @app.route("/submit_quote", methods=["POST"])
# def submit_quote():
#     name = request.form.get("name")
#     email = request.form.get("email")
#     phone_number = request.form.get("phonenumber")
#     website = request.form.get("website")
#     branding = request.form.get("branding")
#     ecommerce = request.form.get("ecommerce")
#     seo = request.form.get("seo")

#     selected_options = []
#     if website:
#         selected_options.append("Glocal City Express")
#     if branding:
#         selected_options.append("Glocal Parcel Express")
#     if ecommerce:
#         selected_options.append("Glocal Transportation")
#     if seo:
#         selected_options.append("Glocal Premium Express")

#     # Prepare data to be saved in JSON format
#     data = {
#         "name": name,
#         "phone_number": phone_number,
#         "selected_options" : selected_options
#     }

#     # Save the data to a JSON file
#     with open("quotes.json", "a") as json_file:
#         json.dump(data, json_file)
#         json_file.write("\n")  # Add a newline for separating multiple entries

#     # send_email(name, email , selected_options)# 
#     send_sms(phone_number , selected_options) #


    

#     return "Quote submitted successfully!"


@app.route("/submit_quote", methods=["POST"])
def submit_quote():
    name = request.form.get("name")
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

    new_entry = {"Name": name, "Phone Number": phone_number, "Selected Options": ", ".join(selected_options)}

    global quotes_data_excel
    
    quotes_data_excel = quotes_data_excel.append(new_entry, ignore_index=True)

    # Save the updated quotes data to the Excel file
    quotes_data_excel.to_excel(QUOTES_EXCEL_FILE_PATH, index=False)

    # send_email(name, email, selected_options)
    send_sms(phone_number, selected_options)

    # Example: Assuming the quote was submitted successfully
    flash('Quote submitted successfully!', 'success')
    
    return redirect(url_for('index'))

def require_password(view_func):
    @wraps(view_func)
    def decorated(*args, **kwargs):
        entered_password = request.args.get("password")
        if entered_password != password:
            return "Invalid password.", 401
        return view_func(*args, **kwargs)
    return decorated

# JSON VERSION

# @app.route("/GLOX7MBQRX5MU7GCAL", methods=["GET", "POST"])
# def company():
#     if request.method == "POST":
#         tracking_id = request.form.get("tracking_id")
#         status = request.form.get("status")
#         hub = request.form.get("hub")

#         if tracking_id and status and hub:
#             if tracking_id in tracking_data:
#                 tracking_data[tracking_id].append((status, hub))
#             else:
#                 tracking_data[tracking_id] = [(status, hub)]

#             # Save the updated tracking data to the JSON file
#             save_tracking_data(tracking_data)

#             return "Status update added successfully."
#         else:
#             return "Missing tracking ID, status, or hub.", 400

#     return render_template("tracking_update.html")

# EXCEL VERSION
@app.route("/GLOX7MBQRX5MU7GCAL", methods=["GET", "POST"])
def company():
    global tracking_data_excel
    
    if request.method == "POST":
        tracking_id = request.form.get("tracking_id")
        status = request.form.get("status")
        hub = request.form.get("hub")

        if tracking_id and status and hub:
            now = datetime.now()
            timestamp = now.strftime("%Y-%m-%d %H:%M:%S")

            # Check if the tracking ID already exists in the DataFrame
            existing_row = tracking_data_excel[tracking_data_excel["Tracking ID"] == tracking_id]

            if not existing_row.empty:
                # Update the existing row
                tracking_data_excel.loc[existing_row.index, "Status"] = status
                tracking_data_excel.loc[existing_row.index, "Hub"] = hub
                tracking_data_excel.loc[existing_row.index, "Timestamp"] = timestamp
            else:
                # Create a new row
                new_entry = {"Tracking ID": tracking_id, "Status": status, "Hub": hub, "Timestamp": timestamp}
                tracking_data_excel = tracking_data_excel.append(new_entry, ignore_index=True)

            # Save the updated tracking data to the Excel file
            tracking_data_excel.to_excel(TRACKING_EXCEL_FILE_PATH, index=False)

            # return "Status update added successfully."
        # Example: Assuming the quote was submitted successfully
            flash('Status Updated Successfully', 'success')
            
            return redirect(url_for('company'))
        else:
            flash('There was an error updating the status', 'fail')
            
            return redirect(url_for('company'))
    return render_template("tracking_update.html")

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
