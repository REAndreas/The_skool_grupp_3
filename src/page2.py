import taipy.gui.builder as tgb
import pandas as pd
import plotly.express as px

from utils import DATA_PATH

df = pd.read_csv(DATA_PATH / "Yrkeshogskolan_transformed.csv")

df.rename(columns={"Unnamed: 0": "År"}, inplace=True)
lov = [col for col in df.columns if col != "År"]

def filter_chart(state):
    global df
    state.educated_chart = create_chart(df, yvalue = state.education_area)

    a = df[df[state.education_area] !=0][state.education_area].iloc[-1]
    b = df[df[state.education_area] !=0][state.education_area].iloc[0]
    state.education_difference = f"{"-" if a < b else ""}{round((a / b)*100, 2)}"

def create_chart(df, yvalue="Data/It",):
    fig = px.line(
        df, 
        title=f"Antal studerande inom {yvalue} per år mellan 2005-2024", 
        y=yvalue, 
        x="År",
        markers=True,
        height = 600,
        width = 1000
    )

    fig.data[0].hovertemplate = "År: %{x}<br>Antal Studerande: %{y}"

    fig.update_layout(
        yaxis_title = "",
        xaxis_title = "",
        xaxis = dict(
            showgrid = False,
            showline = True,
            linecolor = "rgba(101, 110, 242, 1)",
            range = [2005, 2025]
        ),
        yaxis = dict(
            showgrid = False,
            showline = True,
            linecolor = "rgba(101, 110, 242, 1)"
        )
    )
    fig.update_xaxes(
        ticks="outside"
    )   

    return fig

educated_chart = create_chart(df)
education_difference = round(df["Data/It"].iloc[-1] / df["Data/It"].iloc[0] * 100, ndigits=2)
education_area = "Data/It"

with tgb.Page() as page_studerande:
    tgb.text("## Studernade inom olika utbildningsområden", mode="md")
    with tgb.part():
        tgb.selector(value="{education_area}", lov= lov, dropdown=True, on_change=filter_chart)
        with tgb.layout(columns="1000px 400px"):
            with tgb.part():
                tgb.chart(figure="{educated_chart}")

            with tgb.part():    
                with tgb.part(class_name="kpi-card"):
                    tgb.text("{education_difference} %", class_name="kpi-value")
                    tgb.text("Procentuell förändring mellan 2005 och 2024", class_name="kpi-title")
            
            
        # with tgb.layout(columns="400px"):
        #     with tgb.part(class_name="kpi-card"):
        #         tgb.text("{education_difference} %", class_name="kpi-value")
        #         tgb.text("Procentuell förändring mellan 2005 och 2024", class_name="kpi-title")