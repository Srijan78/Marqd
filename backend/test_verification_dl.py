import os
import sys

# Add backend directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from flask import Flask
from app.services.verification import VerificationService

app = Flask(__name__)
app.config['TEMP_FOLDER'] = 'temp_test'
app.config['USE_MOCK_APIS'] = False

def test():
    url = "https://www.tribuneindia.com/news/sports/selfless-super-hit-kl-rahuls-record-breaking-knock-gets-high-praise-from-kaif-pathan/"
    with app.app_context():
        res = VerificationService.download_image(url)
        print("Download result:", res)

if __name__ == "__main__":
    test()
