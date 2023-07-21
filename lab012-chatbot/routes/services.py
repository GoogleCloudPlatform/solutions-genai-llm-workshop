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
import flask
from flask import Blueprint, redirect, render_template, url_for

services_bp = Blueprint("services", __name__)

# A list of services and their corresponding URLs
services = [
    {
        "name": "Chatbot",
        "url": "chatbot",
        "description": "Chatbot Customer Service Samlpe",
    }
]


# Route for the services page
@services_bp.route("/")
def services_page():
    if "user_id" not in flask.session:
        return redirect(url_for("auth.login"))
    return render_template("services.html", services=services)
