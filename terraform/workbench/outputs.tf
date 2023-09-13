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

output "database_private_ip_address" {
  description = "Cloud SQL Private IP Address"
  value = google_sql_database_instance.postgresql.private_ip_address
}

output "database_public_ip_address" {
  description = "Cloud SQL Public IP Address"
  value = google_sql_database_instance.postgresql.public_ip_address
}

output "postgres_instance_connection_name" {
  description = "Cloud SQL PostgreSQL connection instance name"
  value       = "${var.gcp_project_id}:${var.gcp_region}:${google_sql_database_instance.postgresql.name}"
}

output "database_user_name" {
  description = "Database user name"
  value       = google_sql_user.llmuser.name
}

output "database_password_key" {
  description = "Database password key"
  value       = "pgvector-password"
}

output "google-project-id" {
  description = "Google Cloud Porject ID"
  value = var.gcp_project_id
}

output "google-default-region" {
  description = "Default Google Cloud Region"
  value = var.gcp_zone
}

output "gcs_documents_storage_url" {
  description = "Document Store GCS Bucket URL"
  value = module.gcs_documents_storage.url
}