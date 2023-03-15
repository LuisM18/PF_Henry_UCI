import pandas as pd  # 
import plotly.express as px  # 
import streamlit as st 

st.set_page_config(
    page_title="Pacientes",
    page_icon="🏥",
    layout="wide",
)

############## Cargar Data ###################################
labitems = pd.read_csv("./EDA_UCI/dataset/D_LABITEMS.csv")#
drgcodes = pd.read_csv('./EDA_UCI/dataset/DRGCODES.csv')#
labevents = pd.read_csv('./EDA_UCI/dataset/LABEVENTS.csv')#
micro = pd.read_csv('./EDA_UCI/dataset/MICROBIOLOGYEVENTS.csv')#
prescriptions = pd.read_csv('./EDA_UCI/dataset/PRESCRIPTIONS.csv')#
procedures = pd.read_csv('./EDA_UCI/dataset/PROCEDURES_ICD.csv')#
admissions = pd.read_csv('./EDA_UCI/dataset/ADMISSIONS.csv')
callout = pd.read_csv('./EDA_UCI/dataset/CALLOUT.csv')
icustays = pd.read_csv('./EDA_UCI/dataset/ICUSTAYS.csv')
patients = pd.read_csv('./EDA_UCI/dataset/PATIENTS.csv')
services = pd.read_csv('./EDA_UCI/dataset/SERVICES.csv')
caregivers = pd.read_csv('./EDA_UCI/dataset/CAREGIVERS.csv')
chartevents = pd.read_csv('./EDA_UCI/dataset/CHARTEVENTS.csv')
datetimeevents = pd.read_csv('./EDA_UCI/dataset/DATETIMEEVENTS.csv')
inputeventscv = pd.read_csv('./EDA_UCI/dataset/INPUTEVENTS_CV.csv')
inputeventsmv = pd.read_csv('./EDA_UCI/dataset/INPUTEVENTS_MV.csv')
transfers = pd.read_csv('./EDA_UCI/dataset/TRANSFERS.csv')
dcpt = pd.read_csv('./EDA_UCI/dataset/D_CPT.csv')
ddiagnoses = pd.read_csv('./EDA_UCI/dataset/D_ICD_DIAGNOSES.csv')
dprocedures = pd.read_csv('./EDA_UCI/dataset/D_ICD_PROCEDURES.csv')#
ditems = pd.read_csv('./EDA_UCI/dataset/D_ITEMS.csv')
dlabitems = pd.read_csv('./EDA_UCI/dataset/D_LABITEMS.csv')
noteevents= pd.read_csv('./EDA_UCI/dataset/NOTEEVENTS.csv')
outputevents= pd.read_csv('./EDA_UCI/dataset/OUTPUTEVENTS.csv')
procedureevents_mv = pd.read_csv('./EDA_UCI/dataset/PROCEDUREEVENTS_MV.csv')
cptevents = pd.read_csv('./EDA_UCI/dataset/CPTEVENTS.csv')
diagnoses_icd = pd.read_csv('./EDA_UCI/dataset/DIAGNOSES_ICD.csv') 
###################################################################################

st.markdown("# **Reporte de Paciente**")
st.subheader()
st.markdown("---")

paciente = st.selectbox("Paciente",admissions['subject_id'])


st.subheader('Información')
st.markdown("---")

st.subheader('Historial clinico en la UCI')
st.markdown("---")

st.subheader('Procedimientos')
st.markdown("---")

st.subheader('Medicamentos')
st.markdown("---")

st.subheader('Pruebas de Laboratorio')
st.markdown("---")

st.subheader('Costos del paciente')
st.markdown("---")
