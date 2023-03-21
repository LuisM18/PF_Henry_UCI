
import base64
import numpy as np  #
import pandas as pd  # 
import plotly.express as px  # 
import streamlit as st
import mysql.connector
from datetime import datetime
import os
import io

st.set_page_config(
    page_title="Carga de datos- Crowe Clinic",
    page_icon="🏥",
    layout="wide",
)
#os.path.realpath(__file__)
#os.chdir("..")
#st.write(os.getcwd())
rel_path = "../images/a_photography_of_Crowe clinic_hospital3.png"

with open(rel_path, "rb") as image_file:
    encoded_string = base64.b64encode(image_file.read())
st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url(data:image/{"png"};base64,{encoded_string.decode()});
            background-attachment: fixed;
            background-size: cover
        }}
        </style>
        """,
        unsafe_allow_html=True
    )
st.title('Carga de datos- Crowe Clinic')
lista_tablas = ['admissions','callout','caregivers','chartevents','cptevents','d_cpt','d_icd_diagnoses','d_icd_procedures','d_items','d_labitems','datetimeevents','diagnoses_icd','drgcodes','icustays','inputevents_cv','inputevents_mv','labevents','microbiologyevents','noteevents','outputevents','patients','prescriptions','procedureevents_mv','procedures_icd','services','transfers']
st.selectbox('Selecciona la tabla a cargar', lista_tablas)
uploaded_file = st.file_uploader("Selecciona un archivo csv", accept_multiple_files=False, type =['csv'])

if uploaded_file is not None:
    # To read file as bytes:
    # Can be used wherever a "file-like" object is accepted:
    dataframe = pd.read_csv(uploaded_file)
    st.write(dataframe)