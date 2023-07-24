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
import os

from flask import Flask
from routes.auth import auth_bp
from routes.chatbot import chatbot_bp
from routes.predict import predict_bp
from routes.services import services_bp

app = Flask(__name__)

app.secret_key = os.getenv("FLASK_SECRET_KEY")
app.register_blueprint(auth_bp)
app.register_blueprint(services_bp)
app.register_blueprint(predict_bp)
app.register_blueprint(chatbot_bp)

if __name__ == "__main__":
    app.run(debug=True, port=8088, host="0.0.0.0")
