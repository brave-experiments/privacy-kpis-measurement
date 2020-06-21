FROM ubuntu:18.04

ENV DEBIAN_FRONTEND=noninteractive

# https://code.visualstudio.com/docs/remote/containers-advanced#_warning-aptkey-output-should-not-be-parsed-stdout-is-not-a-terminal
ENV APT_KEY_DONT_WARN_ON_DANGEROUS_USAGE=DontWarn

RUN apt-get update \
    # generic/browser stuff
    && apt-get -y install imagemagick less python3 xvfb libnss3-tools sudo chromium-browser firefox apt-transport-https curl gnupg2 ca-certificates 2>&1
    # brave stuff
RUN curl -s https://brave-browser-apt-release.s3.brave.com/brave-core.asc | apt-key --keyring /etc/apt/trusted.gpg.d/brave-browser-release.gpg add - \
    && echo "deb [arch=amd64] https://brave-browser-apt-release.s3.brave.com/ stable main" \
    > /etc/apt/sources.list.d/brave-browser-release.list \
    && apt-get update && apt-get -y install brave-browser \
    ## py3 stuff
    && apt-get -y install python3-dev python3-pip libffi-dev libssl-dev 2>&1 \
    # Clean up
    && apt-get autoremove -y \
    && apt-get clean -y \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /tmp
RUN pip3 install -r /tmp/requirements.txt

RUN useradd -ms /bin/bash scraper && \
    echo "scraper ALL=(root) NOPASSWD:ALL" > /etc/sudoers.d/scraper && \
    chmod 0440 /etc/sudoers.d/scraper

USER scraper

WORKDIR /home/scraper

COPY --chown=scraper . /app

RUN mkdir /tmp/profiles && chown -R scraper /tmp/profiles

# Switch back to dialog for any ad-hoc use of apt-get
ENV DEBIAN_FRONTEND=dialog
