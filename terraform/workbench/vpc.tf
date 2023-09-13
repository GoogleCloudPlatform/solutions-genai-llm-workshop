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
resource "google_compute_network" "llm-vpc" {
  project                 = var.gcp_project_id
  name                    = "llm-vpc"
  auto_create_subnetworks = true
  depends_on = [
    google_project_service.google-cloud-apis
  ]
}

resource "google_compute_router" "llm-vpc-router" {
  name    = "${google_compute_network.llm-vpc.name}-router"
  network = google_compute_network.llm-vpc.id

  bgp {
    asn = 64514
  }
  depends_on = [
    google_compute_network.llm-vpc
  ]
}

resource "google_compute_router_nat" "nat" {
  name                               = "${google_compute_network.llm-vpc.name}-nat"
  router                             = google_compute_router.llm-vpc-router.name
  region                             = google_compute_router.llm-vpc-router.region
  nat_ip_allocate_option             = "AUTO_ONLY"
  source_subnetwork_ip_ranges_to_nat = "ALL_SUBNETWORKS_ALL_IP_RANGES"

  log_config {
    enable = true
    filter = "ERRORS_ONLY"
  }
  depends_on = [
    google_compute_network.llm-vpc
  ]
}

resource "google_compute_firewall" "default-allows-internal" {
  name    = "allow-${google_compute_network.llm-vpc.name}-internal"
  network = google_compute_network.llm-vpc.name
  allow {
    protocol = "tcp"
  }
  allow {
    protocol = "udp"
  }
  allow {
    protocol = "icmp"
  }
  source_ranges = ["10.128.0.0/9"]
  depends_on = [
    google_compute_network.llm-vpc
  ]
}

resource "google_compute_firewall" "default-allows-ssh" {
  name    = "allows-${google_compute_network.llm-vpc.name}-ssh"
  network = google_compute_network.llm-vpc.name

  allow {
    protocol = "tcp"
    ports    = ["22"]
  }
  source_ranges = ["0.0.0.0/0"]
  depends_on = [
    google_compute_network.llm-vpc
  ]
}

resource "google_compute_firewall" "allow-healthcheck" {
  name    = "allows-${google_compute_network.llm-vpc.name}-healthcheck"
  network = google_compute_network.llm-vpc.name
  allow {
    protocol = "tcp"
  }

  source_ranges = ["35.191.0.0/16", "130.211.0.0/22"]
  depends_on = [
    google_compute_network.llm-vpc
  ]
}

resource "google_vpc_access_connector" "connector" {
  name          = "vpcconnector"
  ip_cidr_range = "10.8.200.0/28"
  network       = google_compute_network.llm-vpc.id
  region        = var.gcp_region
}
