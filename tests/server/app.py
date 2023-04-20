import json

from flask import Flask, Response

app = Flask(__name__)


@app.route("/ai", methods=["GET"])
def noai_headers():
    response = Response()
    response.headers["X-Robots-Tag"] = "all"
    return response


@app.route("/noai", methods=["GET"])
def ai_headers():
    response = Response()
    response.headers["X-Robots-Tag"] = "noai"
    return response


@app.route("/user_agents", methods=["GET"])
def user_agents():
    response = Response()
    response.headers["X-Robots-Tag"] = "demobot: noai, examplebot: noai, spawningbot: all"
    return response


@app.route("/user_agents_noai", methods=["GET"])
def user_agents_noai():
    response = Response()
    response.headers["X-Robots-Tag"] = "demobot: noai, examplebot: noai, spawningbot: noai"
    return response


@app.route("/noindex", methods=["GET"])
def user_agents_noindex():
    response = Response()
    response.headers["X-Robots-Tag"] = "none, noindex"
    return response


@app.route("/opts", methods=["POST"])
def opts():
    json_body = {"urls": [
        {"url": "https://www.spawning.ai", "optOut": True, "optIn": False},
        {"url": "https://www.shutterstock.com", "optOut": False, "optIn": False},
        {"url": "https://open.ai", "optOut": False, "optIn": False},
        {"url": "https://www.google.com", "optOut": True, "optIn": False},
        {"url": "https://laion.ai", "optOut": True, "optIn": True},
        {"url": "https://www.youtube.com", "optOut": False, "optIn": False}
    ]}
    return Response(json.dumps(json_body), mimetype="application/json")


@app.route("/fail", methods=["POST"])
def fail():
    response = Response()
    response.status_code = 500
    return response


@app.route("/fail2", methods=["POST"])
def fail2():
    response = Response("not-json")
    response.headers["Content-Type"] = "application/json"
    response.status_code = 200
    return response
