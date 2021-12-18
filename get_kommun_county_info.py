"""
This script does two things:
1. Generate a dictionary that states what County each Municiplaity
belongs to and store it as a json.

2. Obtain a short bit of introductory text for each Municiplaity
and a web link to more info, saves both as a json.

Terminology Note:
The code in this script uses the Swedish words "kommun"/"kommuner"
(translates to Municipality/Municiplaities in English) for varaiable naming.
County/Counties (and not län/län) are used however.
"""
import json
import random
import time
from typing import Tuple
import pandas as pd
from bs4 import BeautifulSoup
import requests


# helper function for step 2.
def get_kommun_info_paragraph(county_kommun_mapping: dict) -> Tuple[dict, dict, list]:
    """
    Given a dict of county and kommun names, extract a paragraph of information about
    each one from: https://www.informationsverige.se/en/.

    Parameters
    ----------
    county_kommun_mapping : dict
        keys are the county and values are a list of all kommuner that belong to the county.

    Returns
    -------
    kommuner_info : dict
        Municipality/Kommun name as key and value is the paragraph

    kommun_urls : dict
        kommun name as key and value is the web link to info page,

    fail_list : list
        Any kommun(er) that failed to be extracted. - Now 0 :)
    """
    url_pre = "https://www.informationsverige.se/en/jag-har-fatt-uppehallstillstand/boende/lan-och-kommuner-i-sverige/"
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
        else:
            url_county = county.lower()

        for pattern in (("ä", "a"), ("å", "a"), ("ö", "o")):
            url_county = url_county.replace(*pattern)

        for kommun in kommunerlist:
            # There are 7 special names that don't follow the general patterns below.
            # They have to be taken care of manually.
            if kommun in awkward_kommuners:
                if kommun == "Bollebygd":
                    url_kommun = "bollebyggd"
                elif kommun == "Gothenburg":
                    url_kommun = "goteborg"
                elif kommun == "Hällefors":
                    url_kommun = "hellefors"
                elif kommun == "Lilla Edet":
                    url_kommun = "lillaedet"
                elif kommun == "Upplands Väsby":
                    url_kommun = "upplandsvasby"
                elif kommun == "Ängelholm":
                    url_kommun = "engelholm"
                elif kommun == "Östra Göinge":
                    url_kommun = "ostragoinge"

            else:  # the rest can be treated as following a general pattern.
                url_kommun = kommun.lower()
                for pattern in (("ä", "a"), ("å", "a"), ("ö", "o")):
                    url_kommun = url_kommun.replace(*pattern)

            # now I can build each url and webscrape
            url = url_pre + url_county + "-lan/" + url_kommun
            kommun_urls.update({kommun: url})  # save me later.

            try:
                # (random pause to not overload)
                time.sleep(random.randint(1, 3))
                response = requests.get(url)
                soup = BeautifulSoup(response.content, "lxml")
                info_text = (soup.find("p", class_="ingress")).string
                kommuner_info.update({kommun: info_text})

            except AttributeError:  # if incorrect web address - now 0 fails :)
                numb_fails += 1
                fail_list.append(kommun)

    print(f"Getting webdata Data failed {numb_fails} times.")

    return kommuner_info, kommun_urls, fail_list


def main():
    """Obtain County to Municiplaity mappings, then a short bit of
    introductory text for each kommun and a web link to more info."""
    url = "https://en.wikipedia.org/wiki/List_of_municipalities_of_Sweden"
    df_urls = (pd.read_html(url)[1])
    df_urls = df_urls.filter(items=["Municipality", "County"])

    # Standardise names by removing the "County" and "Municipality" part from each name.
    df_urls["Municipality"] = df_urls["Municipality"].str.replace(
        " Municipality", "")
    df_urls["County"] = df_urls["County"].str.replace(" County", "")
    county_municip_dict = {key: [] for key in set(df_urls["County"])}

    for county in set(df_urls["County"]):
        municipality_list = []
        municipality_list = list(
            (df_urls[df_urls["County"].isin([county])])["Municipality"])
        county_municip_dict.update({county: municipality_list})

    with open("assets/county_kommun_mapping.json", "w") as outfile:
        json.dump(county_municip_dict, outfile)

    kommuner_info, kommuner_urls, fail_list = get_kommun_info_paragraph(
        county_municip_dict)

    with open("assets/kommun_info_texts.json", "w") as outfile:
        json.dump(kommuner_info, outfile)

    with open("assets/kommun_urls.json", "w") as outfile:
        json.dump(kommuner_urls, outfile)

    if len(fail_list) >= 1:
        print(f"Failed to get information for: {fail_list}")
    else:
        print("All kommun and county data succefully obtained.")


if __name__ == "__main__":
    main()
