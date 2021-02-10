#!/bin/bash
cd /home/ubuntu/Documents/reliant-scrape
echo changed directory...
source ./reliant/bin/activate
echo activated environment, running script...
python3 -m reliant_scrape
echo finished, goodbye.
