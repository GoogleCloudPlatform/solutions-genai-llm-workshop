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

resource "google_cloudfunctions2_function" "index_document" {
  name     = "index_document"
  location = var.google_default_region

  build_config {
    runtime     = "python39"
    entry_point = "index_document"
    source {
      storage_source {
        bucket = module.gcs.name
        object = google_storage_bucket_object.index_document.name
      }
    }
  }
  service_config {
    max_instance_count = 1
    available_memory   = "512M"
    timeout_seconds    = 60
    environment_variables = {
      PROJECT_ID          = var.google_project_id
      GCS_BUCKET          = module.gcs_documents_storage.name
      DATABASE_NAME       = "postgres"
      DATABASE_IP_ADDRESS = google_sql_database_instance.postgresql.private_ip_address
      DATABASE_USER       = google_sql_user.llmuser.name
      DATABASE_PWD_KEY    = "pgvector-password"
      # Default collection / index name
      DEFAULT_INDEX_NAME = "default"
      # https://github.com/langchain-ai/langchain/pull/3964 (512 for TensorFlowEmgedding / 768 for VertexAI Emgedding)
      PGVECTOR_VECTOR_SIZE = 768
    }
    ingress_settings               = "ALLOW_ALL"
    all_traffic_on_latest_revision = true
    service_account_email          = "${var.google_project_id}@appspot.gserviceaccount.com"
    vpc_connector                  = google_vpc_access_connector.connector.id
  }

  event_trigger {
    trigger_region        = var.google_default_region
    event_type            = "google.cloud.storage.object.v1.finalized"
    service_account_email = "${var.google_project_id}@appspot.gserviceaccount.com"
    event_filters {
      attribute = "bucket"
      value     = module.gcs_documents_storage.name
    }
  }

  depends_on = [
    google_project_service.google-cloud-apis,
    google_storage_bucket_object.index_document,
    google_project_service_identity.storage_service_agent,
    google_project_iam_member.bucket_upload_trigger_publisher
  ]
}
