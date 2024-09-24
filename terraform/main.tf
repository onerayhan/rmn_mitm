provider "google" {
  credentials = file("<path-to-your-service-account-key>.json")
  project     = "<your-gcp-project-id>"
  region      = "us-central1"
}

# Define a VPC
resource "google_compute_network" "vpc_network" {
  name = "selenium-mitm-network"
}

# Define a firewall rule to allow traffic on ports 8080 (for mitmproxy) and 4444 (for Selenium Grid)
resource "google_compute_firewall" "default" {
  name    = "allow-http"
  network = google_compute_network.vpc_network.self_link

  allow {
    protocol = "tcp"
    ports    = ["8080", "4444"]
  }
}

# Create a compute instance
resource "google_compute_instance" "selenium_mitm_instance" {
  name         = "selenium-mitm-instance"
  machine_type = "e2-standard-2"
  zone         = "us-central1-a"

  boot_disk {
    initialize_params {
      image = "debian-cloud/debian-11"
    }
  }

  network_interface {
    network = google_compute_network.vpc_network.self_link

    access_config {
      # This is needed to give the instance a public IP
    }
  }

  metadata_startup_script = <<-EOT
    #! /bin/bash
    # Install Docker
    sudo apt-get update
    sudo apt-get install -y apt-transport-https ca-certificates curl software-properties-common
    curl -fsSL https://download.docker.com/linux/debian/gpg | sudo apt-key add -
    sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/debian $(lsb_release -cs) stable"
    sudo apt-get update
    sudo apt-get install -y docker-ce

    # Start Docker service
    sudo systemctl start docker

    # Run mitmproxy container
    sudo docker run -d --name mitmdump -p 8080:8080 <your-mitmdump-image>

    # Run Selenium container
    sudo docker run -d --name selenium -p 4444:4444 <your-selenium-image>
  EOT

  service_account {
    scopes = ["https://www.googleapis.com/auth/cloud-platform"]
  }

  tags = ["http-server"]
}

# Output instance's public IP address
output "instance_public_ip" {
  value = google_compute_instance.selenium_mitm_instance.network_interface[0].access_config[0].nat_ip
}
