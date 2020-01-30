import pathlib
import sys
from urllib.parse import urlparse

class Args:
  def __init__(self, args):
    self.is_valid = False

    expected_url_parts = ["scheme", "netloc"]
    url_parts = urlparse(args.url)
    for index, part_name in enumerate(expected_url_parts):
      if url_parts[index] == "":
        print("invalid URL, missing a {}".format(part_name), file=sys.stderr)
        return
    self.url = args.url

    if args.case != "safari":
      self.case = args.case
      if not args.profile_path:
        print("no profile path provided", file=sys.stderr)
        return

      self.profile_path = args.profile_path

      if not pathlib.Path(args.binary).is_file():
        print(args.binary + " is not a file", file=sys.stderr)
        return

      self.binary = args.binary

    else: # Safari Case
      self.case = "safari"
      self.profile_path = None
      self.binary = "/Applications/Safari.app"

    self.case = args.case
    self.secs = args.secs
    self.proxy_host = args.proxy_host
    self.proxy_port = str(args.proxy_port)
    self.log = args.log
    self.is_valid = True

  def valid(self):
    return self.is_valid