import streamlit as st
import pandas as pd
from datetime import date, datetime
import plotly.express as px
import numpy as np

### IMPORT DATA ###

# data2022 = pd.read_parquet('data/predictions_body_2022.parquet')
# data2021 = pd.read_parquet('data/predictions_body_2021.parquet')
# data2020 = pd.read_parquet('data/predictions_body_2020.parquet')
# data2019 = pd.read_parquet('data/predictions_body_2019.parquet')

# data = pd.concat([data2022, data2021, data2020, data2019])
data_20 = pd.read_parquet("data/20minutes.parquet")
data_20["newspaper"] = "20 minutes"
data_libe = pd.read_parquet("data/liberation.parquet")
data_libe["newspaper"] = "Liberation"

data = pd.concat([data_20, data_libe])

dict_thres = {"20 minutes": 0.2, "Liberation": 0.26}
dict_classes = {'planete': 0, 'sport': 1, 'economie': 2, 'arts-stars': 3, 'high-tech': 4, 'politique': 5, 'monde': 6, 'societe': 7, 'faits_divers': 8, 'sante': 9, 'justice': 10}
dict_classes_inv = {v:k for (k, v) in dict_classes.items()}

if "old_np" not in st.session_state:
    st.session_state.old_np = ''

PAGES = [
    '🏠 Home',
    '🤓 About us'
]

st.set_page_config(
    page_title="ECI",
    page_icon="🌱",
    layout="wide"
)
# st.sidebar.title('ECI - Menu')

def main():
    # Note that page title/favicon are set in the __main__ clause below,
    # so they can also be set through the mega multipage app (see ../pandas_app.py).
    newspaper = st.selectbox(
            "Select a newspaper", (data.newspaper.unique())
            )
    st.write("Global distribution")
    if newspaper != st.session_state.old_np:
        st.session_state.distribution = display_distribution(data, newspaper)
        st.session_state.old_np = newspaper
    else:
        display_precomputed_distribution(st.session_state.distribution)
    col1, col2 = st.columns(2)

    with col1:
        max_date = datetime.strptime(data.month_date.max(), '%Y-%m').date()
        min_date = datetime.strptime(data.month_date.min(), '%Y-%m').date()
        start_date = st.date_input(
            "Select start date",
            min_date,
            min_value=min_date,
            max_value=max_date,
        )
        end_date = st.date_input(
            "Select end date",
            max_date,
            min_value=start_date,
            max_value=max_date,
        )

    with col2:
        categories = st.selectbox(
            "Select the category", (data.columns[3:-1] )
            )
        
    display_chart(data, start_date,end_date, categories, newspaper)
        
def display_chart(data, start_date, end_date, categories, newspaper):
        df = data[["month_date", categories]][(data[categories] >= dict_thres[newspaper]) & (data["newspaper"] == newspaper)].groupby(["month_date"]).count() / data[["month_date", categories]][data["newspaper"] == newspaper].groupby(["month_date"]).count()
        df.index = pd.DatetimeIndex(df.index)
        df = df[df.index <= pd.to_datetime(end_date)]
        final_df = df[df.index >= pd.to_datetime(start_date)]
        fig = px.line(final_df,
                      labels= {"month_date" : "Year",
                               "value" : "Rate of total publications (%)"})
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig)

def extract_class(probabilities, th=0.05):
    cat = list()
    if probabilities[0] >= th:
        cat.append("planete")
    if probabilities[1] >= th:
        cat.append("sport")
    if probabilities[2] >= th:
        cat.append("economie")
    if probabilities[3] >= th:
        cat.append("arts-stars")
    if probabilities[4] >= th:
        cat.append("high-tech")
    if probabilities[5] >= th:
        cat.append("politique")
    if probabilities[6] >= th:
        cat.append("monde")
    if probabilities[7] >= th:
        cat.append("societe")
    if probabilities[8] >= th:
        cat.append("faits_divers")
    if probabilities[9] >= th:
        cat.append("sante")
    if probabilities[10] >= th:
        cat.append("justice")
    if cat == []:
        cat.append(dict_classes_inv[np.argmax(probabilities)])
    return cat

def display_distribution(data, newsp):
    df = data[["planete", "sport", "economie", "arts-stars", "high-tech", "politique", 'monde', "societe", "faits_divers", "sante", "justice"]][data["newspaper"] == newsp]
    df["predicted_classe"] = df.apply(lambda x: extract_class(x.values), axis=1)
    df = df.explode("predicted_classe")
    fig = px.histogram(df,x="predicted_classe",
                       labels= {"predicted_classe" : "Predicted Class",
                               "count" : "Number of iterations"})
    st.plotly_chart(fig)
    return df

def display_precomputed_distribution(df):
    fig = px.histogram(df,x="predicted_classe",
                       labels= {"predicted_classe" : "Predicted Class",
                               "count" : "Number of iterations"})
    st.plotly_chart(fig)
    
### INTRODUCTION ###
st.title("🌱 Welcome to the Environnemental Communication Index! 🌱")

st.markdown("""
            Given the emergency of the Climate Crisis, Climate Related Communicationis more important than ever. This topic is still underrepresented in the media, leading to a recent push for an Environmental Journalism Charter.
        """)
st.markdown("""
            This project aims at assessing quantity, quality and relevance of communication on climate change
            """)
main()
st.markdown("""*:grey[Streamlit App by: Martin Lanchon, Alexandre Pradeilles, Antoine Dargier, Martin Ponchon]*""")