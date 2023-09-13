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

module "gcs" {
  location         = var.gcp_region
  names            = ["${var.gcp_project_id}_cloudfunctions_src"]
  project_id       = var.gcp_project_id
  prefix           = ""
  randomize_suffix = true
  source           = "terraform-google-modules/cloud-storage/google"
  version          = "3.4.0"
  force_destroy = {
    ("${var.gcp_project_id}_cloudfunctions_src") = true
  }
}

module "gcs_conversationHistory" {
  location         = var.gcp_region
  names            = ["${var.gcp_project_id}_conversations"]
  project_id       = var.gcp_project_id
  prefix           = ""
  randomize_suffix = true
  source           = "terraform-google-modules/cloud-storage/google"
  version          = "3.4.0"
  force_destroy = {
    ("${var.gcp_project_id}_conversations") = true
  }
}

module "gcs_documents_storage" {
  location         = var.gcp_region
  names            = ["${var.gcp_project_id}_doc_store"]
  project_id       = var.gcp_project_id
  prefix           = ""
  randomize_suffix = true
  source           = "terraform-google-modules/cloud-storage/google"
  version          = "3.4.0"
  force_destroy = {
    ("${var.gcp_project_id}_doc_store") = true
  }
}

data "archive_file" "index_document" {
  type        = "zip"
  source_dir  = "${path.module}/files/webhooks/index_document/"
  output_path = "/tmp/index_document.zip"
}

resource "google_storage_bucket_object" "index_document" {
  name   = "index_document.zip"
  bucket = module.gcs.name
  source = "/tmp/index_document.zip"
  depends_on = [
    module.gcs,
    data.archive_file.index_document
  ]
}

resource "google_storage_bucket" "embeddings" {
  name          = "${var.gcp_project_id}-embeddings"
  location      = var.gcp_region
  storage_class = "STANDARD"

  uniform_bucket_level_access = true
  depends_on = [
    google_project_service.google-cloud-apis
  ]
}
