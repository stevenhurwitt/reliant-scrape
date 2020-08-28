# reliant-scrape

simple webscrape of daily usage data in python.

## how it works

1. logs into reliant site
2. navigates to account page
3. iterates thru days, cleans & saves data to dataframe
4. writes dataframe to .csv & plots

## setting it up

- conda environment can be created with 

```conda create -f reliant.yml```
- edit the ```config.yaml``` to point to relevant places
    - creds ```json``` is a simple file with ```user``` and ```password``` fields
- run the ```python``` file thru vscode, command line, etc
- use the ```jupyter notebook``` to debug, etc