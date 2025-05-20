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

    a = df[df[state.education_area] !=0][state.education_area].iloc[-1]
    b = df[df[state.education_area] !=0][state.education_area].iloc[0]
    state.education_difference = f"{"-" if a < b else ""}{round((a / b)*100, 2)}"

def create_chart(df, xlabel="Data/It",):
    fig = px.line(df, title=f"Antal studerande inom {xlabel} per år", y=xlabel, x="År")
    

    return fig

educated_chart = create_chart(df)
education_difference = round(df["Data/It"].iloc[-1] / df["Data/It"].iloc[0] * 100, ndigits=2)
education_area = "Data/It"

with tgb.Page() as page_studerande:
    with tgb.part():
        tgb.selector(value="{education_area}", lov= lov, dropdown=True, on_change=filter_chart)
        with tgb.layout(columns="400px"):
            with tgb.part(class_name="card"):
                tgb.text("Procentuell förändring mellan 2005 och 2024")
                tgb.text("#### **{education_difference} %**", mode="md")
        # Styla charten!! möjligen lägg till utbelda medel per år i hover text
        tgb.chart(figure="{educated_chart}")
        #