from glocal_2 import app
from glocal_2 import routes 
import os



BASE_DIR = os.path.abspath(os.path.dirname(__file__))
TRACKING_EXCEL_FILE_PATH = os.path.join(BASE_DIR, "tracking_data.xlsx")
QUOTES_EXCEL_FILE_PATH = os.path.join(BASE_DIR, "quotes.xlsx")


if __name__ == "__main__":
    app.run(debug=False)

        