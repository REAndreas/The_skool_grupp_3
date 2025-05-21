from utils import DATA_PATH

import duckdb as ddb
import plotly.graph_objects as go
import taipy.gui.builder as tgb


con = ddb.connect(database=":memory:")

con.sql(f"""
CREATE TABLE kurser_beslut AS
    FROM '{DATA_PATH}/resultat-for-kurser-inom-yh-2024-beslut.csv';
CREATE TABLE kurser_kommun AS
    FROM '{DATA_PATH}/resultat-for-kurser-inom-yh-2024-diarie_kommun.csv';      
""")


def create_rel_kurser_alla_kommuner(con, years: list[int] | int | None = None, *, distinct=False):
    if not years:
        years = None
    elif isinstance(years, int):
        years = [years]

    base_query = """
        with kurser_alla_kommuner as (

        select
            "Diarienummer",
            "Ansökningsomgång",
            "Beslut",
            "Utbildningsanordnare",
            "Utbildningsnamn",
            "Utbildningsområde",
            "YH-poäng",
            "Beviljade platser",
            "Beviljade platser totalt",
            "Start",
            "Län",
            "Kommun",
            "Antal kommuner",
            "Flera kommuner"
        from kurser_beslut kb
        where
            "Flera kommuner" is not TRUE
            -- and kb."Ansökningsomgång" = 2024
            and ( $year IS NULL OR kb."Ansökningsomgång" = ANY($year) )
        
        union all

        select
            kb."Diarienummer",
            kb."Ansökningsomgång",
            kb."Beslut",
            kb."Utbildningsanordnare",
            kb."Utbildningsnamn",
            kb."Utbildningsområde",
            kb."YH-poäng",
            kb."Beviljade platser",
            kb."Beviljade platser totalt",
            kb."Start",
            kk."Län",                -- kurser_kommun
            kk."Kommun",             -- kurser_kommun
            kb."Antal kommuner",
            kb."Flera kommuner"
        from kurser_beslut kb
        join kurser_kommun kk
            on kk."Diarienummer" = kb."Diarienummer"
        where
            kb."Flera kommuner" is TRUE
            and ( $year IS NULL OR kb."Ansökningsomgång" = ANY($year) )

        )"""

    if distinct:
        query = (
            base_query
            + """
        select distinct on ("Diarienummer", "Kommun")
            "Diarienummer",
            "Ansökningsomgång",
            "Beslut",
            "Utbildningsanordnare",
            "Utbildningsnamn",
            "Utbildningsområde",
            "YH-poäng",
            -- "Beviljade platser",
            "Beviljade platser totalt",
            -- "Start",
            "Län",
            "Kommun",
            "Antal kommuner",
            "Flera kommuner"
        from kurser_alla_kommuner
        order by "Diarienummer";"""
        )
    else:
        query = (
            base_query
            + """
        select *
        from kurser_alla_kommuner
        order by "Diarienummer";"""
        )

    rel = con.sql(query, params={"year": years})
    return rel


def create_rel_utbildningsomrade_beslut(con):
    rel = con.sql(
        """
    select
        Utbildningsområde,
        count(distinct case when Beslut = TRUE then Diarienummer end)::integer as Beviljade,
        count(distinct case when Beslut = FALSE then Diarienummer end)::integer as Avslag
    from ( select distinct on (Diarienummer) * from rel_kurser ) as unique_entries
    group by
        Utbildningsområde
    order by count(Beslut) desc
    ;"""
    )
    return rel


def split_label(label, max_chars=30, split_word="och"):
    words = label.split()
    lines = []
    current_line = []
    current_length = 0

    for i, word in enumerate(words):
        # Check if adding this word would exceed max_chars
        if current_length + len(word) > max_chars and current_line:
            # If the last word in current_line is "och", move it to next line
            if current_line[-1] == split_word:
                current_line.pop()  # Remove "och"
                lines.append(" ".join(current_line))
                current_line = [split_word, word]  # Start new line with "och" and current word
                current_length = len(split_word) + len(word) + 1
            else:
                lines.append(" ".join(current_line))
                current_line = [word]
                current_length = len(word)
        else:
            current_line.append(word)
            current_length += len(word) + 1

    if current_line:
        lines.append(" ".join(current_line))

    return "<br>".join(lines)


def make_fig_utbildningsomrade_beslut(df):
    common_params = dict(
        orientation="h",
        textposition="inside",
        insidetextanchor="end",
        textangle=0,
        textfont=dict(
            size=12,
            color="white",
        ),
    )

    fig = go.Figure(
        data=[
            go.Bar(
                **common_params,
                name="Avslag",
                y=df.index,
                x=df["Avslag"],
                text=df["Avslag"],
                # customdata=df.index,
                hovertemplate="%{x} Avslag<extra></extra>",
                marker_color="rgba(101, 110, 242, 0.5)",
            ),
            go.Bar(
                **common_params,
                name="Beviljade",
                y=df.index,
                x=df["Beviljade"],
                text=df["Beviljade"],
                # customdata=df.index,
                hovertemplate="%{x} Beviljade<extra></extra>",
                marker_color="rgba(101, 110, 242, 1)",
            ),
        ]
    )

    split_labels = {idx: split_label(idx, max_chars=20) for idx in df.index}  # max chars line break
    sorted_idx = df.sort_values("Beviljade").index

    fig.update_layout(
        barmode="group",
        height=len(df) * 60,  # bar height
        plot_bgcolor="rgba(0, 0, 0, 0)",
        font=dict(family="Arial", size=13),
        margin=dict(l=150, r=0, t=0, b=0, pad=10),
        yaxis=dict(
            categoryorder="array",
            categoryarray=sorted_idx,
            ticktext=[split_labels[idx] for idx in sorted_idx],  # split lines
            tickvals=sorted_idx,  # sort order
        ),
        legend=dict(
            orientation="h",
            traceorder="reversed",
            yanchor="bottom",
            xanchor="right",
            y=0.02,
            x=0.98,
            bgcolor="rgba(255, 255, 255, 0)",
            bordercolor="rgba(0, 0, 0, 0)",
            borderwidth=1,
        ),
    )

    fig.update_traces(width=0.375)

    return fig

def create_rel_utbildningsomrade_topp(con):
    rel = con.sql(
        """
    select
        Utbildningsanordnare,
        count(distinct Diarienummer) as Sökta,
        --count(distinct case when Beslut = TRUE then Diarienummer end)::integer as Beviljade,
        --count(distinct case when Beslut = FALSE then Diarienummer end)::integer as Avslag
    from ( select distinct on (Diarienummer) * from rel_kurser ) as unique_entries
    group by
        Utbildningsanordnare
    order by Sökta desc, Utbildningsanordnare
    ;"""
    )
    return rel


rel_kurser = create_rel_kurser_alla_kommuner(con)
df_utbildningsomrade_beslut = create_rel_utbildningsomrade_beslut(con).df().set_index("Utbildningsområde")
fig_utbildningsomrade_beslut = make_fig_utbildningsomrade_beslut(df_utbildningsomrade_beslut)
df_topplista = create_rel_utbildningsomrade_topp(con).df()

topplista_format = "\n".join([str(i) + ". " + x for i, x in enumerate(df_topplista["Utbildningsanordnare"].head(3), 1)])

kpi_mean_sokta = round(df_topplista["Sökta"].mean())
kpi_yh_poang = round(rel_kurser.df()["YH-poäng"].mean())

with tgb.Page() as page_kurser:
    with tgb.part(class_name="card"):
        tgb.text("## Beslut för individuellt sökta kurser", mode="md")

        with tgb.layout("1200px"):
            tgb.chart(figure="{fig_utbildningsomrade_beslut}")

        with tgb.layout("400px 400px 400px"):
            with tgb.part(class_name="kpi-list-card"):
                tgb.text("**Topp 3 Sökta kurser per anordnare**", mode="md", class_name="kpi-title")
                tgb.text("{topplista_format}", mode="md", class_name="kpi-title")

            with tgb.part(class_name="kpi-card"):
                tgb.text("{kpi_mean_sokta}", class_name="kpi-value")
                tgb.text("Antal sökta kurser per anordnare, medelvärde", class_name="kpi-title")

            with tgb.part(class_name="kpi-card"):
                tgb.text("{kpi_yh_poang} YH-poäng", class_name="kpi-value")
                tgb.text("Medelvärdet av sökta YH-poäng", class_name="kpi-title")
            

    

