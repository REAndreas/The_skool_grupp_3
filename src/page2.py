import taipy.gui.builder as tgb
import pandas as pd
import plotly.express as px

from utils import DATA_PATH

df = pd.read_csv(DATA_PATH / "Yrkeshogskolan_transformed.csv")

df.rename(columns={"Unnamed: 0": "År"}, inplace=True)
lov = [col for col in df.columns if col != "År"]

def filter_chart(state):
    global df
    state.educated_chart = create_chart(df, xlabel= state.education_area)

def create_chart(df, xlabel="Data/It",):
    fig = px.line(df, title=f"Antal studerande inom {xlabel} per år", y=xlabel, x="År")

    return fig

educated_chart = create_chart(df)

education_area = "Data/It"

with tgb.Page() as page_studerande:
    with tgb.part():
        tgb.selector(value="{education_area}", lov= lov, dropdown=True, on_change=filter_chart)

        tgb.chart(figure="{educated_chart}")

        tgb.table("{df[['År','Totalt']]}")