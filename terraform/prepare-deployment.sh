#!/usr/bin/env bash

# Copyright 2023 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

DATABASE_CONNECTION_NAME="$(terraform output -raw postgres_instance_connection_name)"
DATABASE_NAME="postgres"
DATABASE_PWD_KEY="$(terraform output -raw database_password_key)"
DATABASE_USER_NAME="$(terraform output -raw database_user_name)"
GOOGLE_CLOUD_PROJECT="$(terraform output -raw google-project-id)"

export DATABASE_CONNECTION_NAME
export DATABASE_NAME
export DATABASE_PWD_KEY
export DATABASE_USER_NAME
export GOOGLE_CLOUD_PROJECT

python3 -m venv .venv

# shellcheck disable=SC1091
. .venv/bin/activate

pip3 install -r ../requirements.txt

python3 ../setup-postgres.py

echo "Setup complete"
