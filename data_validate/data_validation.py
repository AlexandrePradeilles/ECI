import streamlit as st
import pandas as pd
from datetime import date, datetime
import plotly.express as plt
import numpy as np

### IMPORT DATA ###

data = pd.read_parquet('multi_classe_20perc.parquet')
body_list = data ["body"].values
cat_list = data ["predicted_classe"].values

def main():
    st.title("Data annotation")

    # Note that page title/favicon are set in the __main__ clause below,
    # so they can also be set through the mega multipage app (see ../pandas_app.py).

    try:
        annotation = np.load("annotations.npy", allow_pickle=True)
    except:
        annotation = []
        
    if 'annotation' not in st.session_state:
        st.session_state['annotation'] = list(annotation)
    
    if 'id' not in st.session_state:
         st.session_state['id'] = len(annotation)
         
    
    st.markdown("""*:grey[Compteur : {}]*""".format(len(st.session_state['annotation'])))
    
    st.write(body_list[len(st.session_state['annotation'])])
    st.markdown('**:red[{}]**'.format(cat_list[len(st.session_state['annotation'])]))
    
    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        if st.button("0"):
            st.session_state.annotation.append(0)
            st.session_state['id']+=1
            
    with col2:
        if st.button("1"):
            st.session_state.annotation.append(1)
            st.session_state['id']+=1
        
    with col3:
        if st.button("2"):
            st.session_state.annotation.append(2)
            st.session_state['id']+=1
    
    with col4:            
        if st.button("3"):
            st.session_state.annotation.append(3)
            st.session_state['id']+=1
    
    with col5:
        if st.button("Update"):
            pass

        if st.button("Save"):
            np.save("annotations.npy",st.session_state.annotation , allow_pickle=True)
            st.write("**:red[You can now leave the session]**")
            
        if st.button("Back"):
            st.session_state['id']-=1
            st.session_state.annotation.pop()
            
        if st.button("+10000"):
            st.session_state['id']+=10000

    st.markdown("""*:grey[Compteur : {}]*""".format(len(st.session_state['annotation'])))
    
### INTRODUCTION ###
# st.title("Data annotation")
main()
# st.markdown("""*:grey[Compteur : {}]*""".format(len(st.session_state['annotation'])))



### CREATE TABLE TO ANNOTATE 