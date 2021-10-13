import numpy as np
import pandas as pd
import json
from urllib.request import urlopen


def get_geojson_map(relation_numbers):
    """Given a list of relation_numbers, extract geojson data for each list member.
    Outputs (1) a single dictionary with map data reformatted to be compatable with plotly. 
    (2) A list of any relation numbers that failed to be extracted. 
    """
    url_geojson_pre = "http://polygons.openstreetmap.fr/get_geojson.py?id="  
    url_geojson_post = "&params=0"
    kommuner_features = [] 
    numb_fails = 0 
    fail_list = []
    for relation in relation_numbers: 
        relation_url = url_geojson_pre + str(relation) + url_geojson_post
        with urlopen(relation_url) as response:
            try:
                coordset = json.load(response) 
                # Reformat coordsets before appending. 
                coordset['type'] = 'Feature' 
                coordset["geometries"] = coordset["geometries"][0] 
                coordset['geometry'] = coordset.pop('geometries')
                coordset["id"] = relation 
                kommuner_features.append(coordset)

            except ValueError: # includes simplejson.decoder.JSONDecodeError
                numb_fails += 1
                fail_list.append(relation)
    print(f"Getting JSON Data failed {numb_fails} times.")

    # Now construct the complete geoJson file. 
    complete_map = {}
    complete_map = {'type': 'FeatureCollection'} # headline for all.
    complete_map['features'] = kommuner_features
    
    return complete_map, fail_list


def main():
    # Grab Kommun and county relation numbers from wiki. 
    # No comments on either page so happy to drop them. 
    url_kommuner = 'https://wiki.openstreetmap.org/wiki/Sweden/Kommuner'
    df_kommuner = (pd.read_html(url_kommuner))[0] # I want 1st table on page
    df_kommuner = df_kommuner.drop(["KommentarComment"], axis=1) 
    df_kommuner = df_kommuner.rename(columns={'KommunMunicipality': 'kommun'})  
    kommuner_relation_nums = df_kommuner["Relation"] 

    url_counties = 'https://wiki.openstreetmap.org/wiki/Sweden/L%C3%A4n'
    df_counties = (pd.read_html(url_counties))[1] # I want 2nd table on page
    drop_list = ['SCB', 'NUTS-1', 'NUTS-2', 'NUTS-3', 'FIPS', 'ISO-3166-2', 'KommentarComment'] 
    df_counties = df_counties.drop(drop_list, axis=1) 
    df_counties = df_counties.rename(columns={'LänCounty': 'county'}) 
    # rename län to county for record matching 
    # (Swedish version of county town names often end with "s")
    df_counties['county'] = df_counties['county'].str.replace('s län', ' county') 
    df_counties['county'] = df_counties['county'].str.replace('län', 'county')

    counties_relations_nums = df_counties["Relation"] 

    counties_map, counties_fail_list = get_geojson_map(counties_relations_nums)
    kommuner_map, kommuner_fail_list = get_geojson_map(kommuner_relation_nums)

    # Remove any that are in the fail_list (thankfully none). 
    df_kommuner = df_kommuner[~df_kommuner.Relation.isin(kommuner_fail_list)]
    df_counties = df_counties[~df_counties.Relation.isin(counties_fail_list)]

    # Write out the dataframes and map files.
    df_kommuner.to_csv("assets/kommuner_list.csv", index=False)
    df_counties.to_csv("assets/counties_list.csv", index=False )
    with open("assets/kommuner_map.json", 'w') as outfile:
        json.dump(kommuner_map, outfile)
    with open("assets/counties_map.json", 'w') as outfile:
        json.dump(counties_map, outfile)

if __name__ == "__main__":
    main()


