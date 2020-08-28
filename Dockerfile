# Start from ubuntu
FROM ubuntu:20.04

# Update repos and install dependencies
RUN apt-get update \
  && apt-get -y upgrade

# Add python 3.8
FROM python:3.8

# Adding trusting keys to apt for repositories
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add -

# Adding Google Chrome to the repositories
RUN sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list'

# Updating apt to see and install Google Chrome
RUN apt-get -y update

RUN apt-get -y upgrade

# Magic happens
RUN apt-get install -y google-chrome-stable \
    chromium

# Extra for chromedriver
RUN apt-get install -y libglib2.0-0 \
    libgconf-2-4 \
    libfontconfig1

RUN apt-get install -y libnspr4 libnss3 libnss3-tools

# Installing Unzip
RUN apt-get install -yqq unzip

# Download the Chrome Driver
RUN wget -O /tmp/chromedriver.zip http://chromedriver.storage.googleapis.com/`curl -sS chromedriver.storage.googleapis.com/LATEST_RELEASE`/chromedriver_linux64.zip

# Unzip the Chrome Driver into /usr/local/bin directory
RUN unzip /tmp/chromedriver.zip chromedriver -d /usr/local/bin/

RUN chmod +x /usr/local/bin/chromedriver

RUN ln -s /usr/local/bin/chromedriver /usr/bin

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

RUN export PATH=$PATH:/root/reliant-scrape/chromedriver
RUN chmod +x /root/reliant-scrape/chromedriver

# Create the environment:
RUN conda create -n reliant

# Make RUN commands use the new environment:
SHELL ["conda", "run", "-n", "reliant", "/bin/bash", "-c"]

RUN /root/reliant-scrape/chromedriver --version
#RUN conda update -y -n base -c defaults conda

#RUN conda install -y beautifulsoup4 html5lib numpy pandas pyyaml selenium

# The code to run when container is started:
#ENTRYPOINT ["conda", "run", "-n", "reliant", "python", "reliant_scrape.py"]