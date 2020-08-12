import base64
import datetime
import json
import sys


class HeaderLogger:
    def __init__(self):
        proxy_args_str = base64.b64decode(sys.argv[-1]).decode("utf-8")
        parent_args = json.loads(proxy_args_str)

        self.requests = []
        self.start_time = datetime.datetime.now()
        self.initial_url = parent_args['url']
        self.log_path = parent_args['log_path']
        self.request_chain = parent_args['request_chain']

    def done(self):
        end_time = datetime.datetime.now()
        complete_log = {
            "start": str(self.start_time),
            "end": str(end_time),
            "url": self.initial_url,
            "request_chain": self.request_chain,
            "requests": self.requests
        }
        with open(self.log_path, "w") as h:
            json.dump(complete_log, h)

    def request(self, flow):
        request_body = ""
        if flow.request.content:
            request_body = str(flow.request.get_text(strict=False))
        request_headers = [(k, v) for k, v in flow.request.headers.items()]
        log_data = {
          "url": flow.request.pretty_url,
          "headers": request_headers,
          "time": str(datetime.datetime.now()),
          "body": request_body,
        }
        self.requests.append(log_data)


addons = [
    HeaderLogger(),
]
