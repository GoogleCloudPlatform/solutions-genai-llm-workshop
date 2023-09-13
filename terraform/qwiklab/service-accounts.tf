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

# locals {
#   pubsub_svc_account_email                 = "service-${data.google_project.project.number}@gcp-sa-pubsub.iam.gserviceaccount.com"
#   default_compute_engine_svc_account_email = "${data.google_project.project.number}-compute@developer.gserviceaccount.com"
# }

resource "google_project_service_identity" "dialogflow_serviceAgent" {
  provider = google-beta

  project = var.gcp_project_id
  service = "dialogflow.googleapis.com"
}

# resource "google_project_iam_member" "pubsub_service_account_roles" {
#   project = var.gcp_project_id
#   for_each = toset([
#     "roles/iam.serviceAccountTokenCreator",
#     "roles/bigquery.dataEditor"
#   ])
#   role   = each.key
#   member = "serviceAccount:${local.pubsub_svc_account_email}"
#   depends_on = [
#     google_project_service.google-cloud-apis
#   ]
# }

resource "google_project_iam_member" "dialogflow_service_account_roles" {
  project = var.gcp_project_id
  for_each = toset([
    "roles/bigquery.dataEditor"
  ])
  role   = each.key
  member = "serviceAccount:${google_project_service_identity.dialogflow_serviceAgent.email}"
  depends_on = [
    google_project_service.google-cloud-apis,
    google_project_service_identity.dialogflow_serviceAgent
  ]
}

# resource "google_project_iam_member" "default_compute_engine_service_account" {
#   project = var.gcp_project_id
#   for_each = toset([
#     "roles/cloudfunctions.invoker"
#   ])
#   role   = each.key
#   member = "serviceAccount:${local.default_compute_engine_svc_account_email}"
#   depends_on = [
#     google_project_service.google-cloud-apis,
#   ]
# }

resource "google_project_iam_member" "bucket_upload_trigger" {
  project = var.gcp_project_id
  for_each = toset([
    # Invoke Generative AI services
    "roles/aiplatform.user",
    # Invoke Cloud Functions
    "roles/cloudfunctions.invoker",
    # Receive Eventarc events, so the functions can be triggered by file upload
    "roles/eventarc.eventReceiver",
    "roles/eventarc.serviceAgent",
    "roles/iam.serviceAccountUser",
    "roles/logging.logWriter",
    # Able to upload and download conversation logs from GCS
    "roles/storage.objectCreator",
    "roles/storage.objectViewer",
    # Need storage.objects.delete
    "roles/storage.objectAdmin",
    # Able to publish events to Pub/Sub topic
    "roles/pubsub.publisher",
    # For Gen2 cloud functions invoker
    "roles/run.invoker",
    # For Secret Manager
    "roles/secretmanager.secretAccessor",
  ])
  role   = each.key
  member = "serviceAccount:${google_service_account.app_service_account.email}"
  depends_on = [
    google_project_service.google-cloud-apis,
  ]
}

# https://cloud.google.com/eventarc/docs/run/create-trigger-storage-gcloud#before-you-begin
resource "google_project_iam_member" "bucket_upload_trigger_eventReceiver" {
  project = var.gcp_project_id
  for_each = toset([
    "roles/eventarc.eventReceiver",
    "roles/run.invoker",
    "roles/cloudfunctions.invoker",
  ])
  role   = each.key
  member = "serviceAccount:${data.google_project.project.number}-compute@developer.gserviceaccount.com"
  depends_on = [
    google_project_service.google-cloud-apis,
  ]
}


# https://cloud.google.com/eventarc/docs/run/create-trigger-storage-gcloud#before-you-begin
resource "google_project_service_identity" "storage_service_agent" {
  provider = google-beta
  project  = var.gcp_project_id
  service  = "storage.googleapis.com"
  depends_on = [
    google_project_service.google-cloud-apis
  ]
}

resource "google_project_iam_member" "bucket_upload_trigger_publisher" {
  project = var.gcp_project_id
  for_each = toset([
    "roles/pubsub.publisher",
  ])
  role   = each.key
  member = "serviceAccount:service-${data.google_project.project.number}@gs-project-accounts.iam.gserviceaccount.com"
  depends_on = [
    google_project_service.google-cloud-apis,
    google_project_service_identity.storage_service_agent
  ]
}
