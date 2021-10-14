# sweden-rent-dashboard
An interactive dashboard built with python that enables you to visualise how rent prices differ across Sweden.

[**The dashboard/web-app generated from this project can be viewed by clicking here**](http://roryc760.pythonanywhere.com/) The dashboard was built to be highly interactive so please do feel free to interact with the figures, dialog buttons, sliders and text inputs. (Unfortunately, the web-app does not render well on mobile devices.)

### Preview of the Dashboard Overview Page  
![SwedenDashBoard](https://user-images.githubusercontent.com/49672044/137277590-e2b84774-b4bd-419c-a866-b79be11eb0ab.gif)


## Code and Resources Used 
* Python Version: 3.8
* Packages Used: pandas, numpy, json, dash, plotly, BeautifulSoup, requests, urllib.request (Those that are required for hosting the web-app can be installed using: pip install -r requirements.txt after cloning the repo).
* Statistical Data: Downloaded from [Statistics Sweden](https://www.statistikdatabasen.scb.se/pxweb/en/ssd/). The median values were used instead of the means as the underlying distribution of each data set is unavailable.
* Web scraping: Performed on various sites including [wiki](https://en.wikipedia.org/wiki/), [Information Sverige](https://www.informationsverige.se/en/mer-om-sverige/boende/lan-och-kommuner-i-sverige/) and [Open Street Map](https://wiki.openstreetmap.org/wiki/). 
* GeoJSON (Map) Data: Obtained from [Open Street Map](https://wiki.openstreetmap.org/) using their [API](http://polygons.openstreetmap.fr/). See section below for further details.


## Repository Layout
#### Main folder
* **app.py**: Used to generate the Plotly/Dash web-app. In order to run this you will need to have run all the below scripts in advance or use the files provided in the "assets" folder in this repo.

* **"get_kommun_county_info.py"**: This script web scrapes from both [wiki](https://en.wikipedia.org/wiki/List_of_municipalities_of_Sweden) and [Information Sverige](https://www.informationsverige.se/en/mer-om-sverige/boende/lan-och-kommuner-i-sverige/) to:
   * Generate a dictionary that states what county ("län" in Swedish) each municipality ("kommun" in Swedish) belongs to.
   * Obtain a short bit of introductory text about each municipality. 
   * Store the web address for each municipality's page on Information Sverige. 

* **"prepare_rent_data.py"**: Takes the 4 Statistics Sweden excel files (these can be found in the "stats" folder) and cleans/reformats them. Outputs are saved as ".csv" files in the "assets" folder and are loaded into the web-app. 

* **"get_geojson_data.py"**: This script first web scrapes relation numbers (like an i.d. number for a map file) for all counties ("län" in Swedish) and municipalities ("kommuner" in Swedish) in Sweden from [Open Street Map](https://wiki.openstreetmap.org/wiki/). The relation numbers are then used to download GeoJSON files from the [OSM database](http://polygons.openstreetmap.fr/) and merged to create maps of Sweden (with borders marked at both the county and municipality levels). The original map files generated from this process ("counties_map.json" and "kommuner_map.json") and they were then "simplified" (resolution decreased) using [mapshaper](https://mapshaper.org/) to improve page loading times on the web-app.

#### Folder: stats
The four ".xlsx" files were obtained directly from [Statistics Sweden](https://www.statistikdatabasen.scb.se/pxweb/en/ssd/) and left unaltered. The file "sources.txt" provides additional information about how exactly these files were obtained.  

#### Folder: assets
These are the resources read in and used by the Plotly/Dash web-app. These were all generated in advance using the scripts described in the main folder. 

## Issues/Comments/Questions
Please feel free to open an issue or pull request if you have any issues/comments/questions or notice something that could be improved. 

