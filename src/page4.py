import taipy.gui.builder as tgb
import duckdb as ddb
import pandas as pd
import numpy as np
 
from utils import DATA_PATH
 
 
con = ddb.connect(database=":memory:")
 
con.sql(f"""
CREATE TABLE program_beslut AS
    FROM 'src/data/resultat-ansokningsomgang-2020-2024-beslut.csv';
CREATE TABLE program_kommun AS
    FROM 'src/data/resultat-ansokningsomgang-2020-2024-diarie_kommun.csv';  
""")
 
 

 
 
def create_rel_program_alla_kommuner(con, years: list[int] | int | None = None, *, distinct=False):
    if not years:
        years = None
    elif isinstance(years, int):
        years = [years]
 
    query = """
        with program_alla_kommuner as (
 
        select
            "Utbildningsområde",
            "Utbildningsnamn",
            "Län",
            "Kommun",
            "Antal kommuner",
            "Flera kommuner",
            "YH-poäng",
            "Studieform",
            "Studietakt %" as "Studietakt %",
            "Utbildningsanordnare",
            "Huvudmannatyp",
            "Sökta utbildningsomgångar",
            "Beviljade utbildningsomgångar",
            "Sökta platser totalt",
            "Beviljade platser totalt",
            "Sökta platser per utbildningsomgång",
            "Ansökningsomgång",
            "Diarienummer",
            "Beslut"
        from program_beslut pb
        where
            "Flera kommuner" is not TRUE
            and ( $year IS NULL OR pb."Ansökningsomgång" = ANY($year) )
 
        union all
 
        select
            pb."Utbildningsområde",
            pb."Utbildningsnamn",
            pk."Län",                -- kurser_kommun
            pk."Kommun",             -- kurser_kommun
            pb."Antal kommuner",
            pb."Flera kommuner",
            pb."YH-poäng",
            pb."Studieform",
            pb."Studietakt %" as "Studietakt %",
            pb."Utbildningsanordnare",
            pb."Huvudmannatyp",
            pb."Sökta utbildningsomgångar",
            pb."Beviljade utbildningsomgångar",
            pb."Sökta platser totalt",
            pb."Beviljade platser totalt",
            pb."Sökta platser per utbildningsomgång",
            pb."Ansökningsomgång",
            pb."Diarienummer",
            pb."Beslut"
        from program_beslut pb
        join program_kommun pk
            on pk."Diarienummer" = pb."Diarienummer"
        where
            pb."Flera kommuner" is TRUE
            and ( $year IS NULL OR pb."Ansökningsomgång" = ANY($year) )
 
        )
        select distinct on ("Diarienummer", "Kommun")
            *
        from program_alla_kommuner
        order by "Diarienummer";"""
 
    rel = con.sql(query, params={"year": years})
    return rel


selected_anordnare = "Stiftelsen Stockholms Tekniska Institut"
selected_year = 2024

df_dataset = create_rel_program_alla_kommuner(con, years=None).df()  # raw
anordnare_lov = sorted(df_dataset["Utbildningsanordnare"].unique())
year_lov = [int(x) for x in sorted(df_dataset["Ansökningsomgång"].unique())]
df_view = df_dataset[(df_dataset["Utbildningsanordnare"] == selected_anordnare) & (df_dataset["Ansökningsomgång"] == int(selected_year))]

kpi_antal_sokta = len(df_view)
kpi_beviljade = df_view[df_view["Beslut"] == True].groupby(["Utbildningsanordnare"])["Beslut"].count().iloc[0]
kpi_beviljad_procent = round(kpi_beviljade / kpi_antal_sokta * 100, 2)
kpi_yh_poang = int(round(df_view["YH-poäng"].mean(), 0))
kpi_sokta_platser = df_view["Sökta platser totalt"].sum()
kpi_beviljade_platser = df_view["Beviljade platser totalt"].sum()
kpi_distans = round(df_view[df_view["Studieform"] == "Distans"]["Studieform"].count() / df_view["Studieform"].count() * 100, 2)
kpi_mest_sokta_omrade = df_view["Utbildningsområde"].value_counts().sort_values(ascending=False).head(1).index[0]

def update_df_view(state):
    state.df_view = state.df_dataset[(state.df_dataset["Utbildningsanordnare"] == state.selected_anordnare) & (state.df_dataset["Ansökningsomgång"] == int(state.selected_year))]
    state.kpi_antal_sokta = state.df_view.groupby(["Utbildningsanordnare"])["Beslut"].count().iloc[0] if not state.df_view.empty else 0
    kpi_yh_poang_result = round(state.df_view["YH-poäng"].mean(), 0)
    state.kpi_yh_poang = 0 if np.isnan(kpi_yh_poang_result) else int(kpi_yh_poang_result)
    state.kpi_sokta_platser = state.df_view["Sökta platser totalt"].sum()
    state.kpi_beviljade_platser = state.df_view["Beviljade platser totalt"].sum()
    try:
        state.kpi_beviljade = state.df_view[state.df_view["Beslut"] == True].groupby(["Utbildningsanordnare"])["Beslut"].count().iloc[0] if not state.df_view.empty else 0
        state.kpi_beviljad_procent = round(state.kpi_beviljade / state.kpi_antal_sokta * 100, 2)
    except (IndexError, ZeroDivisionError):
        state.kpi_beviljade = 0
        state.kpi_beviljad_procent = 0

    try:
        state.kpi_distans = round(state.df_view[state.df_view["Studieform"] == "Distans"]["Studieform"].count() / state.df_view["Studieform"].count() * 100, 2) if not state.df_view.empty else 0
    except (ValueError, ZeroDivisionError):
        state.kpi_distans = 0

    state.kpi_mest_sokta_omrade = state.df_view["Utbildningsområde"].value_counts().sort_values(ascending=False).head(1).index[0] if not state.df_view.empty else "Inga sökta kurser"

with tgb.Page() as page_anordnare:
    tgb.text("## Statistik för individuella utbildningsanordnare", mode="md")
    with tgb.part():
        with tgb.layout(columns="1000px 200px"):
            with tgb.part():
                tgb.selector(value="{selected_anordnare}", lov = anordnare_lov, dropdown=True, on_change=update_df_view, filter=True)
            with tgb.part():
                tgb.selector(value="{selected_year}", lov = year_lov, dropdown=True, on_change=update_df_view, width="400px")
        
        with tgb.layout("400px 400px 400px"):
            with tgb.part(class_name="kpi-card"):
                tgb.text("{kpi_beviljade} av {kpi_antal_sokta}", class_name="kpi-value")
                tgb.text("Antal beviljade program av antal sökta", class_name="kpi-title")

            with tgb.part(class_name="kpi-card"):
                tgb.text("{kpi_beviljad_procent} %", class_name="kpi-value")
                tgb.text("Procentuellt beviljade utbildningar", class_name="kpi-title")
            
            with tgb.part(class_name="kpi-card"):
                tgb.text("{kpi_distans} %", class_name="kpi-value")
                tgb.text("Procentuellt ansökta distans-utbildningar", class_name="kpi-title")

        with tgb.layout("400px 400px 400px"):
            with tgb.part(class_name="kpi-card"): 
                tgb.text("{kpi_yh_poang} YH-poäng", class_name="kpi-value")
                tgb.text("Medelvärdet av sökta YH-poäng", class_name="kpi-title")

            with tgb.part(class_name="kpi-card"):
                tgb.text("{kpi_beviljade_platser} av {kpi_sokta_platser}", class_name="kpi-value")    
                tgb.text("Antal beviljade platser av antelt sökta", class_name="kpi-title")

            with tgb.part(class_name="kpi-card"):
                tgb.text("{kpi_mest_sokta_omrade}", class_name="kpi-value")    
                tgb.text("Område med flest sökta utbildningar", class_name="kpi-title")

    with tgb.expandable("Visa detaljerad information", expanded = False):
        with tgb.part():
            tgb.table(data="{df_view}")