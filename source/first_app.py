import pandas as pd
import plotly.express as px  
import streamlit as st
from datetime import date, datetime
import altair as alt

st.set_page_config(page_title="ECI Dashboard", page_icon=":seedling:", layout="wide")

# Première page Welcome
# Comparaison par media (radio et newspapers confondus)
# page Methodology


# ---- READ FILE ----
@st.cache_data
def get_data_from_excel():
    df = pd.read_parquet("predictions_body_2018.parquet")
    return df

df = get_data_from_excel()

st.title("ECI Dashboard")
#st.markdown("##")



tab1, tab2, tab3, tab4= st.tabs(["Menu", "Méthodologie", "Insights", "par media"])

with tab1:
    st.header("Menu")
    st.markdown("The project aims at assessing quantity, quality and relevance of communication on climate change")
    st.dataframe(df)

with tab2:
    st.header("Méthodologie")
    st.image("https://static.streamlit.io/examples/dog.jpg", width=200)

with tab3:
    st.header("Top Insights")
    #st.image("https://static.streamlit.io/examples/owl.jpg", width=200)


    dates = st.slider(
    "Schedule time range:",
    min_value=date(2010, 1, 1),
    value=(date(2010, 1, 1), date(2022, 1, 1)),
    max_value=date(2022, 1, 1),
    format="MMM, YYYY")
    
    start_date, end_date = dates

    option = st.selectbox(
        "Choix du sujet",
        ("Email", "Home phone", "Mobile phone"))
    
    st.write("Choix", option)


    st.markdown("""---""")
    left_column, middle_column, right_column = st.columns(3)
    st.markdown("""---""")

with left_column:
    st.subheader("Total:")
    st.subheader(f"{3:,}")

middle_column.metric("Recall", 0.60, delta=-0.1)
right_column.metric("Precision", 0.85, delta=0.2)
    
with tab4:
    st.header("Insight par média")

    









# ---- HIDE STREAMLIT STYLE ----
hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)
