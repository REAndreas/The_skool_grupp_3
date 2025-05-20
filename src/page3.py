from pathlib import Path
import taipy.gui.builder as tgb


import numpy as np
import pandas as pd
import plotly.graph_objects as go
import json
from difflib import get_close_matches
import duckdb

from utils import DATA_PATH



def create_choropleth_map(
    excel_path,
    geojson_path,
    colorscale="ylorrd",
    map_width=600,
    map_height=500,
    map_title="Beviljade utbildningar per län 2024",
    use_log=True
):
    # Load Excel data
    df = pd.read_excel(f"{DATA_PATH}/resultat-ansokningsomgang-2024.xlsx", sheet_name="Tabell 3", skiprows=5)


    # Register the dataframe with DuckDB
    duckdb.register("df", df)

    # Aggregate by län
    df_regions = duckdb.query(
        """
        SELECT 
            län AS Län,
            COUNT_IF(beslut = 'Beviljad') AS Beviljade
        FROM df 
        WHERE län != 'Flera kommuner'
        GROUP BY Län
        ORDER BY Beviljade DESC
        """
    ).df()

    # Load GeoJSON
    with open(f"{Path(__file__).parent}/assets/swedish_regions.geojson", encoding="utf-8") as fp:
        json_data = json.load(fp)

    # Extract region codes from GeoJSON
    properties = [feature.get("properties") for feature in json_data.get("features")]
    region_codes = {
        prop.get("name"): prop.get("ref:se:länskod")
        for prop in properties
    }

    # Match region names with geojson keys
    region_codes_map = []
    for region in df_regions["Län"]:
        region_name = get_close_matches(region, region_codes.keys())
        if len(region_name) > 0:
            region_code = region_codes.get(region_name[0])
            if region_code is not None:
                region_codes_map.append(region_code)
            else:
                print(f"Region code not found for {region}")
        else:
            print(f"No close match found for {region}")

    # Add länskod column and clean data
    df_regions["länskod"] = region_codes_map
    df_regions = df_regions.dropna(subset=["länskod"])
    df_regions["länskod"] = df_regions["länskod"].astype(str)

    # Apply log if needed
    if use_log:
        df_regions["Value"] = np.log(df_regions["Beviljade"] + 1)
        colorbar_title = "Beviljade"
    else:
        df_regions["Value"] = df_regions["Beviljade"]
        colorbar_title = "Beviljade"

    # Create the choropleth map
    fig = go.Figure(
        go.Choroplethmapbox(
            geojson=json_data,
            locations=df_regions["länskod"],
            z=df_regions["Beviljade"],
            featureidkey="properties.ref:se:länskod",
            colorscale=colorscale,
            marker_opacity=0.9,
            zmin=df_regions["Beviljade"].min(),
            zmax=df_regions["Beviljade"].max(),
            showscale=True,
            colorbar=dict(
                title=f"<b>{colorbar_title}<br>utbildningar</b>",
                thickness=18,
                x=1,
                y=0.5,
                len=0.8,
            ),
            customdata=df_regions["Beviljade"],
            text=df_regions["Län"],
            hovertemplate="<b>%{text}</b><br>Beviljade utbildningar: %{customdata}<extra></extra>",
            marker_line_width=0.3,
        )
    )

    fig.update_layout(
        title=dict(
            text=f"<b>{map_title}</b>",
            x=0.06,
            y=0.75,
            font=dict(size=14),
            font_color="black",
            font_family="Arial",
        ),
        mapbox=dict(
            style="white-bg",
            zoom=3.3,
            center=dict(lat=62.6952, lon=13.9149),
        ),
        margin=dict(r=0, t=50, l=0, b=0),
        dragmode=False,
        width=map_width,
        height=map_height,
    )

    return fig


# Run the function
fig = create_choropleth_map(
    excel_path="data/resultat-ansokningsomgang-2024.xlsx",             
    geojson_path="assets/swedish_regions.geojson",
    colorscale="ylorrd",
    map_width=700,
    map_height=550,
    map_title="Beviljade utbildningar per län 2024",
    use_log=True
)


with tgb.Page() as page_karta:
    with tgb.part():
        tgb.chart(figure="{fig}")