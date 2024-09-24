import unittest
import requests
from subprocess import Popen, PIPE
import time
import os

class TestMitmProxy(unittest.TestCase):

    def setUp(self):
        # Start mitmproxy in the background
        self.proxy_host = os.getenv("PROXY_HOST", "localhost")
        self.proxy_port = os.getenv("PROXY_PORT", "8080")

    def test_http_request_through_mitmproxy(self):
        # Send an HTTP request through mitmproxy and check the response
        proxies = {
            "http": f"http://{self.proxy_host}:{self.proxy_port}",
            "https": f"http://{self.proxy_host}:{self.proxy_port}"
        }
        response = requests.get('http://example.com', proxies=proxies)
        self.assertEqual(response.status_code, 200)
        print("HTTP Request through mitmproxy successful!")

    def test_https_request_with_certificate(self):
        # Test HTTPS request passing the custom certificate
        cert_path = "/path/to/mitmproxy-ca-cert.pem"
        proxies = {
            "http": f"http://{self.proxy_host}:{self.proxy_port}",
            "https": f"http://{self.proxy_host}:{self.proxy_port}"
        }
        try:
            response = requests.get('https://example.com', proxies=proxies, verify=cert_path)
            self.assertEqual(response.status_code, 200)
            print("HTTPS Request with certificate passed!")
        except requests.exceptions.SSLError as e:
            self.fail(f"SSL verification failed: {e}")

    def tearDown(self):
        # Teardown logic if necessary
        pass

if __name__ == "__main__":
    unittest.main()
