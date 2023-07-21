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
import importlib

import flask
from flask import Blueprint, jsonify, request

predict_bp = Blueprint("predict", __name__)


def do_predict(query: str) -> str:
    import requests

    response = requests.post(
        f"{request.scheme}://{request.host}/predict?model=web_search", json=query
    )

    if response.status_code == 200:
        result = response.json()
        return result
    else:
        print("Error:", response.text)
        raise Exception(response.text)


@predict_bp.route("/predict", methods=["POST"])
def predict():
    json_payload = request.get_json()
    print(f"***** json_payload={json_payload}")

    model = request.args.get("model")
    print(f"***** model={model}")
    try:
        print("***** importlib.import_module")
        module = importlib.import_module("models." + model)
        print("***** calling predict_fn")
        predict_fn = getattr(module, "predict")
    except ModuleNotFoundError:
        return flask.Response(response="ModuleNotFoundError", status=404)

    # try:
    # Get the HTTP POST body as JSON
    json_payload = request.get_json()
    # Extract the message property from the JSON payload
    message = json_payload

    # Call the predict() function with the message property
    prediction = predict_fn(query=message)
    # Return the prediction as a JSON response with a 200 OK status code.
    return jsonify(prediction)
    # except Exception as e:
    #   print("*** Exception when running /predict"+str(e))
    #   return flask.Response(response=str(e),status=500)
