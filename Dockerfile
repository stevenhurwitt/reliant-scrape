# Start from ubuntu
FROM ubuntu:20.04

# Add python 3.7
FROM python:3.7

# Updating apt to see and install Google Chrome
RUN apt-get -y update \
  && apt-get -y upgrade

# Set display port as an environment variable
ENV DISPLAY=:99

# Make directory & copy
RUN mkdir -p /root/reliant-scrape
WORKDIR /root/reliant-scrape
COPY . /root/reliant-scrape

# chrome & chromedriver
RUN apt-get install -y libglib2.0-0 \
    libfontconfig1 \
    libc6 \
    libnspr4 \
    libsqlite3-0 \
    libnspr4 \
    libgconf-2-4 \
    libnss3-dev \
    libx11-xcb-dev \
    libx11-doc \
    libxcb-doc \
    default-dbus-session-bus \
    chromium \
    chromium-driver \
    unixodbc-dev

# add chromedriver to path
RUN export PATH=$PATH:/usr/bin/chromedriver
RUN chmod +x /usr/bin/chromedriver

#install packages
RUN pip3 install -r /root/reliant-scrape/requirements.txt

# The code to run when container is started:
ENTRYPOINT ["python3", "reliant_scrape.py"]