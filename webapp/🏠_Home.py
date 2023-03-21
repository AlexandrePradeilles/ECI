import streamlit as st
import pandas as pd
from datetime import date, datetime
import plotly.express as px

### IMPORT DATA ###

data2022 = pd.read_parquet('data/predictions_body_2022.parquet')
data2021 = pd.read_parquet('data/predictions_body_2021.parquet')
data2020 = pd.read_parquet('data/predictions_body_2020.parquet')
data2019 = pd.read_parquet('data/predictions_body_2019.parquet')

data = pd.concat([data2022, data2021, data2020, data2019])

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
    display_distribution(data)
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
            "Select the category", (data.predicted_classe.unique() )
            )
        
    display_chart(data, start_date,end_date, categories)
        
def display_chart(data, start_date, end_date, categories):
        df = data[["month_date", "predicted_classe"]][data.predicted_classe == categories].groupby(["month_date"]).count() / data[["month_date", "predicted_classe"]].groupby(["month_date"]).count()
        df.index = pd.DatetimeIndex(df.index)
        df = df[df.index <= pd.to_datetime(end_date)]
        final_df = df[df.index >= pd.to_datetime(start_date)]
        fig = px.line(final_df,
                      labels= {"month_date" : "Year",
                               "value" : "Rate of total publications (%)"})
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig)

def display_distribution(data):
    fig = px.histogram(data,x="predicted_classe",
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