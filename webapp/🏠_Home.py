import streamlit as st
import pandas as pd
from datetime import date, datetime
from dateutil.relativedelta import relativedelta
import plotly.express as px
import numpy as np

### IMPORT DATA ###


def extract_class(row, classes_list, threshold=0.15):
    # Keep only the classes with prob > threshold
    res_dict = {col: row[col] for col in classes_list if row[col] > threshold}

    if res_dict == {}:
        return [col for col in classes_list if row[col] == row.max]
    else:
        # return list with classes by decreasing order of probability
        if row['medium_type'] == 'newspaper':
            return sorted(res_dict, key=res_dict.get, reverse=True)
        if row['medium_type'] == 'radio':
            res_list = sorted(res_dict, key=res_dict.get, reverse=True)
            if 'planete' in res_list and res_list[0] != 'planete':
                res_list.remove('planete')
            return res_list


@st.cache_data
def get_data():
    # Get data for 20 minutes
    data_20_1 = pd.read_parquet("../data/20minutes_part1.parquet")
    data_20_2 = pd.read_parquet("../data/20minutes_part2.parquet")
    data_20 = pd.concat([data_20_1, data_20_2])
    data_20["medium_name"] = "20 minutes"
    data_20["medium_type"] = "newspaper"
    data_20 = data_20.drop('category_id', axis=1).rename(columns={'article_url':'url'})
    
    # Get data for Liberation
    data_libe = pd.read_parquet("../data/liberation.parquet")
    data_libe["medium_name"] = "Liberation"
    data_libe["medium_type"] = "newspaper"
    data_libe = data_libe.drop('category_id', axis=1).rename(columns={'article_url':'url'})
    
    # Get data for France Inter
    data_franceinter = pd.read_parquet("../data/franceinter.parquet")
    data_franceinter["medium_name"] = "France Inter"
    data_franceinter["medium_type"] = "radio"

    data = pd.concat([data_20, data_libe, data_franceinter])
    
    # Get predicted classes
    classes_list = ["planete", "sport", "economie", "arts-stars", "high-tech", "politique", 'monde', "societe", "faits_divers", "sante", "justice"]
    data["predicted_classes"] = data.apply(lambda row: extract_class(row, classes_list), axis=1)

    return data



dict_thres = {"20 minutes": 0.2, "Liberation": 0.26, "France Inter": 0.2}
dict_classes = {'planete': 0, 'sport': 1, 'economie': 2, 'arts-stars': 3, 'high-tech': 4, 'politique': 5, 'monde': 6, 'societe': 7, 'faits_divers': 8, 'sante': 9, 'justice': 10}
dict_classes_inv = {v:k for (k, v) in dict_classes.items()}


if "old_np" not in st.session_state:
    st.session_state.old_np = ''

# PAGES = [
#     '🏠 Home',
#     '🤓 About us'
# ]


st.set_page_config(
    page_title="ECI",
    page_icon="🌱",
    layout="wide"
)
# st.sidebar.title('ECI - Menu')

def compute_time_allocated_to_climate_by_show(data_radio):
    by_show_df = pd.pivot_table(data_radio, values=['planete', 'talks_about_climate'], index=['url', 'month_date'], aggfunc={'planete': 'count', 'talks_about_climate': np.sum}, fill_value=0)
    by_show_df = by_show_df.reset_index().rename(columns={'planete':'nb_segments'})
    by_show_df['proportion_of_time_about_climate'] = by_show_df['talks_about_climate'] * 100 / by_show_df['nb_segments']
    return by_show_df



            
def display_chart(data, start_date, end_date, categories, newspapers):
        data_multilines = 0
        if len(categories) == 0:
            categories = dict_classes.keys()
            
        if type(categories) == str:
            categories = [categories]
        for categorie in categories:
            for newspaper in newspapers:
                df = data[["month_date", categorie]][(data[categorie] >= dict_thres[newspaper]) & (data["medium_name"] == newspaper)].groupby(["month_date"]).count() / data[["month_date", categorie]][data["medium_name"] == newspaper].groupby(["month_date"]).count()
                df.index = pd.DatetimeIndex(df.index)
                df["medium_name"] = newspaper
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
                    labels= {"month_date" : "Année",
                               "value" : "Rate of total publications (%)"},
                    color = "cat",
                    line_dash="medium_name").update_layout(yaxis_title="Rate of total publications (%)")
            fig = add_annotation(fig,data_multilines, categories[0])

        else:
            fig = px.line(data_multilines,
                    labels= {"month_date" : "Année",
                               "value" : "Rate of total publications (%)"},
                    color = "cat",
                    line_dash="medium_name").update_layout(yaxis_title="Rate of total publications (%)")
            
            fig.update_layout(showlegend=True)
        st.plotly_chart(fig, use_container_width=True)



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


def display_distribution(data, newsp):
    df = data[data["medium_name"] == newsp]
    df = df.explode("predicted_classes")
    fig = px.histogram(df, x="predicted_classes",
                       labels= {"predicted_classes" : "Predicted Class",
                               "count" : "Number of iterations"},
                       title='Topics covered by the media (in #)').update_layout(yaxis_title="Number of iterations")
    st.plotly_chart(fig, use_container_width=True)
    return df


def display_pie(data, newsp):
    df = data[data["medium_name"] == newsp]
    df = df.explode("predicted_classes")
    fig = px.pie(df,
                 values=df.predicted_classes.value_counts().values,
                 names=df.predicted_classes.value_counts().index,
                 title='Topics covered by the media (in %)')
    st.plotly_chart(fig, use_container_width=True)


def display_precomputed_distribution(df):
    fig = px.histogram(df, x="predicted_classes",
                       labels= {"predicted_classes" : "Predicted Class",
                               "count" : "Number of iterations"},
                       title='Topics covered by the media (in #)').update_layout(yaxis_title="Number of iterations")
    st.plotly_chart(fig, use_container_width=True)


def display_precomputed_pie(df):
    fig = px.pie(df,
                 values=df.predicted_classes.value_counts().values,
                 names=df.predicted_classes.value_counts().index,
                 title='Topics covered by the media (in %)')

    st.plotly_chart(fig, use_container_width=True)


def get_metrics(data):
    df_metric = data.copy()
    df_metric =  df_metric.explode("predicted_classes")
    df_metric["year"] = pd.to_datetime(df_metric.month_date, format = '%Y-%m').dt.year
    current_month = (datetime.strptime(df_metric.month_date.max(),"%Y-%m")- relativedelta(months=1)).strftime("%Y-%m")
    last_month = (datetime.strptime(df_metric.month_date.max(),"%Y-%m")- relativedelta(months=2)).strftime("%Y-%m")
    current_month_rate = df_metric[df_metric.month_date ==current_month].predicted_classes.value_counts().planete/df_metric[df_metric.month_date ==current_month].predicted_classes.value_counts().sum()
    change = np.round((df_metric[df_metric.month_date ==current_month].predicted_classes.value_counts().planete - df_metric[df_metric.month_date ==last_month].predicted_classes.value_counts().planete)/df_metric[df_metric.month_date ==current_month].predicted_classes.value_counts().sum(), 3)
    
    nb_articles = "{:,}".format(data.loc[data.medium_type == 'newspaper'].shape[0])
    broad_time = "{:,} hours".format(int(data.loc[data.medium_type == 'radio'].shape[0]*5/60))
    climate_rate = "{:.0%}".format(np.round(current_month_rate,2))
    climate_change = "{:.0%}".format(change)
    return nb_articles, broad_time, climate_rate, climate_change


def main():
    # Note that page title/favicon are set in the __main__ clause below,
    # so they can also be set through the mega multipage app (see ../pandas_app.py).
    
    data = get_data()
    data_radio = data.loc[data.medium_type == 'radio']
    data_radio["talks_about_climate"] = data_radio['predicted_classes'].apply(lambda classes: 'planete' in classes)

    tab1, tab2, tab3, tab4, tab5 = st.tabs(["🌱 ECI", "🛠️ Methodology", "📊 Breakdown by topic", "📈 Temporal Evolution", "📊 Distribution of radio shows"])
    
    with tab1:
        st.markdown("""
             Given the emergency of the Climate Crisis, climate-related communication is more important than ever. This topic is still underrepresented in the media, leading to a recent push for an Environmental Journalism Charter.
         """)
        st.markdown("""
             This project aims at assessing quantity, quality and relevance of communication on climate change
             """)
        st.markdown("--------")
        col11, col12, col13 = st.columns(3)
        nb_articles, broad_time, climate_rate, climate_change = get_metrics(data)
        with col11:
            st.metric("Number of articles", nb_articles)
        with col12:
            st.metric("Available broadcast time", broad_time)
        with col13:
            st.metric("Climate communication rate current month", climate_rate, climate_change)
    
    
    with tab3:    
        newspaper = st.selectbox(
                "Select a newspaper", (data.medium_name.unique()),
                key=1)
        st.write("Global distribution")
        if newspaper != st.session_state.old_np:
            st.session_state.distribution = display_distribution(data, newspaper)
            display_pie(data, newspaper)
            st.session_state.old_np = newspaper
        else:
            display_precomputed_distribution(st.session_state.distribution)
            display_precomputed_pie(st.session_state.distribution)
       
        
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
                "Select a newspaper", (data.medium_name.unique()),
                default=(data.medium_name.unique()),
                key=2
                )
        st.write("Global distribution")
        with col2:
            categories = st.multiselect(
                "Select the category", dict_classes.keys()
                )
        
        display_chart(data, start_date, end_date, categories, newspapers)

    with tab5:
        by_show_df = compute_time_allocated_to_climate_by_show(data_radio)
        st.markdown("If the climate topic is brought up in virtually every show , it only represents on average {} % of air time in a news show".format(round(by_show_df['proportion_of_time_about_climate'].mean())))
        fig = px.histogram(by_show_df, 
                            x="proportion_of_time_about_climate",
                            title="Climate topic in radio shows",
                            labels={"proportion_of_time_about_climate" : "Share of air time dedicated to climate (%)"},
                            nbins=30).update_layout(yaxis_title="Number of shows")
        st.plotly_chart(fig, use_container_width=True)


    
### INTRODUCTION ###
st.title("🌱 Environmental Communication Index 🌱")


main()
st.markdown("""*:grey[Streamlit App by: Martin Lanchon, Alexandre Pradeilles, Antoine Dargier, Martin Ponchon]*""")
#st.write(data.month_date.values[0])
