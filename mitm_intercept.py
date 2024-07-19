import threading
from mitmproxy import http
import time
import datetime
import pytz


class InterceptAddon:

    def __init__(self):
        self.semaphore = threading.Semaphore(0)
        #self.setup_release_semaphore_at_9am()
        self.start_time = None
        self.end_time = None
        self.log_file = "intercept_log.txt"

    def setup_release_semaphore_at_9am(self):
        def release_semaphore_at_9am():
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

            self.semaphore.release()

        thread = threading.Thread(target=release_semaphore_at_9am)
        thread.start()

    def request(self, flow: http.HTTPFlow) -> None:
        if "programarecetatenie.eu" in flow.request.pretty_url and "programare_online" in flow.request.path:
            flow.intercept()
            # Modify the request
            if "application/x-www-form-urlencoded" in flow.request.headers.get("Content-Type", ""):
                flow.request.urlencoded_form["data_programarii"] = "2024-11-19"
                flow.request.urlencoded_form["tip_formular"] = "4"
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
        if "programarecetatenie.eu" in flow.request.pretty_url and "programare_online" in flow.request.path:
            # Print the response
            self.end_time = time.time()  # End time

            if self.start_time is not None:
                duration = self.end_time - self.start_time
                with open(self.log_file, "a") as file:
                    file.write(f"Time between request and response: {duration:.2f} seconds\n")
                    file.write("Response intercepted:\n")
                    file.write(flow.response.content.decode("utf-8") + "\n\n")


addons = [
    InterceptAddon()
]
