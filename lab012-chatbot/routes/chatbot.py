# Copyright 2023 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import logging

import flask
from flask import Blueprint, jsonify, redirect, render_template, request, url_for

chatbot_bp = Blueprint("chatbot", __name__)


@chatbot_bp.route("/chatbot")
def index():
    if "user_id" not in flask.session:
        return redirect(url_for("auth.login"))
    return render_template("chatbot.html")


@chatbot_bp.route("/get_response", methods=["POST"])
def get_response():
    try:
        from .models.chatbot_service import predict

        message = request.form["message"]
        response = predict(message)
        return jsonify({"response": response})
    except Exception as e:
        logging.exception(str(e), extra={"stack": True})
        return jsonify({"response": f"[Error]{str(e)}"})
