import numpy as np
import pandas as pd
import json
import random
import time
from bs4 import BeautifulSoup
import requests
import json

# This script does two things:
# Step 1. Generate a dictionary that states what County each Municiplaity belongs to and store it as a json.
# Done using the table from this  page: https://en.wikipedia.org/wiki/List_of_municipalities_of_Sweden

# Step 2. Obtain a short bit of introductory text for each kommun and a web link to more info. 
# Save both as a json (dict format).   
# Done using the webpages for each kommun available on this page: 
# https://www.informationsverige.se/en/mer-om-sverige/boende/lan-och-kommuner-i-sverige/


# helper function for step 2. 
def get_kommun_info_paragraph(county_kommun_mapping):
    """Given a dict of county and kommun names, extract a paragraph of information about 
    each one from:https://www.informationsverige.se/en/.
    Outputs (1) A dictionary with kommun name as key and value is the paragraph,
    (2) A dictionary with kommun name as key and value is the web link to info page,
    (3) A list of any kommun(er) that failed to be extracted. - No 0 :) """
    url_pre = "https://www.informationsverige.se/en/mer-om-sverige/boende/lan-och-kommuner-i-sverige/"  
    numb_fails = 0 
    fail_list = []
    kommun_urls = {}
    kommuner_info = {}
    awkward_kommuners = ["Bollebygd", "Gothenburg", "Hällefors", "Lilla Edet", 
                         "Upplands Väsby", "Ängelholm", "Östra Göinge"]
    for county, kommunerlist in county_kommun_mapping.items():
        # First need to fix the names to match webadress formatting. 
        if county == "Västra Götaland":
            url_county = "vastra-gotalands"
        elif county not in ["Blekinge", "Kalmar", "Skåne", "Uppsala", "Örebro"]:
            url_county = county.lower()
            url_county += "s"
        else: url_county = county.lower()
            
        for r in (("ä", "a"), ("å", "a"), ("ö", "o")):
            url_county = url_county.replace(*r)
        
        for kommun in kommunerlist:
            # There are 7 special names that don't follow the general patterns below. 
            # They have to be taken care of manually.
            if kommun in awkward_kommuners:
                if kommun == "Bollebygd": url_kommun = "bollebyggd"
                elif kommun == "Gothenburg": url_kommun = "goteborg"
                elif kommun == "Hällefors": url_kommun = "hellefors"
                elif kommun == "Lilla Edet": url_kommun = "lillaedet"
                elif kommun == "Upplands Väsby": url_kommun = "upplandsvasby"
                elif kommun == "Ängelholm": url_kommun = "engelholm"
                elif kommun == "Östra Göinge": url_kommun = "ostragoinge"
    
            else: # the rest can be treated as following a general pattern. 
                url_kommun = kommun.lower()
                for r in (("ä", "a"), ("å", "a"), ("ö", "o")):
                    url_kommun = url_kommun.replace(*r)
            
            # now I can build each url and webscrape 
            url = url_pre + url_county + "-lan/" + url_kommun
            kommun_urls.update({kommun: url}) # save me later. 

            try:
                time.sleep(random.randint(1, 3)) # (random pause to not overload)
                response = requests.get(url)
                soup = BeautifulSoup(response.content, "lxml")
                info_text = (soup.find('p', class_="ingress")).string
                kommuner_info.update({kommun: info_text})
            
            except AttributeError: # if incorrect web address - now 0 fails :) 
                numb_fails += 1
                fail_list.append(kommun)
        
    print(f"Getting webdata Data failed {numb_fails} times.")
    
    return kommuner_info, kommun_urls, fail_list




def main():
    # Step 1. Generate a dictionary that states what County each Municiplaity belongs to and store it as a json. 
    url = 'https://en.wikipedia.org/wiki/List_of_municipalities_of_Sweden'
    df = (pd.read_html(url)[1]) 
    df = df.filter(items=["Municipality", "County"])

    # remove the "County" and "Municipality" part from each name.
    df["Municipality"] = df["Municipality"].str.replace(" Municipality", "") 
    df["County"] = df["County"].str.replace(" County", "") 
    county_municip_dict = {key: [] for key in set(df["County"])}

    for county in set(df["County"]):
        municipality_list = [] 
        municipality_list = list((df[df["County"].isin([county])])["Municipality"])
        county_municip_dict.update({county: municipality_list})
       
    with open("assets/county_kommun_mapping.json", 'w') as outfile:
        json.dump(county_municip_dict, outfile)

    # Step 2. Obtain a short bit of introductory text for each kommun and a web link to more info. 
    # Save both as a json (dict format).  
    kommuner_info, kommuner_urls, fail_list = get_kommun_info_paragraph(county_municip_dict)

    with open("assets/kommun_info_texts.json", 'w') as outfile:
        json.dump(kommuner_info, outfile)

    with open("assets/kommun_urls.json", 'w') as outfile:
        json.dump(kommuner_urls, outfile)



if __name__ == "__main__":
    main()
