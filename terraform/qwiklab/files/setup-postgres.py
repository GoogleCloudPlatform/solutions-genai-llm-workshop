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

import os

import sqlalchemy
from google.cloud import secretmanager
from google.cloud.sql.connector import Connector

DATABASE_CONNECTION_NAME = os.environ.get("DATABASE_CONNECTION_NAME")
DATABASE_NAME = os.environ.get("DATABASE_NAME", "postgres")
DATABASE_PWD_KEY = os.environ.get("DATABASE_PWD_KEY", "pgvector-password")
DATABASE_USER_NAME = os.environ.get("DATABASE_USER_NAME", "llmuser")
GOOGLE_CLOUD_PROJECT = os.environ.get("GOOGLE_CLOUD_PROJECT", "")


def __get_db_password() -> str:
    if GOOGLE_CLOUD_PROJECT == "":
        raise Exception("PROJECT_ID environment variables must be set")

    client = secretmanager.SecretManagerServiceClient()

    request = secretmanager.AccessSecretVersionRequest(
        name=f"projects/{GOOGLE_CLOUD_PROJECT}/secrets/{DATABASE_PWD_KEY}/versions/latest",  # noqa: E501
    )
    response = client.access_secret_version(request)

    payload = response.payload.data.decode("UTF-8")
    return payload


# initialize Connector object
connector = Connector()


# function to return the database connection object
def getconn():
    conn = connector.connect(
        DATABASE_CONNECTION_NAME,
        "pg8000",
        user=DATABASE_USER_NAME,
        password=__get_db_password(),
        db=DATABASE_NAME,
    )
    return conn


pool = sqlalchemy.create_engine(
    "postgresql+pg8000://",
    creator=getconn,
)

with pool.connect() as db_conn:
    db_conn.execute(sqlalchemy.text("CREATE EXTENSION IF NOT EXISTS vector;"))
    db_conn.commit()
