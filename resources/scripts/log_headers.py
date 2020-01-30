import datetime
import getpass
import json
import os
import pwd
import sys

from mitmproxy import ctx


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

    # It would have been better to just run mitmproxy as a lower privilaged
    # user, instead of running it as root and then changing the ownership
    # afterwards, but mitmproxy crashes if run as non-root w/in root,
    # so here is the hack.
    current_user = getpass.getuser()
    less_privileged_user = os.getlogin()
    if current_user != less_privileged_user:
      less_privileged_user_info = pwd.getpwnam(less_privileged_user)
      less_privileged_uid = less_privileged_user_info.pw_uid
      less_privilaged_gid = less_privileged_user_info.pw_gid
      os.chown(self.log_path, less_privileged_uid, less_privilaged_gid)


  def request(self, flow):
    request_headers = [(k, v) for k, v in flow.request.headers.items()]
    log_data = {
      "url": flow.request.pretty_url,
      "headers": request_headers,
      "time": str(datetime.datetime.now()),
    }
    self.requests.append(log_data)

addons = [
  HeaderLogger(),
]