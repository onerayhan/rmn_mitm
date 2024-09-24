output "instance_ip" {
  description = "The public IP of the GCP instance running Selenium and mitmproxy"
  value       = google_compute_instance.selenium_mitm_instance.network_interface[0].access_config[0].nat_ip
}
