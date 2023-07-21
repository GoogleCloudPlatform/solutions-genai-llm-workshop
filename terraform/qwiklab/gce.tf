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
resource "google_compute_address" "llm-vpc-static-internal-ip" {
  project      = var.gcp_project_id
  address_type = "INTERNAL"
  subnetwork   = google_compute_network.llm-vpc.id
  name         = "llm-vpc-internal-ip"
  region       = var.gcp_region
  depends_on = [
    google_project_service.google-cloud-apis
  ]
}

resource "google_compute_address" "llm-vpc-static-external-ip" {
  project      = var.gcp_project_id
  address_type = "EXTERNAL"
  name         = "llm-vpc-external-ip"
  region       = var.gcp_region
  depends_on = [
    google_project_service.google-cloud-apis
  ]
}

resource "google_compute_instance" "llm-workshop" {
  #ts:skip=AC_GCP_0041 https://github.com/tenable/terrascan/issues/1084
  project      = var.gcp_project_id
  name         = "llm-workshop"
  machine_type = "e2-standard-4"
  zone         = var.gcp_zone

  boot_disk {
    initialize_params {
      image = "projects/ubuntu-os-cloud/global/images/ubuntu-2004-focal-v20221018"
      size  = 500
    }
  }

  network_interface {
    network    = google_compute_network.llm-vpc.name
    network_ip = google_compute_address.llm-vpc-static-internal-ip.address
    access_config {
      nat_ip = google_compute_address.llm-vpc-static-external-ip.address
    }
  }

  service_account {
    email  = data.google_compute_default_service_account.default.email
    scopes = ["cloud-platform"]
  }

  metadata_startup_script = <<EOL
apt-get update -y
apt install software-properties-common -y
add-apt-repository ppa:deadsnakes/ppa
apt-get update -y
apt install python3.11 -y

curl https://raw.githubusercontent.com/creationix/nvm/552db40622bb7a82d9c6d67d2d6bcf3694b47e30/install.sh | bash
curl -sSL https://raw.githubusercontent.com/python-poetry/install.python-poetry.org/385616cd90816622a087450643fba971d3b46d8c/install-poetry.py | python3 -

  EOL

  depends_on = [
    google_compute_address.llm-vpc-static-internal-ip,
    google_project_service.google-cloud-apis
  ]
}