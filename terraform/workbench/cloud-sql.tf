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

resource "google_sql_database_instance" "postgresql" {
  name             = "pgvector-db"
  database_version = "POSTGRES_14"
  region           = var.gcp_region

  settings {
    availability_type = "REGIONAL"
    tier              = "db-custom-2-8192"
    disk_size         = "10"
    disk_type         = "PD_SSD"
    disk_autoresize   = "true"
    ip_configuration {
      ipv4_enabled    = "true"
      private_network = google_compute_network.llm-vpc.id
    }

    database_flags {
      name  = "cloudsql.iam_authentication"
      value = "on"
    }
  }

  depends_on = [google_service_networking_connection.servicenetworking]
}

resource "random_password" "password" {
  length           = 12
  special          = true
  override_special = "!#$%&*()-_=+[]{}<>:?"
}

resource "google_sql_user" "llmuser" {
  name     = "llmuser"
  instance = google_sql_database_instance.postgresql.name
  password = random_password.password.result
}
