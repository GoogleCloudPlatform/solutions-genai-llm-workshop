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
data "google_project" "project" {
  project_id = var.gcp_project_id
}

resource "google_project_service" "google-cloud-apis" {
  project = var.gcp_project_id
  for_each = toset([
    "aiplatform.googleapis.com",
    "servicenetworking.googleapis.com",
    "compute.googleapis.com",
    "bigquery.googleapis.com",
    "run.googleapis.com"
  ])
  disable_dependent_services = true
  disable_on_destroy         = true
  service                    = each.key
}

data "google_compute_default_service_account" "default" {
  project = data.google_project.project.project_id
}

resource "google_project_iam_member" "vertexai_user" {
  project = var.gcp_project_id
  for_each = toset([
    "roles/aiplatform.user",
    "roles/aiplatform.admin",
    "roles/ml.admin",
    "roles/bigquery.dataEditor",
    "roles/bigquery.dataViewer",
    "roles/bigquery.jobUser",
    "roles/storage.objectAdmin",
    "roles/storage.objectViewer",
    "roles/storage.objectCreator"
  ])

  role   = each.key
  member = "serviceAccount:${data.google_compute_default_service_account.default.email}"
  depends_on = [
    google_project_service.google-cloud-apis
  ]
}
