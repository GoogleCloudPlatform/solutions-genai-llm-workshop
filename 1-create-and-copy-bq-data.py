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
from google.cloud import bigquery

client = bigquery.Client()

dataset_id = "{}.chicago_crimes".format(client.project)

dataset = bigquery.Dataset(dataset_id)

dataset.location = "US"

dataset = client.create_dataset(dataset, timeout=30)
print("Created dataset {}.{}".format(client.project, dataset.dataset_id))

table_id = "{}.chicago_crimes.crimes".format(client.project)

orig_table_id = "bigquery-public-data.chicago_crime.crime"

job = client.copy_table(orig_table_id, table_id)
job.result()

dest_table = client.get_table(table_id)
print("Table Copied")
