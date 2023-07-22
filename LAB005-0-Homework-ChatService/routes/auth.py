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
from flask import Blueprint, redirect, render_template, request, url_for

auth_bp = Blueprint("auth", __name__)

# Define the roles and their corresponding permissions.
roles = {
    "guest": {
        "can_view_board": True,
        "can_add_posts": True,
        "can_delete_posts": True,
        "can_reply_posts": False,
    },
    "admin": {
        "can_view_board": True,
        "can_add_posts": True,
        "can_delete_posts": False,
        "can_reply_posts": True,
    },
}
role_map = {
    "user1@example.com": "guest",
    "user2@example.com": "admin",
}
# Define the users and their corresponding passwords.
users = {
    "user1@example.com": "password1",
    "user2@example.com": "password2",
}


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")

    email = request.form.get("email")
    password = request.form.get("password")

    # Check if the user's email and password are valid.
    if email not in users or users[email] != password:
        return render_template("login.html", error="Invalid email or password.")

    # Login the user.
    flask.session["user_id"] = email
    # flask.session["role"] = role_map.get(email) #roles[role_map.get(email)]
    flask.session["role"] = roles[role_map.get(email)]
    print(f"===>role_map.get(email)={role_map.get(email)}")
    return redirect(url_for("services.services_page"))
