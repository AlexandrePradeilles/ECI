import altair as alt
import pandas as pd
import streamlit as st
from datetime import date, datetime


st.set_page_config(
    page_title="Test Altair", page_icon="⬇", layout="centered"
)

@st.cache_data
def get_data():
    df_2018 = pd.read_parquet("predictions_body_2018.parquet")
    df_2019 = pd.read_parquet("predictions_body_2019.parquet")
    df_2020 = pd.read_parquet("predictions_body_2020.parquet")
    df_2021 = pd.read_parquet("predictions_body_2021.parquet")
    df_2022 = pd.read_parquet("predictions_body_2022.parquet")

    df = pd.concat([df_2018, df_2019, df_2020, df_2021, df_2022])

    df['month_date'] = pd.DatetimeIndex(df['month_date'])
    return df[["predicted_classe", "month_date", 'article_url']].groupby(["predicted_classe", "month_date"]).count().reset_index()


def get_chart(data):
    hover = alt.selection_single(
        fields=["month_date"],
        nearest=True,
        on="mouseover",
        empty="none",
    )

    lines = (
        alt.Chart(data, height=500, title="Nombre d'articles publés par sujet")
        .mark_line()
        .encode(
            x=alt.X("month_date", title="Date"),
            y=alt.Y("article_url", title="Nombre d'articles"),
            color="predicted_classe",
        )
    )

    # Draw points on the line, and highlight based on selection
    #points = lines.transform_filter(hover).mark_circle(size=65)

    # Draw a rule at the location of the selection
    tooltips = (
        alt.Chart(data)
        .mark_rule()
        .encode(
            x="month_date",
            y="article_url",
            opacity=alt.condition(hover, alt.value(0.3), alt.value(0)),
            tooltip=[
                alt.Tooltip("month_date", title="Date"),
                alt.Tooltip("article_url", title="Nombre"),
            ],
        )
        .add_selection(hover)
    )

    return (lines + tooltips).interactive()


st.title("ECI")

source = get_data()

col1, col2 = st.columns(2)
with col1:
    choix = st.selectbox(
        "Choix du sujet",
        ["Tout"] + list(source['predicted_classe'].unique()))
    
    
with col2:
    dates = st.slider(
    "Période :",
    min_value=datetime(2018, 1, 1),
    value=(datetime(2018, 1, 1), datetime(2023, 1, 1)),
    max_value=datetime(2023, 1, 1),
    format="MMM, YYYY")
    
    start_date, end_date = dates
    #st.write(start_date)

if choix == "Tout":
    chart = get_chart(source.loc[(source.month_date >= start_date) & (source.month_date <= end_date)])
else:
    chart = get_chart(source.loc[(source.month_date >= start_date) & (source.month_date <= end_date)].loc[source.predicted_classe == choix])

st.altair_chart((chart).interactive(), use_container_width=True)