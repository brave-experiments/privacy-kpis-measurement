Privacy KPIs Measurement Tools
===

Tools for setting up, tearing down and using a MITM environment
to perform cross browser measurements of HTTP request content.

Requirements
---
* certutil (if you're on linux)
* Xvfb (if you're on linux)

Use
---
*  `sudo ./environment.py` to setup and teardown the MITM environment (installing
certs, configuring MacOS proxy settings, etc.).
*  `./run.py` to actually perform measurements (not sudo).