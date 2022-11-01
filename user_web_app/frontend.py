import os

from dotenv import load_dotenv
from flask import Flask, request, jsonify

mandatory_params = [
    "HOST",
    "PORT",
    "PROXY_URL"
]

load_dotenv()

for param in mandatory_params:
    if not os.getenv(param):
        raise SystemExit("[ENV] Parameter %s is mandatory" % param)

app = Flask(__name__)

if __name__ == "__main__":
    app.run(host=os.getenv("HOST"), port=int(str(os.getenv("PORT"))), debug=True)
