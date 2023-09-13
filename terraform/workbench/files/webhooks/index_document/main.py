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

import functions_framework
from utils_pgvector import index


@functions_framework.cloud_event
def index_document(cloud_event):
    data = cloud_event.data

    event_type = cloud_event["type"]
    print(f"data={data}")
    bucket = data["bucket"]
    name = data["name"].split(sep="/")[-1]
    folder = data["name"].replace(f"/{name}", "")

    if name == folder:
        # No folder in the path
        folder = os.environ.get("DEFAULT_INDEX_NAME", "default")

    print(f"bucket:{bucket} | folder:{folder} | name:{name} | event_type:{event_type}")

    index(bucket=bucket, folder=folder, file_name=name)
