import streamlit as st
import pandas as pd
from datetime import date, datetime
import plotly.express as px
import numpy as np

### IMPORT DATA ###

@st.cache_data
def get_data():
    data_20 = pd.read_parquet("../data/20minutes.parquet")
    data_20["newspaper"] = "20 minutes"
    data_libe = pd.read_parquet("../data/liberation.parquet")
    data_libe["newspaper"] = "Liberation"

    data = pd.concat([data_20, data_libe])
    return data

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

data = get_data()

def main():
    # Note that page title/favicon are set in the __main__ clause below,
    # so they can also be set through the mega multipage app (see ../pandas_app.py).
    tab1, tab2, tab3, tab4= st.tabs(["Menu", "Methodologie", "Global distribution", "Evolution over time"])
    
    with tab3:    
        newspaper = st.selectbox(
                "Select a newspaper", (data.newspaper.unique()),
                key=1)
        st.write("Global distribution")
        if newspaper != st.session_state.old_np:
            st.session_state.distribution = display_distribution(data, newspaper)
            st.session_state.old_np = newspaper
        else:
            display_precomputed_distribution(st.session_state.distribution)
       
        
    with tab4:  
        max_date = datetime.strptime(data.month_date.max(), '%Y-%m').date()
        min_date = datetime.strptime(data.month_date.min(), '%Y-%m').date()
        dates = st.slider(
        "Select date:",
        min_value=min_date,
        value=(min_date, max_date),
        max_value=max_date,
        format="MMM, YYYY")
            
        start_date, end_date = dates
        col1, col2 = st.columns(2)
        with col1:
           newspapers = st.multiselect(
                "Select a newspaper", (data.newspaper.unique()),
                default=(data.newspaper.unique()),
                key=2
                )
        st.write("Global distribution")
        with col2:
            categories = st.multiselect(
                "Select the category", data.columns[3:-1].to_list()
                )
        
        display_chart(data, start_date,end_date, categories, newspapers)
            
def display_chart(data, start_date, end_date, categories, newspapers):
        data_multilines = 0
        if len(categories) == 0:
            categories = data.columns[3:-1].to_list()
            
        if type(categories) == str:
            categories = [categories]
        for categorie in categories:
            for newspaper in newspapers:
                df = data[["month_date", categorie]][(data[categorie] >= dict_thres[newspaper]) & (data["newspaper"] == newspaper)].groupby(["month_date"]).count() / data[["month_date", categorie]][data["newspaper"] == newspaper].groupby(["month_date"]).count()
                df.index = pd.DatetimeIndex(df.index)
                df["newspaper"] = newspaper
                df["cat"] = categorie
                df = df.rename({categorie : "value"}, axis=1)
                if type(data_multilines) == int:
                    data_multilines = df
                else: 
                    data_multilines = pd.concat([data_multilines,df],axis=0)
        
        data_multilines = data_multilines[data_multilines.index <= pd.to_datetime(end_date)]
        data_multilines = data_multilines[data_multilines.index >= pd.to_datetime(start_date)]
        
        if len(categories)==1:
            # data_multilines["event"] = [""]*data_multilines.shape[0]
            # filter = (data_multilines.index == "2022-02-01") & (data_multilines["cat"].values=="planete")
            # data_multilines.loc[filter,"event"] = "Rapport GIEC"
            fig = px.line(data_multilines,
                    labels= {"month_date" : "Year",
                               "value" : "Rate of total publications (%)"},
                    color = "cat",
                    line_dash="newspaper"
                      )
            fig = add_annotation(fig,data_multilines, categories[0])

        else:
            fig = px.line(data_multilines,
                    labels= {"month_date" : "Year",
                               "value" : "Rate of total publications (%)"},
                    color = "cat",
                    line_dash="newspaper"
                      )
            
            fig.update_layout(showlegend=True)
        st.plotly_chart(fig)

def add_annotation(fig,data, categorie):
    dic_annot = {"planete": [["2018-12-01" , "COP24" ],
                             ["2021-08-01" , "1st report GIEC" ], 
                             ["2022-02-01" , "2nd report GIEC" ],
                            ["2022-04-01" , "3rd report GIEC" ]]}
    placement = 1.06
    if categorie not in dic_annot.keys():
        print("none")
        return fig
    
    for event in dic_annot[categorie]:
        #try :
        print(pd.to_datetime(event[0], format='%Y-%m-%d'))
        fig.add_vline(x=pd.to_datetime(event[0], format='%Y-%m-%d').timestamp()*1000, 
                    line_dash="dot")
        fig.add_annotation(
                x=pd.to_datetime(event[0], format='%Y-%m-%d').timestamp()*1000,
                y=placement,
                yref='paper',
                showarrow=False,
                text=event[1])
        # fig.add_annotation(xref="x", yref="y",axref="x", ayref="y",
        #                         x=event[0],
        #                         ax=event[0],
        #                         y= data.loc[event[0]].value,
        #                         ay = (1+placement)*data.loc[event[0]].value,
        #                         text=event[1],
        #                         showarrow=True)
        #except:
            #None
        placement +=0.04
    return fig


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
st.write(data.month_date.values[0])