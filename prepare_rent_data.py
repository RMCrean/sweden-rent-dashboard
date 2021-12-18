"""
Takes the 4 Statistics Sweden excel files and cleans/reformats them.
Outputs are saved as ".csv" files in the "assets" folder.

Terminology Note:
The code in this script uses the Swedish words "kommun"/"kommuner"
(translates to Municipality/Municiplaities in English) for varaiable naming.
County/Counties (and not län/län) are used however.
"""
import pandas as pd


def create_label_column(row) -> str:
    """
    Helper function to generate a new column which will be used
    to label the choropleth maps. Function used to label missing data
    (otherwise they will show up on the map as "-1 SEK").

    Parameters
    ----------
    row :

    Returns
    -------
    str
        Column label to show when user hovers mouse over a choropleth map.
    """
    if row["Median Rent (SEK)"] > 0:
        return "Median Cost: " + str(int(row["Median Rent (SEK)"])) + " SEK"
    else:
        return "Missing Data"


def process_stat_data(excel_path: str, kommun_or_county: str) -> pd.DataFrame:
    """
    Takes a Statistics Sweden excel file and reformats for easy processing
    in the web-app.

    Parameters
    ----------
    excel_path : str
        Path to excel file.

    kommun_or_county : str
        Defines if dataset is at the kommun or county level.

    Returns
    -------
    pd.DataFrame
        Dataframe reformatted for easy plotting with Plotly library.
    """
    columns_keep = [1, 4, 5, 6, 7, 8, 9]  # same for all.
    years = ["2016", "2017", "2018", "2019", "2020", "2021"]  # same for all.

    if kommun_or_county == "kommun":
        skip_rows = [0, 1] + list(range(294, 355))
        df_relations = pd.read_csv("assets/kommuner_list.csv")
    elif kommun_or_county == "county":
        skip_rows = [0, 1] + list(range(25, 81))
        df_relations = pd.read_csv("assets/counties_list.csv")
    else:
        raise ValueError(
            "You didn't choose between 'kommun' or 'county' for the 2nd parameter.")

    df_raw = pd.read_excel(excel_path, skiprows=skip_rows,
                           na_values=[".."], usecols=columns_keep)
    # read_excel always seem to keep an extra row.
    df = df_raw.drop(df_raw.tail(1).index, axis=0)
    df = df.rename(columns={"Unnamed: 1": kommun_or_county})
    df[kommun_or_county] = df[kommun_or_county].str.replace(
        "\d+", "", regex=True)
    df = df.applymap(lambda x: x.strip() if isinstance(x, str) else x)
    df = df.fillna(0)
    # add relation id.
    df = df.merge(df_relations, on=kommun_or_county, how="inner")

    df = pd.melt(df, id_vars=[kommun_or_county, "Relation"], value_vars=years)
    df = df.rename(columns={"variable": "Year", "value": "Median Rent (SEK)"})

    # Extra column to label when there is no rent data for a region.
    df["Map Label"] = df.apply(create_label_column, axis=1)

    return df


def main():
    """Processes excel files and saves output to .csv files."""
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
    dfs["rent_kommun"].to_csv(
        "assets/median_rent_kommuner_cleaned.csv", index=False, line_terminator="\n")
    dfs["rent_county"].to_csv(
        "assets/median_rent_counties_cleaned.csv", index=False, line_terminator="\n")
    dfs["new_rent_kommun"].to_csv(
        "assets/median_new_rent_kommuner_cleaned.csv", index=False, line_terminator="\n")
    dfs["new_rent_county"].to_csv(
        "assets/median_new_rent_counties_cleaned.csv", index=False, line_terminator="\n")


if __name__ == "__main__":
    main()
