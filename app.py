# -*- coding: utf-8 -*-

# Run this app with: "python app.py"
# Then visit: http://127.0.0.1:8050/ in your web browser. 
import pandas as pd
import numpy as np 
import json
import plotly.express as px
import plotly.graph_objects as go
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
from dash_bootstrap_templates import load_figure_template
from dash.exceptions import PreventUpdate



####################################################################
######################### Part0 - Style Selection ##################
####################################################################

# https://hellodash.pythonanywhere.com/theme_explorer 
# Since we're adding callbacks to elements that don"t exist in the initial app.layout, 
# we need suppress_callback_exceptions=True.
app = dash.Dash(
    __name__, 
    external_stylesheets=[dbc.themes.CERULEAN], suppress_callback_exceptions=True,
    # these meta_tags ensure content is scaled correctly on different devices
    # see: https://www.w3schools.com/css/css_rwd_viewport.asp for more
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],
)

banner_color = {"background-color": "#DEDEDE"}

content_style = {"margin-left": "2rem", "margin-right": "2rem", "margin-top": "0.5rem"}

# colour scheme for violin plots. 
violin_colors = ["lightseagreen", "green", "goldenrod", "magenta", "mediumpurple", "red"]

# horizontal rule styles. 
hr_styles = {"v1": {"border":"2px lightgray solid"}, "v2": {"border":"1px lightgray solid"}, "v3": {"border":"0.5px lightgray solid"}}



####################################################################
################### Part1 - All Big Text Blocks ####################
####################################################################

################ random extras. ################
sidebar_text = "An interactive dashboard built with python that enables you to visualise how rent prices differ across Sweden."

graph_title_1 = html.H5(["Median Annual Rent per m", html.Sup(2), " (SEK)"], className="text-center")

################ overview page text ################
overview_page_text = html.P(["The bar graph and choropleth map shown below depict the median annual cost to rent an apartment per square meter (m",
    html.Sup(2), "). You can use the dialog buttons above to switch the view from the municipality perspective to the county perspective. ",
    "Fun Fact: The word for municipality is \"kommun\" in swedish (or \"kommuner\" in the plural form). ", 
    "The word for county in Swedish is \"län\" in both the singular and plural form.",
])

card_body_title_kommun = html.H5("The Top 10 Most and Least Expensive Municipalities to Rent in.", className="text-center")
card_body_text_kommun = html.P([
    html.Li("Of the ten most expensive municipalities, only two (Lomma in 6th and Uppsala in 10th) are not located in Stockholm county."),
    html.Li("Vallentuna is now the most expensive municipality to rent in (last year it was Täby Municipality), with it's median annual rent per square meter increasing by over 20% in the last year alone."),
])

card_body_title_county = html.H5("Differences in Median Annual Rent per Square Meter For All 21 Counties (län).", className="text-center")
card_body_text_county = html.P([
])

# Define rent increase and inflation calculation method.  - overview page. 
rent_increase_explain_p1 = html.P(["Rent price increases are the change (normally an increase) in annual rent per sqaure meter that a current tenant has to pay for the same propety, usually starting from January. ",
    "Inflation was accounted for using the annual Consumer Price Index (CPI) published by ",
    html.A("Statistics Sweden", 
        href="https://www.scb.se/en/finding-statistics/statistics-by-subject-area/prices-and-consumption/consumer-price-index/consumer-price-index-cpi/pong/tables-and-graphs/consumer-price-index-cpi/cpi-fixed-index-numbers-1980100", target="_blank"),
    ". The base year is set to 2016, meaning the values for 2016 remain unchanged whilst all other years refer back to 2016 levels)."
])

rent_increase_explain_p2 = html.P([
    html.B("Please note that for a fairer comparison between the years, only municipalities with complete data across 2016-2021 are included (222 of the 290 municipalities). "),
        "The below graph combines a scatter plot (of each municipality's value for each year - which you can hover on), and a \"violin plot\". " ,
        "Violin plots are a way to show the distribution of rent prices for each year. Roughly speaking, the thicker the violin at a given price point, the more common/frequent that value is.",
])


################ rent_vs_time page text ################
rent_vs_time_info_text = html.P([
    "The map below allows you to compare how rent prices have changed over recent years (2016-2021). ", 
    "Values shown are the same as those in the overview page (Annual rent per m", html.Sup(2), 
    "). You can also choose whether to study the map at the municipality or county perspective. ",
    "Further, if you can click on the map, you can study how prices have changed for a specific region in more detail.",
])


################ FAQ page text ################
faq_title_1 = "What is This Website and Why Did You Make it?"
faq_text_1 = html.P([
    "This website allows you to compare and contrast how rent prices differ across Sweden ",
    "and how those prices have changed in recent years. ",
    "The app and graphs themselves are quite interactive, so please feel free to hover/click away!", 
    html.Br(), html.Br(),
    "I built this app primarily to improve my python programming and dashboarding skills. ",
    "If you would like to see the python code used to extract, prepare, and ultimately present the data shown on this website, ",
    "please feel free to visit the ",
    html.A("Github repository", href="https://github.com/RMCrean/sweden-rent-dashboard", target="_blank"),
    ".",
])  

faq_title_2 = "How Did You Obtain This Data?"
faq_text_2 = html.P([
    "All data presented here was taken from the ",
    html.A("Statistics Sweden website", href="https://www.scb.se/", target="_blank"),
    ". In all cases I chose to present the median values as opposed to the means. ",
    "This is because I was unable to look at the underlying distributions for each data set, and ",
    "the general rule is that you should only use the mean if you know your data is normally distributed. ", 
    html.Br(), html.Br(),
    "The coordinates needed to generate the choropleth maps (i.e. the coloured maps) of Sweden ",
    "were obtained from ",
    html.A("Open Street Map", href="https://www.openstreetmap.org/", target="_blank"),
    ". To help reduce the loading times for this website, I reduced the resolutions of the map files using ",
    html.A("Mapshaper", href="https://mapshaper.org/", target="_blank"),
    ". ",
])  

faq_title_3 = "Why is Some Data Missing?"
faq_text_3 = html.P([
    "Unfortunately it is true that some municipalities have missing data, especially in the case of the earlier years. ",
    "I'm afraid I do not have control over this as all available data was taken from the ",
    html.A("Statistics Sweden website", href="https://www.scb.se/", target="_blank"),
    ". ",
])  

faq_title_4 = "How Was This Website Built?"
faq_text_4 = html.P([
    "The web application itself was built with the open-source version of ",
    html.A("Ploty-Dash", href="https://plotly.com/dash/", target="_blank"),
    " in python (with a little HTML and CSS where necessary). To host this website I used the free service provided by ",
    html.A("PythonAnywhere", href="https://www.pythonanywhere.com/", target="_blank"),
    ". ",
]) 

faq_title_5 = "What is a Municipality and/or County?"
faq_text_5 = html.P([
    "Sweden is divided up into 21 Counties or 'län' in Swedish. ",
    "Each County contains several Municipalities (\"kommuner\" in Swedish). ",
    "There are 290 Municipalities in Sweden in total and each municipality will charge a municipal tax ",
    "which is used to fund (among other things) schools, social services and libraries. ",
]) 

faq_title_6 = "I Have a Comment/Suggestion/Issue"
faq_text_6 = html.P([
    "All comments, suggestions, issues etc... are very welcome on the app's ", 
    html.A("Github repository", href="https://github.com/RMCrean/sweden-rent-dashboard", target="_blank"),
    ". You can also contact me via ", 
    html.A("LinkedIn", href="https://www.linkedin.com/in/rory-crean/", target="_blank"),
    " if you prefer. Thank you for taking a look at my web app."
]) 



####################################################################
###################### Part2 - Data Preperation ####################
####################################################################

# Read in the prepared dfs, dicts and simplified maps (made with mapshaper)
dfs = {}
dfs["rent_kommun"] = pd.read_csv("assets/median_rent_kommuner_cleaned.csv")
dfs["rent_county"] =  pd.read_csv("assets/median_rent_counties_cleaned.csv")
dfs["new_rent_kommun"] = pd.read_csv("assets/median_new_rent_kommuner_cleaned.csv")
dfs["new_rent_county"] = pd.read_csv("assets/median_new_rent_counties_cleaned.csv")

with open("assets/kommuner_map_low_res.json") as infile:
    kommuner_map = json.load(infile)
with open("assets/counties_map_low_res.json") as infile:
    counties_map = json.load(infile)

with open("assets/county_kommun_mapping.json","r") as json_file:
    county_kommun_mapping = json.load(json_file)
with open("assets/kommun_info_texts.json","r") as json_file:
    kommun_info_texts = json.load(json_file)
with open("assets/kommun_urls.json","r") as json_file:
    kommun_urls = json.load(json_file)


################ Data prep for overview page ################
# Define Top 10 most expensive and least expensive kommuner to live in. 
kommun_bar_df = dfs["rent_kommun"][dfs["rent_kommun"]["Year"].apply(lambda x : x == 2021)]
kommun_bar_df = kommun_bar_df[~(kommun_bar_df["Median Rent (SEK)"] <= 0)]  # remove missing values
kommun_bar_df = kommun_bar_df.sort_values(by=["Median Rent (SEK)"], ascending=True, ignore_index=True)
kommun_bar_df = kommun_bar_df.iloc[np.r_[0:10, -10:0]] # filter for plotting. 

# As there are 21 counties, show all on the bar graph but sort them first.  
county_bar_df = dfs["rent_county"][dfs["rent_county"]["Year"].apply(lambda x : x == 2021)]
county_bar_df = county_bar_df[~(county_bar_df["Median Rent (SEK)"] <= 0)]  # remove missing values
county_bar_df = county_bar_df.sort_values(by=["Median Rent (SEK)"], ascending=True, ignore_index=True)
county_bar_df["county"] = county_bar_df["county"].str.replace(" county", "")

# Taken from: https://www.scb.se/en/finding-statistics/statistics-by-subject-area/prices-and-consumption/consumer-price-index/consumer-price-index-cpi/pong/tables-and-graphs/consumer-price-index-cpi/cpi-fixed-index-numbers-1980100/
# For 2021, the average from Jan to Aug was used (only data available at the time). 
cpi_rates = {"2016": 316.43, "2017": 322.11, "2018": 328.40, "2019": 334.26, "2020": 335.92, "2021": 340.70}

def inflation_adjust(x, year):
    """Adjust values for inflation, with 2016 set as the base year. 
    Inputs are (1) "x", value to inflate/deflate and 
    (2) "year" of the value. "year" can only be in range 2016-2021. 
    "cpi_rates" dictionary taken from Statistics Sweden"s official CPI rate."""
    if year == 2016:
        adj_value = (x * cpi_rates["2016"]) / cpi_rates["2016"]
    elif year == 2017:
        adj_value = (x * cpi_rates["2017"]) / cpi_rates["2016"]
    elif year == 2018:
        adj_value = (x * cpi_rates["2018"]) / cpi_rates["2016"]
    elif year == 2019:
        adj_value = (x * cpi_rates["2019"]) / cpi_rates["2016"]
    elif year == 2020:
        adj_value = (x * cpi_rates["2020"]) / cpi_rates["2016"]
    elif year == 2021:
        adj_value = (x * cpi_rates["2021"]) / cpi_rates["2016"]
    else: 
        raise ValueError("year parameter can only be within the range 2016-2021.")
    return adj_value


################ Data prep for specifics page ################
# (unravels each sublist item into one long list)
all_kommuner = [item for sublist in county_kommun_mapping.values() for item in sublist] 
kommun_options = [{"label": x, "value": x} for x in all_kommuner]

def get_key(val, my_dict):
    """Little helper function to return the "key" i.e. the county name for a given kommum.
    Note that the "value" from the dict is a list of all kommun names in the county."""
    for key, value in my_dict.items():
        if val in value:
            return key
    return "key doesn't exist"


####################################################################
######################### Part3 - Layout ###########################
####################################################################

# Banner part of page - same for all webpages. 
page_banner = [
    dbc.Row([
        dbc.Col([
            html.H2("How Much?", className="display-4" ),
        ], xs=6, sm=5, md=4, lg=3, xl=3),

        dbc.Col([
            dbc.Nav(
                [
                    dbc.NavLink("Overview", href="/", active="exact", style={"font-size": "18px"}),
                    dbc.NavLink("How Have Rent Prices Changed in Recent Years?", href="/rent_prices_vs_time", active="exact", style={"font-size": "18px"}),
                    dbc.NavLink("Focus on a Specific Municipality of your Choice", href="/rent_price_specifics", active="exact", style={"font-size": "18px"}),
                    dbc.NavLink("FAQs", href="/FAQs", active="exact", style={"font-size": "18px"}), 
                ],
                pills=True,
            ),
        ], style={"textAlign":"right"}, xs=6, sm=7, md=8, lg=9, xl=9, className="mr-auto"),
    ], style=banner_color),

    dbc.Row([
        html.P(sidebar_text, className="lead"),
        html.Hr(style=hr_styles["v2"]), 
        html.Br(), html.Br(), 
    ], style=banner_color), 
]


# blank content with central layout defined by the callbacks. 
content = html.Div(id="page-content", children=[], style=content_style)

app.layout = dbc.Container([
    dcc.Location(id="url"),
    content
], fluid=True)


# The overview page. 
rent_prices_overview = [ 
    page_banner[0],
    page_banner[1],
    html.Br(),
    html.H4("An Overview of Current Rent Prices Throughout Sweden (As of January 2021).", style={"textAlign":"center"}),
    html.Hr(style=hr_styles["v2"]),
    
    # 1st row
    dbc.Row([
        dbc.Col([
            dbc.RadioItems(
                options=[
                        {"label": "Compare By Municipality (kommun)", "value": "kommun_view"},
                        {"label": "Compare By County (län)", "value": "county_view"},
                ],
                value="kommun_view", id="county-kommun-radio-overview-page", inline=True,
                style={"font-size": "18px"}, className="text-center"
            ),
        ], xs=11, sm=11, md=11, lg=10, xl=10, className="mb-2"),
    ], justify="center"),

    # 2nd row
    dbc.Row([
        html.P(overview_page_text),
    ]),

    # 3rd row 
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody(children=[], id="card-body-overview", className="text-center" "card-title"),
            ]),
        ], xs=12, sm=12, md=12, lg=6, xl=6, className="mb-2"),

        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    graph_title_1,
                    dcc.Graph(id="map-overview", figure = {})
                ]),
            ]),    
        ], xs=12, sm=12, md=12, lg=6, xl=6, className="mb-2"),
    ], justify="center"),

    # 4th row
    dbc.Row([
        dbc.Col([
            html.Br(),
            html.Br(),
            html.H4("Distribution of Yearly Increases in Median Rent Throughout Sweden", style={"textAlign": "center"}),
            rent_increase_explain_p1,
            html.Hr(),
        ], className="mb-2"),
    ]),

    # 5th row. 
    dbc.Row([
        dbc.Col([
            dbc.RadioItems(
                options=[
                        {"label": "Adjust Prices for Inflation", "value": "inflation_on"},
                        {"label": "Show Original Values", "value": "inflation_off"},
                ],
                value="inflation_on", id="inflation-toggle-overview", inline=True,
                style={"font-size": "18px"}, className="text-center"
            ),
        ], className="mb-2"),
    ]),

    # 6th row. 
    dbc.Row([
        dbc.Col([
            html.H5("Median Annual Rent Increase per square meter Across Sweden's Municipalities", style={"textAlign": "left"}),
            rent_increase_explain_p2,
            dcc.Graph(id="boxplot-increases-overview", figure = {})
        ], className="mb-2"),
    ]),

    # 7th row. 
    dbc.Row([
        dbc.Col([
            html.H5("Median Annual Rent Increase per square meter Across Sweden's Counties", style={"textAlign": "left"}),
            dcc.Graph(id="scatter-increases-overview", figure = {})
        ], className="mb-2"),
    ]),

]


# The page which presents changing rent prices on the map. 
rent_prices_vs_time = [ 
    page_banner[0],
    page_banner[1],
    html.Br(),

    html.H4("How Have Rent Prices Changed Across Sweden in Recent Years?", style={"textAlign":"center"}),
    html.Hr(style=hr_styles["v2"]),
    
    html.P(rent_vs_time_info_text),
    # 1st row
    dbc.Row([
        dbc.Col([
            dbc.RadioItems(
                options=[
                        {"label": "Compare By Municipality (kommun)", "value": "kommun_view"},
                        {"label": "Compare By County (län)", "value": "county_view"},
                ],
                value="kommun_view", id="county-kommun-radio-vs-time-page", inline=True,
                style={"font-size": "18px"}, className="text-center"
            ),
        ], className="mb-2"),
    ]),

    # 2nd row
    dbc.Row([
        dbc.Col([
            dcc.Slider(
                min=2016, max=2021, step=1, value=2021, id="year-slider",
                marks={
                    2016: {"label": "2016", "style": {"font-size": "18px"}}, 
                    2017: {"label": "2017", "style": {"font-size": "18px"}},  
                    2018: {"label": "2018", "style": {"font-size": "18px"}}, 
                    2019: {"label": "2019", "style": {"font-size": "18px"}}, 
                    2020: {"label": "2020", "style": {"font-size": "18px"}}, 
                    2021: {"label": "2021", "style": {"font-size": "18px"}}, 
                }, 
            )
        ], width={"size": 8, "offset": 2}, className="mb-2"),
    ]),
    
    # 3rd row
    dbc.Row([

        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    graph_title_1,
                    dcc.Graph(id="rent-choropleth-fig", figure = {})
                ]),
            ]), 
        ], xs=12, sm=12, md=12, lg=6, xl=6, className="mb-2"),      

        dbc.Col([
            dbc.Card(id="rent-info-card",
                children=[
                    dbc.CardBody([
                        html.H5("Click on any region on the Map to populate this box!", className="card-title text-center"),
                        html.Br(), html.Br(), html.Br(), html.Br(), html.Br(), html.Br(), html.Br(), html.Br(), html.Br(), html.Br(), html.Br(), html.Br(),
                        html.Br(), html.Br(), html.Br(), html.Br(), html.Br(), html.Br(), html.Br(), html.Br(), html.Br(), html.Br(), html.Br(), html.Br(),
                    ]),
                ]
            ),
        ], xs=12, sm=12, md=12, lg=6, xl=6, className="mb-2"),
    ]),

]


# The page which allows users to specificy a kommun and study it in more detail. 
rent_price_specifics = [
    page_banner[0],
    page_banner[1],
    html.Br(),

    html.H4("View Specific Details about a Municipality of Your Choice", style={"textAlign":"center"}),
    html.Hr(style=hr_styles["v2"]),
    
    # 1st row 
    dbc.Row([
        dbc.Col([
            html.H5("Select a Municipality to Study in More Detail:"), 
            dcc.Dropdown(
                id="dropdown-kommun-select", multi=False, value="Örnsköldsvik",
                placeholder="Örnsköldsvik is currently selected, start typing to change to a different Municipality...",
            ),
        ], style={"font-size": "16x", "justify-content": "left"}, className="mb-2"), 
    ]), 

    # 2nd row
    dbc.Row([
        html.Br(),
    ]),

    # 3rd row 
    dbc.Row([
        dbc.Col([], id="kommun-specific-info-text", xs=12, sm=12, md=8, lg=8, xl=8, className="mb-2"),
        dbc.Col([], id="kommun-specific-map", xs=12, sm=12, md=4, lg=4, xl=4, className="mb-2"),
    ]), 

    # 4th row 
    dbc.Row([
        dbc.Col([], id="kommun-specific-to-county", xs=12, sm=12, md=12, lg=12, xl=12, className="mb-2"),
    ]), 

    # 5th row 
    dbc.Row([
        dbc.Col([], id="kommun-specific-median-bar", xs=12, sm=12, md=6, lg=6, xl=6, className="mb-2"),
        dbc.Col([], id="kommun-specific-increase-bar", xs=12, sm=12, md=6, lg=6, xl=6, className="mb-2"),
    ]), 

]



# FAQs page. 
FAQs_page_layout = [
    page_banner[0],
    page_banner[1],
    html.Br(),

    html.H4("Frequently asked questions (FAQs)", style={"textAlign":"center"}),
    html.Hr(style=hr_styles["v2"]),

    dbc.Col([
        dbc.Card([
            dbc.CardBody([
                html.H5(faq_title_1),
                html.Hr(style=hr_styles["v3"]),
                html.P(faq_text_1),
            ]),
        ], color="primary", outline=True),    
    ], width=12, className="mb-2"),

    dbc.Col([
        dbc.Card([
            dbc.CardBody([
                html.H5(faq_title_2),
                html.Hr(style=hr_styles["v3"]),
                html.P(faq_text_2),
            ]),
        ], color="primary", outline=True),    
    ], width=12, className="mb-2"),

    dbc.Col([
        dbc.Card([
            dbc.CardBody([
                html.H5(faq_title_3),
                html.Hr(style=hr_styles["v3"]),
                html.P(faq_text_3),
            ]),
        ], color="primary", outline=True),    
    ], width=12, className="mb-2"),

    dbc.Col([
        dbc.Card([
            dbc.CardBody([
                html.H5(faq_title_4),
                html.Hr(style=hr_styles["v3"]),
                html.P(faq_text_4),
            ]),
        ], color="primary", outline=True),    
    ], width=12, className="mb-2"),

    dbc.Col([
        dbc.Card([
            dbc.CardBody([
                html.H5(faq_title_5),
                html.Hr(style=hr_styles["v3"]),
                html.P(faq_text_5),
            ]),
        ], color="primary", outline=True),    
    ], width=12, className="mb-2"),

    dbc.Col([
        dbc.Card([
            dbc.CardBody([
                html.H5(faq_title_6),
                html.Hr(style=hr_styles["v3"]),
                html.P(faq_text_6),
            ]),
        ], color="primary", outline=True),    
    ], width=12, className="mb-2"),

]



####################################################################
######################### Part 4 - Callbacks #######################
####################################################################

# callback to move user to the correct page. 
@app.callback(
    Output("page-content", "children"),
    Input("url", "pathname")
)
def define_location(pathname):
    if pathname == "/":
        return rent_prices_overview

    elif pathname == "/rent_prices_vs_time":
        return rent_prices_vs_time

    elif pathname == "/rent_price_specifics":
        return rent_price_specifics

    elif pathname == "/FAQs":
        return FAQs_page_layout

    # If the user tries to reach a different page, return a 404 message
    else: 
        return dbc.Jumbotron([
            html.H1("404: Not found", className="text-danger"),
            html.Hr(style=hr_styles["v1"]),
            html.P(f"The pathname {pathname} was not recognised..."),
            ])


##################### rent_prices_overview callbacks ########################### 

# Callback to modify rent_prices_overview page format. 
@app.callback(
    [
    Output("card-body-overview", "children"),
    Output("map-overview", "figure")
    ],
    Input("county-kommun-radio-overview-page", "value"),
)
def render_overview_page(kommun_or_county):
    
    if kommun_or_county == "kommun_view":
        card_body_title = card_body_title_kommun
        card_body_text = card_body_text_kommun 

        fig = px.bar(kommun_bar_df, x="Median Rent (SEK)", y="kommun", orientation="h", 
            color="Median Rent (SEK)", color_continuous_scale="ylgnbu") 
        fig.add_hline(y=9.5, line_width=3, line_dash="dash", line_color="black")
        fig.update_xaxes(range=[0, 1850])

        # now choropleth map
        choro_df = dfs["rent_kommun"][(dfs["rent_kommun"]["Year"] == 2021)] 
        choro_map = px.choropleth_mapbox(choro_df, geojson = kommuner_map, 
            locations = "Relation", featureidkey = "id", opacity=0.8, height=800,
            color = "Median Rent (SEK)", color_continuous_scale="ylgnbu", 
            range_color=[700, 1850],
            hover_data = {"kommun":True, "Relation":False, "Year":False,
                "Median Rent (SEK)":False, "Map Label":True},
        )

        choro_map.update_geos(fitbounds="locations", visible=False)
        customdata = choro_df
        choro_map.update_traces(hovertemplate="<b>%{customdata[0]} </b><br><br>%{customdata[4]}<extra></extra>") 

    elif kommun_or_county == "county_view":
        card_body_title = card_body_title_county
        card_body_text = card_body_text_county

        fig = px.bar(county_bar_df, x="Median Rent (SEK)", y="county", orientation="h", 
            color="Median Rent (SEK)", color_continuous_scale="ylgnbu") 

        # now choropleth map
        choro_df = dfs["rent_county"][(dfs["rent_county"]["Year"] == 2021)] 
        choro_map = px.choropleth_mapbox(choro_df, geojson = counties_map, 
            locations = "Relation", featureidkey = "id", opacity=0.8, height=800, 
            color = "Median Rent (SEK)", color_continuous_scale="ylgnbu",
            hover_data = {"county":True, "Relation":False, "Year":False,
                "Median Rent (SEK)":False, "Map Label":True},
        )
        choro_map.update_geos(fitbounds="locations", visible=False)
        customdata = choro_df
        choro_map.update_traces(hovertemplate="<b>%{customdata[0]} </b><br><br>%{customdata[4]}<extra></extra>") 

    # Shared between both "kommun_view" and "county_view". 
    fig.update_layout(
        xaxis=dict(title="Median Rent per M<sup>2</sup> (SEK)", titlefont_size=18, tickfont_size=14),
        yaxis=dict(title="",  tickfont_size=14), margin={"r":0,"t":30,"l":0,"b":0},
    )
    fig.update_traces(marker_line_color="black", marker_line_width=1.5, opacity=0.6)
    fig.update_layout(coloraxis_showscale=False)

    choro_map.update_layout(
        legend=dict(bgcolor="rgba(0,0,0,0)", title="Median Cost per M<sup>2</sup> (SEK)", yanchor="top", xanchor="left",
            x=0.01, y=0.80, font=dict(size=16, color="black")
        ),
        margin={"r":0,"t":20,"l":0,"b":0}, mapbox_center = {"lat": 62.90, "lon": 16.00},
        mapbox_style="white-bg", mapbox_zoom=4.1, plot_bgcolor = "lightgray",
    )

    # finally build the card_body
    card_body = ([
        card_body_title,
        dcc.Graph(id="bar-top10s-overview", figure = fig),
        html.Br(),
        card_body_text,
    ])

    return card_body, choro_map


# Callback to update graphs with correction for inflation or not. 
@app.callback(
    [
    Output("boxplot-increases-overview", "figure"),
    Output("scatter-increases-overview", "figure"),
    ],
    Input("inflation-toggle-overview", "value"),
)
def inflation_on_off_overview(inflation_selection):

    years = [2016, 2017, 2018, 2019, 2020, 2021]
    # Take only those with data for each year.  
    df_new_rent_kommun = dfs["new_rent_kommun"][~(dfs["new_rent_kommun"]["Median Rent (SEK)"] <= 0)]
    complete_kommuner = df_new_rent_kommun["kommun"].value_counts().reset_index(name="count").query("count == 6")["index"] # all 6 years. 
    df_new_rent_kommun = df_new_rent_kommun[df_new_rent_kommun["kommun"].apply(lambda x : x in list(complete_kommuner))]

    df_new_rent_county = dfs["new_rent_county"][~(dfs["new_rent_county"]["Median Rent (SEK)"] <= 0)]
    complete_counties = df_new_rent_county["county"].value_counts().reset_index(name="count").query("count == 6")["index"] # all 6 years. 
    df_new_rent_county = df_new_rent_county[df_new_rent_county["county"].apply(lambda x : x in list(complete_counties))]

    if inflation_selection == "inflation_on":
        # first add new inflation adjusted column for plotting. 
        adjusted_cost_kommun = []
        for price, year in zip(df_new_rent_kommun["Median Rent (SEK)"], df_new_rent_kommun["Year"]): 
            adjusted_cost_kommun.append(round(inflation_adjust(price, year), 1))
        df_new_rent_kommun_box = df_new_rent_kommun.copy()
        df_new_rent_kommun_box["Inflation Adjusted Median Rent (SEK)"] = adjusted_cost_kommun
    
        adjusted_cost_county = []
        for price, year in zip(df_new_rent_county["Median Rent (SEK)"], df_new_rent_county["Year"]): 
            adjusted_cost_county.append(round(inflation_adjust(price, year), 1))
        df_new_rent_county_scatter = df_new_rent_county.copy()
        df_new_rent_county_scatter["Inflation Adjusted Median Rent (SEK)"] = adjusted_cost_county
            
        # Now plotting.     
        box_fig = go.Figure()
        for idx, year in enumerate(years):
            df = df_new_rent_kommun_box[(df_new_rent_kommun_box["Year"] == year)]
            box_fig.add_trace(go.Violin(x=df["Year"], y=df["Inflation Adjusted Median Rent (SEK)"], customdata=df, name=year, 
                                        box_visible=False, meanline_visible=True, line_color=violin_colors[idx], hoveron="points", 
                                        ))
            box_fig.update_traces(hovertemplate="<b>%{customdata[0]} </b><br><br>Median Cost: %{customdata[5]} SEK<extra></extra>") 

        scatter_fig = go.Figure()
        for county in (df_new_rent_county_scatter["county"].unique()):
            df = df_new_rent_county_scatter[(df_new_rent_county_scatter["county"] == county)]
            scatter_fig.add_trace(go.Scatter(x=df["Inflation Adjusted Median Rent (SEK)"], y=df["Year"], name=county,
                mode="lines+markers", customdata=df,
                marker=dict(size=12, line=dict(width=2, color='DarkSlateGrey')),
            ))
            scatter_fig.update_traces(hovertemplate="<b>%{customdata[0]} </b><br><br>Median Cost: %{customdata[5]} SEK<extra></extra>") 

    else: 
        # Straight to plotting. 
        box_fig = go.Figure()
        for idx, year in enumerate(years):
            df = df_new_rent_kommun[(df_new_rent_kommun["Year"] == year)] 
            box_fig.add_trace(go.Violin(x=df["Year"], y=df["Median Rent (SEK)"], customdata=df, name=year, 
                                        box_visible=False, meanline_visible=True, line_color=violin_colors[idx], hoveron="points", #here todo
                                        ))
            box_fig.update_traces(hovertemplate="<b>%{customdata[0]} </b><br><br>Median Cost: %{customdata[3]} SEK<extra></extra>") #here  

        scatter_fig = go.Figure()
        for county in (df_new_rent_county["county"].unique()):
            df = df_new_rent_county[(df_new_rent_county["county"] == county)]
            scatter_fig.add_trace(go.Scatter(x=df["Median Rent (SEK)"], y=df["Year"], name=county,
                mode="lines+markers", customdata=df,
                marker=dict(size=12, line=dict(width=2, color='DarkSlateGrey')),
            ))
            scatter_fig.update_traces(hovertemplate="<b>%{customdata[0]} </b><br><br>Median Cost: %{customdata[3]} SEK<extra></extra>") 

    # Params independant of callback below.
    box_fig.update_layout(
        yaxis=dict(title="Median Annual Rent Increase per M<sup>2</sup> (SEK)", titlefont_size=18, tickfont_size=14),
        xaxis=dict(title="", tickfont_size=14), margin={"r":0,"t":25,"l":0,"b":0}
    )
    box_fig.update_traces(meanline_visible=True, points="all", jitter=0.40, scalemode="count") 
    
    scatter_fig.update_layout(
        xaxis=dict(title="Median Annual Rent Increase per M<sup>2</sup> (SEK)", titlefont_size=18, tickfont_size=14),
        yaxis=dict(title="", tickfont_size=14), margin={"r":0,"t":25,"l":0,"b":0}, 
    )
    

    return box_fig, scatter_fig 



##################### rent_prices_vs_time callbacks ###########################

# Rent prices choropleth callback. 
@app.callback(
    Output("rent-choropleth-fig", "figure"),
    [
    Input("county-kommun-radio-vs-time-page", "value"),
    Input("year-slider", "value")
    ],
)
def choro_rent_vs_time(kommun_or_county, year):

    if kommun_or_county == "kommun_view":
        map_df = dfs["rent_kommun"][dfs["rent_kommun"]["Year"].apply(lambda x : x == year)]

        fig = px.choropleth_mapbox(map_df,
            geojson = kommuner_map, locations = "Relation", opacity=0.8, 
            color = "Median Rent (SEK)", featureidkey = "id", height=800, 
            color_continuous_scale="ylgnbu", range_color=[700, 1850], # "ylgnbu", "deep" # ["blue", "white", "red"]
            hover_data = {"kommun":True, "Relation":False, "Year":False,
                "Median Rent (SEK)":False, "Map Label":True},
        )

    elif kommun_or_county == "county_view":
        map_df = dfs["rent_county"][dfs["rent_county"]["Year"].apply(lambda x : x == year)]

        fig = px.choropleth_mapbox(map_df,
            geojson = counties_map, locations = "Relation", opacity=0.8,
            color = "Median Rent (SEK)", featureidkey = "id", height=800, 
            color_continuous_scale="ylgnbu", range_color=[850, 1350],  # "ylgnbu", "deep" # ["blue", "white", "red"]
            hover_data = {"county":True, "Relation":False, "Year":False,
                "Median Rent (SEK)":False, "Map Label":True},
        )

    # shared figure params below. 
    customdata = map_df
    fig.update_traces(hovertemplate="<b>%{customdata[0]} </b><br><br>%{customdata[4]}<extra></extra>") 
    fig.update_layout(legend=dict(
        title="Median Cost per M<sup>2</sup> (SEK)",
        yanchor="top", xanchor="left", 
        x=0.01, y=0.99, font=dict(size=16, color="black")
        ),
        mapbox_style="white-bg", mapbox_zoom=4.1, mapbox_center={"lat": 62.90, "lon": 16.00}, 
        plot_bgcolor="lightgray", margin={"r":0,"t":0,"l":0,"b":0}, 
    )

    return fig


# Rent card callback 
@app.callback(
    Output("rent-info-card", "children"),
    Input("rent-choropleth-fig", "clickData"),
    State("county-kommun-radio-vs-time-page", "value"),
    prevent_initial_call=True # because I am reliant on a user click. 
)
def get_card(clickData, kommun_or_county):
    if clickData is not None:
        location_id = clickData["points"][0]["location"] # gives relation id.
        location_name = clickData["points"][0]["customdata"][0] 
        if kommun_or_county == "kommun_view":
            bar_df = dfs["rent_kommun"][dfs["rent_kommun"]["Relation"].apply(lambda x : x == location_id)]
        else:
            bar_df = dfs["rent_county"][dfs["rent_county"]["Relation"].apply(lambda x : x == location_id)]

        fig = px.bar(bar_df, x="Year", y="Median Rent (SEK)",
            color="Median Rent (SEK)", color_continuous_scale="ylgnbu", range_color=[700, 1850]
        )

        fig.update_layout(
            xaxis=dict(title="", tickfont_size=14, tickmode = "array", tickvals = [2016, 2017, 2018, 2019, 2020, 2021]),
            yaxis=dict(title="Median Rent (SEK)", titlefont_size=18, tickfont_size=14), margin={"r":0,"t":30,"l":0,"b":0}, 
        )

        card_content = [
            dbc.CardBody([
                html.H5(f"You Have Selected: {location_name}.", className="card-title text-center"),
                html.P("Please note that any missing data (see FAQs tab) will show up as 0 on the bar chart below."),
                html.Br(),
                dcc.Graph(figure=fig)
            ]),
        ]

    return card_content


##################### rent_price_specifics callbacks ###########################

# Callback for dropdown-kommun-select. (Case insensitive search also enabled.)
@app.callback(
    dash.dependencies.Output("dropdown-kommun-select", "options"),
    [dash.dependencies.Input("dropdown-kommun-select", "search_value")],
    [dash.dependencies.State("dropdown-kommun-select", "value")],
)
def update_multi_options(search_value, value):
    if not search_value:
        raise PreventUpdate
    # Make sure that the set values are in the option list, else they will disappear
    # from the shown select list, but still part of the `value`.
    return [o for o in kommun_options if search_value.upper() in o["label"].upper() or o["value"] in (value or [])]


# Callback for updating page based on user selected kommuner. 
@app.callback(
    [
    Output("kommun-specific-info-text", "children"),
    Output("kommun-specific-map", "children"),
    Output("kommun-specific-to-county", "children"),
    Output("kommun-specific-median-bar", "children"),
    Output("kommun-specific-increase-bar", "children"),
    ],
    Input("dropdown-kommun-select", "value"),
)
def update_specifics_page(kommun): 

    # First filter based on user choice:
    median_bar_df = dfs["rent_kommun"][dfs["rent_kommun"]["kommun"].apply(lambda x : x == kommun)]
    increase_bar_df = dfs["new_rent_kommun"][dfs["new_rent_kommun"]["kommun"].apply(lambda x : x == kommun)]

    # Key Stats now:
    county_name = get_key(kommun, county_kommun_mapping) # gets the county name for the selected kommun. 
    numb_of_kommuner = len(county_kommun_mapping[county_name])

    df_2021 = dfs["rent_kommun"][dfs["rent_kommun"]["Year"].apply(lambda x : x == 2021)]
    df_2020 = dfs["rent_kommun"][dfs["rent_kommun"]["Year"].apply(lambda x : x == 2020)]

    # Current median rent rank
    df_2021 = df_2021.sort_values(by=["Median Rent (SEK)"], ascending=False)
    df_2021["Rank"] = df_2021["Median Rent (SEK)"].rank(method="min", na_option="bottom", ascending=False)
    kommun_rank = str(int(df_2021.loc[df_2021["kommun"] == kommun, "Rank"]))
    kommun_rank_line = [html.Li(f"{kommun} is ranked {kommun_rank} out of 288, for the most expensive municipality to rent in (2 municipalities of 290 do not have data available for this year).")]

    # Median rent increase from last year. 
    rent_2021 = df_2021[df_2021["kommun"].apply(lambda x : x == kommun)]["Median Rent (SEK)"]
    rent_2020 = df_2020[df_2020["kommun"].apply(lambda x : x == kommun)]["Median Rent (SEK)"]
    percent_increase = round((float(rent_2021)/float(rent_2020)*100) - 100, 1)
    percent_increase_line = [html.Li(f"{kommun} municipalities median rent increased by {percent_increase}% this year.")]

    # Make a df for plotting all kommuner that belong to the same county (alongside the county average) rent price as scatter+line plot. 
    same_county_list = county_kommun_mapping[county_name]
    df_local_kommuner = dfs["rent_kommun"][dfs["rent_kommun"]["kommun"].apply(lambda x : x in same_county_list)]
    df_county = dfs["rent_county"][dfs["rent_county"]["county"].apply(lambda x : x == (county_name +" county"))]
    df_local_kommuner = df_local_kommuner.rename(columns={"kommun": "Place"})
    df_county = df_county.rename(columns={"county": "Place"})
    df_compare_county = pd.concat([df_county, df_local_kommuner])

    if kommun in ["Ljusnarsberg", "Ragunda"]: # deal with the two years that have missing data.
        percent_increase_line = [html.Li("Unfortunately no statistics can be calculated for this Municipality due to missing data.")]
        kommun_rank_line = [html.P("")]


    # Now make all figures needed. 
    median_bar_fig = px.bar(median_bar_df, x="Median Rent (SEK)", y="Year", color="Median Rent (SEK)", color_continuous_scale="deep", orientation="h")
    median_bar_fig.update_layout(
        yaxis=dict(title="", tickfont_size=13, tickmode = "array", tickvals = [2016, 2017, 2018, 2019, 2020, 2021]),
        xaxis=dict(title="Median Annual Rent per square meter (SEK)", titlefont_size=16, tickfont_size=13),
        margin={"r":0,"t":30,"l":0,"b":0}, coloraxis_showscale=False,
    )
    median_bar_fig.update_traces(marker_line_color="black", marker_line_width=1.5, opacity=0.6)

    increase_bar_fig = px.bar(increase_bar_df, x="Median Rent (SEK)", y="Year", color="Median Rent (SEK)", color_continuous_scale="deep", orientation="h")
    increase_bar_fig.update_layout(
        yaxis=dict(title="", tickfont_size=13, tickmode = "array", tickvals = [2016, 2017, 2018, 2019, 2020, 2021]),
        xaxis=dict(title="Median Annual Increase in Rent per square meter (SEK)", titlefont_size=16, tickfont_size=13),
        margin={"r":0,"t":30,"l":0,"b":0}, coloraxis_showscale=False,
    )
    increase_bar_fig.update_traces(marker_line_color="black", marker_line_width=1.5, opacity=0.6)

    # Map highlighing selected kommun.
    def label_marked_kommun(row):
        """Helper function for creating new a df column with a selected kommun labelled as 1, 
        all others labelled as 0. Useful for marking selected kommun's location on map."""  
        if row["kommun"] == kommun: 
            return 1 
        return 0

    choro_df = (dfs["rent_kommun"][(dfs["rent_kommun"]["Year"] == 2021)]).copy()
    choro_df["MarkedLabel"] = choro_df.apply(label_marked_kommun, axis=1)
    choro_map = px.choropleth_mapbox(choro_df, geojson = kommuner_map, 
                             locations = "Relation", featureidkey = "id", opacity=0.8, height=475, 
                             color = "MarkedLabel", color_continuous_scale=["white", "green"], range_color=[0, 1],
                             hover_data = {"kommun":True, "Relation":False, "Year":False, "Median Rent (SEK)":False, 
                             "Map Label":False, "MarkedLabel":False}, title=f"{kommun}\'s Location",
                             )

    choro_map.update_geos(fitbounds="locations", visible=False)
    customdata = choro_df
    choro_map.update_traces(hovertemplate="<b>%{customdata[0]} </b><extra></extra>")
    choro_map.update_layout(
        legend=dict(yanchor="top", xanchor="left",x=0.01, y=0.80),
        margin={"r":0,"t":40,"l":0,"b":0}, mapbox_center = {"lat": 63.0, "lon": 20.00},
        mapbox_style="white-bg", mapbox_zoom=3.3, coloraxis_showscale=False,
        title_font_color="green", title=dict(font_size=20)
    )


    # Scatter + line plot of all local kommuner and county average. todo
    scatter_fig = go.Figure()
    for place in df_compare_county["Place"].unique():
        df = df_compare_county[(df_compare_county["Place"] == place)]
        df = df[df["Median Rent (SEK)"].apply(lambda x : x > 0)] # remove any missing values before plotting. 

        # If else so I can emphasize the county average as bigger on the graph. 
        if "county" in place:
            scatter_fig.add_trace(go.Scatter(x=df["Year"], y=df["Median Rent (SEK)"],
                                             name="County Average", mode="lines+markers", customdata=df,
                                             marker=dict(size=18, line=dict(width=4, color='DarkSlateGrey')),
                                            ))
            scatter_fig.update_traces(hovertemplate="<b>%{customdata[0]} </b><br><br>Median Cost: %{customdata[3]} SEK<extra></extra>") 
        
        else: 
            scatter_fig.add_trace(go.Scatter(x=df["Year"], y=df["Median Rent (SEK)"],
                                             name=place, mode="lines+markers", customdata=df,
                                             marker=dict(size=12, line=dict(width=2, color='DarkSlateGrey')),
                                            ))
            scatter_fig.update_traces(hovertemplate="<b>%{customdata[0]} </b><br><br>Median Cost: %{customdata[3]} SEK<extra></extra>") 
        
    scatter_fig.update_layout(margin={"r":0,"t":30,"l":0,"b":0}, xaxis=dict(title="", tickfont_size=14))
    scatter_fig.update_layout(yaxis=dict(title="Median Annual Rent per m<sup>2</sup> (SEK)", titlefont_size=18, tickfont_size=14))


    # Now make the card contents. 
    info_text_content = [
        dbc.Card(
            dbc.CardBody([
                html.H5([f"An Overview of {kommun} Municipality"], className="card-title"),              
                html.P([
                    f"{kommun} is one of {numb_of_kommuner} Municipalities that make up {county_name} County. ",
                    html.Br(), html.Br(),
                    html.B(html.A(f"Information Sverige's website describes {kommun} as follows:", href=kommun_urls[kommun], target="_blank")),
                    html.Br(),
                    "\"", kommun_info_texts[kommun], "\"",
                    html.Br(), 
                    html.A(f"Feel free to check out their website for more information about {kommun} Municipality.", href=kommun_urls[kommun], target="_blank"),
                    html.Br(), html.Br(),
                    html.H6([f"Key Statistics for {kommun} Municipality:"], className="card-title"), 
                    kommun_rank_line[0],
                    percent_increase_line[0],
                ]),
            ]),
        ),
    ]

    kommun_map_content = [
        dbc.Card(
            dbc.CardBody([
                dcc.Graph(figure=choro_map),
            ]),          
        )
    ]
    
    compare_county_content = [
        dbc.Card(
            dbc.CardBody([
                html.H5([f"Compare {kommun} to all {numb_of_kommuner - 1} other members of {county_name} county."], className="card-title"),
                dcc.Graph(figure=scatter_fig), 
            ]),
        )
    ]

    median_bar_content = [
        dbc.Card(
            dbc.CardBody([
                html.H5(["Median Annual Rent per m", html.Sup(2), f" for {kommun} (SEK)"], className="card-title"),
                dcc.Graph(figure=median_bar_fig)
            ]),
        )
    ]
    increase_bar_content = [
        dbc.Card(
            dbc.CardBody([
                html.H5(["Median Annual Increase in Rent per m", html.Sup(2), f" for {kommun} (SEK)"], className="card-title"),
                dcc.Graph(figure=increase_bar_fig)
            ]),
        )
    ]

    return info_text_content, kommun_map_content, compare_county_content, median_bar_content, increase_bar_content
    



######################### END OF Part 4 ######################

if __name__ == "__main__":
    app.run_server() 



