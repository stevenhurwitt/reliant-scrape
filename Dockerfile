# Start from ubuntu
FROM ubuntu:20.04

# Add python 3.7
FROM python:3.7

# Adding Google Chrome to the repositories
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add -

RUN sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list'

# Updating apt to see and install Google Chrome
RUN apt-get update \
  && apt-get -y upgrade

# Add to path
RUN export PATH=$PATH:/usr/local/bin/chromedriver

# Set display port as an environment variable
ENV DISPLAY=:99

# Use anaconda environment
FROM continuumio/miniconda3

# Make directory & copy
RUN mkdir -p /root/reliant-scrape
WORKDIR /root/reliant-scrape
COPY . /root/reliant-scrape

RUN cp /root/reliant-scrape/chromedriver /usr/local/bin/

RUN export PATH=$PATH:/usr/local/bin/chromedriver
RUN chmod +x /usr/local/bin/chromedriver

RUN apt-get update

# Extra for chromedriver
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
    default-dbus-session-bus

RUN wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb

RUN dpkg -i google-chrome-stable_current_amd64.deb; apt-get -fy install

# Create the environment:
RUN conda create -n reliant-37

# Make RUN commands use the new environment:
SHELL ["conda", "run", "-n", "reliant-37", "/bin/bash", "-c"]

RUN conda update -y -n base -c defaults conda

RUN conda install -y beautifulsoup4 html5lib numpy pandas pyyaml selenium mysql-connector-python sqlalchemy

# The code to run when container is started:
ENTRYPOINT ["conda", "run", "-n", "reliant-37", "python", "reliant_scrape.py"]
