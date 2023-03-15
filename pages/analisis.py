import base64
import numpy as np  #
import pandas as pd  # 
import plotly.express as px  # 
import streamlit as st  # 🎈

labevents = pd.read_csv("./EDA_UCI/dataset/LABEVENTS.csv")
labitems = pd.read_csv("./EDA_UCI/dataset/D_LABITEMS.csv")
admissions = pd.read_csv('./EDA_UCI/dataset/ADMISSIONS.csv')
icustays = pd.read_csv('./EDA_UCI/dataset/ICUSTAYS.csv')
ditems = pd.read_csv('./EDA_UCI/dataset/D_ITEMS.csv')
dlabitems = pd.read_csv('./EDA_UCI/dataset/D_LABITEMS.csv')
patients = pd.read_csv('./EDA_UCI/dataset/PATIENTS.csv')
prescriptions = pd.read_csv('./EDA_UCI/dataset/PRESCRIPTIONS.csv')

st.sidebar.markdown("# Análisis descriptivo de las tablas 🎈")
st.sidebar.markdown("# Seleccione las tablas🎈")
tables = ['patients','prescriptions']
tabla_seleccionada = st.sidebar.selectbox('Seleccione las tablas🎈',tables)
st.header('Análisis descriptivo')
st.markdown("---")
fig3, fig4 = st.columns(2)
fig5, fig6 = st.columns(2)
if tabla_seleccionada == 'patients':
    with fig3:
        st.markdown("### Pacientes por sexo")
        patient = patients.merge(admissions, left_on='subject_id', right_on='subject_id')
        x = patient['gender'].value_counts().keys()
        y = patient['gender'].value_counts().values
        fig3 = px.bar(data_frame=patient, x=x, y = y )
        st.plotly_chart(fig3,use_container_width=True)

    with fig4:
        st.markdown("### Pacientes por estado civil")
        patient = patients.merge(admissions, left_on='subject_id', right_on='subject_id')
        x = patient['marital_status'].value_counts().keys()
        y = patient['marital_status'].value_counts().values
        fig4 = px.bar(data_frame=patient, x=x, y =y )
        st.plotly_chart(fig4,use_container_width=True)

    with fig5:
        st.markdown("### Pacientes por edad")
        patient = patients.merge(admissions, left_on='subject_id', right_on='subject_id')
        yearnac = pd.to_datetime(patient['dob'])
        yearmu = pd.to_datetime(patient['dod'])
        patient['age'] = yearmu.dt.year - yearnac.dt.year
        fig5 = px.histogram(data_frame=patient, x="age")
        st.plotly_chart(fig5,use_container_width=True)

    with fig6:
        st.markdown("### Pacientes por admission_location")
        patient = patients.merge(admissions, left_on='subject_id', right_on='subject_id')
        x = patient['admission_location'].value_counts().keys()
        y = patient['admission_location'].value_counts().values
        fig6 = px.bar(data_frame=patient, x=x, y =y)
        st.plotly_chart(fig6,use_container_width=True)

if tabla_seleccionada == 'prescriptions':
    with fig3:
        st.markdown("### Medicamentos más utilizados")
        x = prescriptions['drug'].value_counts().keys()
        y = prescriptions['drug'].value_counts().values
        fig3 = px.bar(data_frame=prescriptions, x=x, y = y )
        st.plotly_chart(fig3,use_container_width=True)

    with fig4:
        st.markdown("### Ruta de la medicación")
        x = prescriptions['route'].value_counts().keys()
        y = prescriptions['route'].value_counts().values
        fig4 = px.bar(data_frame=prescriptions, x=x, y =y )
        st.plotly_chart(fig4,use_container_width=True)


    st.markdown("### Medicamentos dados en el tiempo")
    prescriptions['startdate'] = prescriptions.startdate.apply(pd.to_datetime)
    prescriptions['month'] = prescriptions['startdate'].dt.to_period('M')
    max_value = prescriptions['startdate'].max()
    min_value = prescriptions['startdate'].min()
    mind, maxd  = st.date_input('Seleccione el rango de fecha', [min_value, max_value])
    from datetime import datetime
    maxd = datetime.strptime(str(maxd), '%Y-%m-%d')
    mind = datetime.strptime(str(mind), '%Y-%m-%d')
    filtered_prescriptions = prescriptions[(prescriptions['startdate'] > mind) & (prescriptions['startdate'] < maxd)]
    #filtered_prescriptions = prescriptions[prescriptions['startdate'] > mind]
    y = filtered_prescriptions.groupby(['month'])['drug'].count().values
    x = filtered_prescriptions.groupby(['month'])['drug'].count().index
    x = x.astype(str)
    #fig7 = px.line(data_frame=filtered_prescriptions, x=x, y = y)
    fig7 = px.line( x=x, y= y)
    st.plotly_chart(fig7,use_container_width=True)

