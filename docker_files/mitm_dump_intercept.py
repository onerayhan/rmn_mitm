import threading
from mitmproxy import http
import time
import datetime
import pytz
from google.cloud import storage
import os
import logging
from google.cloud import logging as gcloud_logging


# Configure Google Cloud Logging
gcloud_logging_client = gcloud_logging.Client()
logger = gcloud_logging_client.logger("mitmproxy-log")



class InterceptAddon:

    def __init__(self):
        logger.log_text("Initializing InterceptAddon...")
        self.semaphore = threading.Semaphore(0)
        #self.setup_release_semaphore_at_9am()
        self.start_time = None
        self.end_time = None
        self.bucket_name = os.environ.get('GCS_BUCKET_NAME')
        self.data_programarii = os.environ.get('DATA_PROGRAMARII', '2024-11-25')
        self.tip_formular = os.environ.get('TIP_FORMULAR', '4')
        try: 
            self.client = storage.Client()
            self.bucket = self.client.bucket(self.bucket_name)
            self.blob = self.bucket.blob('intercept1_log.txt')
            logger.log_text(f"Connected to Google Cloud Storage bucket: {self.bucket_name}")
        except Exception as e:
            logger.log_text(f"Failed to connect to Google Cloud Storage: {e}", severity="ERROR")

    def setup_release_semaphore_at_9am(self):
        def release_semaphore_at_9am():
            logger.log_text("Setting up semaphore release at 9am...")
            tz = pytz.timezone('Europe/Istanbul')
            now = datetime.datetime.now(tz)
            target_time = now.replace(hour=9, minute=0, second=0, microsecond=0)
            if now > target_time:
                target_time += datetime.timedelta(days=1)
            time_to_wait = (target_time - now).total_seconds() - 5
            if time_to_wait > 0:
                time.sleep(time_to_wait)

            while datetime.datetime.now(tz) < target_time:
                time.sleep(0.01)

            logger.log_text("Semaphore released.")
            self.semaphore.release()

        thread = threading.Thread(target=release_semaphore_at_9am)
        thread.start()

    def write_to_gcs(self, content):
        try:
            logger.log_text("Writing log entry to GCS...") 
            current_content = self.blob.download_as_text()
            new_content = current_content + content
            self.blob.upload_from_string(new_content)
            logger.log_text("Log entry written to GCS.")
        except Exception as e:
            logger.log_text(f"Failed to write log entry to GCS: {e}", severity="ERROR")

    def request(self, flow: http.HTTPFlow) -> None:
        logger.log_text(f"Intercepting request: {flow.request.pretty_url}")
        if "programarecetatenie.eu" in flow.request.pretty_url and "programare_online" in flow.request.path:
            flow.intercept()
            # Modify the request
            if "application/x-www-form-urlencoded" in flow.request.headers.get("Content-Type", ""):
                # flow.request.urlencoded_form["data_programarii"] = "2024-11-25"
                # flow.request.urlencoded_form["tip_formular"] = "4"
                flow.request.urlencoded_form["data_programarii"] = self.data_programarii
                flow.request.urlencoded_form["tip_formular"] = self.tip_formular
                logger.log_text(f"Request modified: data_programarii={self.data_programarii}, tip_formular={self.tip_formular}")

                #time.sleep(5)
                #new_time = datetime.datetime.now().strftime("%a, %d %b %Y %H:%M:%S GMT")
                #flow.request.headers["Date"] = new_time
                #self.semaphore.acquire()
                #print("Request modified to new date and tip_formular")

            # Wait until semaphore is released
            #self.start_time = time.time()  # Start time
            #print("Request sent at the specified time")
            flow.resume()
        


    def response(self, flow: http.HTTPFlow) -> None:
        logger.log_text(f"Intercepting response for: {flow.request.pretty_url}")
        if "programarecetatenie.eu" in flow.request.pretty_url and "programare_online" in flow.request.path:
            # Print the response
            self.end_time = time.time()  # End time

            if self.start_time is not None:
                duration = self.end_time - self.start_time
                log_entry = f"Time between request and response: {duration:.2f} seconds\n"
                log_entry += "Response intercepted:\n"
                log_entry += flow.response.content.decode("utf-8") + "\n\n"
                self.write_to_gcs(log_entry)
                logger.log_text("Response logged.")

addons = [
    InterceptAddon()
]
