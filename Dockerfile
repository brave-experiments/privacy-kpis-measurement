FROM ubuntu

ENV DEBIAN_FRONTEND=noninteractive

# Configure apt and install packages
RUN apt-get update \
    && apt-get -y install --no-install-recommends imagemagick less python3 xvfb libnss3-tools sudo chromium-browser firefox 2>&1 \
    && apt-get -y install python3-dev python3-pip libffi-dev libssl-dev 2>&1 \
    && pip3 install mitmproxy xvfbwrapper \
    # Clean up
    && apt-get autoremove -y \
    && apt-get clean -y \
    && rm -rf /var/lib/apt/lists/*

RUN useradd -ms /bin/bash scraper && \
    echo "scraper ALL=(root) NOPASSWD:ALL" > /etc/sudoers.d/scraper && \
    chmod 0440 /etc/sudoers.d/scraper

USER scraper

WORKDIR /home/scraper

COPY --chown=scraper . /app

RUN mkdir /tmp/logs

# Switch back to dialog for any ad-hoc use of apt-get
ENV DEBIAN_FRONTEND=dialog
