import datetime
import json
import sys


class HeaderLogger:
    def __init__(self):
        parent_args = json.loads(sys.argv[-1])
        self.requests = []
        self.start_time = datetime.datetime.now()
        self.initial_url = parent_args['privacy_kpis_url']
        self.log_path = parent_args['privacy_kpis_log']

    def done(self):
        end_time = datetime.datetime.now()
        complete_log = {
            "start": str(self.start_time),
            "end": str(end_time),
            "url": self.initial_url,
            "requests": self.requests
        }
        with open(self.log_path, "w") as h:
            json.dump(complete_log, h)

    def request(self, flow):
        request_headers = [(k, v) for k, v in flow.request.headers.items()]
        log_data = {
          "url": flow.request.pretty_url,
          "headers": request_headers,
          "time": str(datetime.datetime.now()),
          "body": flow.request.content,
        }
        self.requests.append(log_data)


addons = [
    HeaderLogger(),
]
