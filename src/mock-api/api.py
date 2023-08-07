import json

import pytz as pytz
from flask import request
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import generate_password_hash, check_password_hash

from flask import Flask, Response
from dateutil import parser

app = Flask(__name__)

utc = pytz.UTC

auth = HTTPBasicAuth()

users = {
    "api": generate_password_hash("api"),
}


@auth.verify_password
def verify_password(username, password):
    if username in users and check_password_hash(users.get(username), password):
        return username


sample_data = json.loads(open("./mock-data.json").read())


@app.route("/test")
@auth.login_required()
def test():
    return Response(
        response=json.dumps({"status": "ok"}), status=200, mimetype="application/json"
    )


@app.route("/orders")
@auth.login_required
def orders():
    query_string = request.args
    if "since" not in query_string:
        return Response("Since required", status=400)

    try:
        since = utc.localize(parser.parse(query_string["since"]))
    except Exception as e:
        return Response("Since must be a valid date in ISO-8601 format", status=400)

    if "page" not in query_string:
        page = 0
    else:
        page = int(query_string["page"])

    page_size = 25
    offset = page_size * page
    count = 0
    result = []
    for rec in sample_data["data"]:
        d = utc.localize(parser.parse(rec["updated_at"]))
        if d > since:
            if offset == 0:
                result.append(rec)
                count += 1
            else:
                offset -= 1

        if count == page_size:
            break

    return Response(
        response=json.dumps(result), status=200, mimetype="application/json"
    )
