import numpy as np
import pandas as pd
import json



def create_label_column(row):
    """Helper function to generate a new column which will be used to label the choropleth maps.
    Function used to help label missing data (otherwise it will show on the map as "-1 SEK")."""
    if row["Median Rent (SEK)"] > 0: 
        val = "Median Cost: " + str(int(row["Median Rent (SEK)"])) + " SEK"
    else:
        val = "Missing Data"
    return val



def process_stat_data(excel_path, kommun_or_county):
    """Takes a Statistics Sweden excel file and reformats it for easy analysis with pandas.
    Input is (1) the file path to the excel file And (2) whether this is data at the kommun or county level.
    Output is a prepared dataframe for Dash/Plotly."""
    columns_keep =[1, 4, 5, 6, 7, 8, 9] # same for all.
    years = ["2016", "2017", "2018", "2019", "2020", "2021"] # same for all.

    if kommun_or_county == "kommun":
        skip_rows = [0, 1] + list(range(294, 355))
        df_relations = pd.read_csv("assets/kommuner_list.csv")
    elif kommun_or_county == "county":
        skip_rows= [0, 1] + list(range(25, 81))
        df_relations = pd.read_csv("assets/counties_list.csv")
    else:
        raise ValueError("You didn't choose between 'kommun' or 'county' for the 2nd parameter.")
    
    df = pd.read_excel(excel_path, skiprows=skip_rows, na_values=['..'], usecols=columns_keep)
    df = df.drop(df.tail(1).index, axis=0) # read_excel always seem to keep an extra row.
    df = df.rename(columns={"Unnamed: 1": kommun_or_county})
    df[kommun_or_county] = df[kommun_or_county].str.replace('\d+', '', regex=True)
    df = df.applymap(lambda x: x.strip() if isinstance(x, str) else x)
    df = df.fillna(0) 
    df = df.merge(df_relations, on=kommun_or_county, how='inner') # add relation id.
    
    df = pd.melt(df, id_vars=[kommun_or_county, "Relation"], value_vars=years)
    df = df.rename(columns={"variable": "Year", "value": "Median Rent (SEK)"})

    # create extra column for labelling on graphs (so I can say if there is no rent data.)
    df["Map Label"] = df.apply(create_label_column, axis=1) 

    return df



def main():
	path_rent_kommun = "stats/Annual_Rent_2016_2021_by_Municipalities.xlsx"
	path_rent_county = "stats/Annual_Rent_2016_2021_by_County.xlsx"
	path_new_rent_kommun = "stats/New_Rent_2016_2021_by_Municipalities.xlsx"
	path_new_rent_county = "stats/New_Rent_2016_2021_by_County.xlsx"


	dfs = {}
	dfs["rent_kommun"] = process_stat_data(path_rent_kommun, "kommun")
	dfs["new_rent_kommun"] = process_stat_data(path_new_rent_kommun, "kommun")
	dfs["rent_county"] = process_stat_data(path_rent_county, "county")
	dfs["new_rent_county"] = process_stat_data(path_new_rent_county, "county")


	# save these for later use with Dash/Plotly.
	dfs["rent_kommun"].to_csv("assets/median_rent_kommuner_cleaned.csv", index=False, line_terminator="\n")
	dfs["rent_county"].to_csv("assets/median_rent_counties_cleaned.csv", index=False, line_terminator="\n")
	dfs["new_rent_kommun"].to_csv("assets/median_new_rent_kommuner_cleaned.csv", index=False, line_terminator="\n")
	dfs["new_rent_county"].to_csv("assets/median_new_rent_counties_cleaned.csv", index=False, line_terminator="\n")


if __name__ == "__main__":
	main()

