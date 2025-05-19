import taipy.gui.builder as tgb
import duckdb as ddb
import pandas as pd
 
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


def update_df_view(state):
    state.df_view = state.df_dataset[(state.df_dataset["Utbildningsanordnare"] == state.selected_anordnare) & (state.df_dataset["Ansökningsomgång"] == int(state.selected_year))]


with tgb.Page() as page_anordnare:
    with tgb.part():
        tgb.selector(value="{selected_anordnare}", lov = anordnare_lov, dropdown=True, on_change=update_df_view)
        tgb.selector(value="{selected_year}", lov = year_lov, dropdown=True, on_change=update_df_view)
        tgb.table(data="{df_view}")