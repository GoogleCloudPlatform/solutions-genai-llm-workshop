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
# Create an IP address
resource "google_compute_global_address" "private_ip_alloc" {
  name          = "private-ip-alloc"
  purpose       = "VPC_PEERING"
  address_type  = "INTERNAL"
  prefix_length = 16
  network       = google_compute_network.llm-vpc.id
}

# Create a private connection
resource "google_service_networking_connection" "servicenetworking" {
  network                 = google_compute_network.llm-vpc.id
  service                 = "servicenetworking.googleapis.com"
  reserved_peering_ranges = [google_compute_global_address.private_ip_alloc.name]
}

# (Optional) Import or export custom routes
resource "google_compute_network_peering_routes_config" "peering_routes" {
  peering = google_service_networking_connection.servicenetworking.peering
  network = google_compute_network.llm-vpc.name

  import_custom_routes = true
  export_custom_routes = true
}