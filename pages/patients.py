import pandas as pd  # 
import plotly.express as px  # 
import streamlit as st 
import mysql.connector
import datetime as dt

st.set_page_config(
    page_title="Pacientes",
    page_icon="🏥",
    layout="wide",
)

############## Cargar Data ###################################
mydb = mysql.connector.connect(
  host="proyectdb.mysql.database.azure.com",
  user="administrador123",
  password="pasword123.",
  database="proyectdb"
)

admissions = pd.read_sql("""SELECT subject_id
                            FROM admissions""",mydb)

###################################################################################

st.markdown("# **Reporte de Paciente**")
st.markdown("---")

paciente = st.selectbox("Paciente",admissions['subject_id'].unique())

icustays = pd.read_sql("""SELECT * 
                              FROM icustays
                              WHERE subject_id = {paciente} 
                              ORDER BY intime DESC""".format(paciente=paciente),mydb)

estancia = st.selectbox("Estancia en UCI",icustays['ICUSTAY_ID'].unique())
hadm_id = icustays[icustays['ICUSTAY_ID'] == estancia]['HADM_ID'].values[0]
###################################################################################

st.markdown('## Información de Admisión')
st.markdown("---")

patient = pd.read_sql("""SELECT * 
                              FROM patient
                              WHERE subject_id = {paciente} """.format(paciente=paciente),mydb)
admission = pd.read_sql("""SELECT * 
                              FROM admissions
                              WHERE subject_id = {paciente} AND hadm_id = {hadmid}
                              ORDER BY admittime DESC""".format(paciente=paciente,hadmid =hadm_id),mydb)

st.dataframe(patient)
st.dataframe(admission)
st.dataframe(icustays) #Esta informacion no se va mostrar

###################################################################################
st.markdown('## Historial clinico en la UCI')
st.markdown("---")


diagnoses_icd = pd.read_sql("""SELECT d.seq_num, d.subject_id, d.hadm_id,dd.long_title 
                              FROM diagnoses_icd d
                              JOIN d_icd_diagnoses dd
                              ON (d.icd9_code = dd.icd9_code) 
                              WHERE subject_id = {paciente} AND hadm_id = {hadmid}
                              ORDER BY d.seq_num""".format(paciente=paciente,hadmid=hadm_id),mydb)


datetimeevents = pd.read_sql("""SELECT * 
                              FROM datetimeevents
                              WHERE subject_id = {paciente} AND icustay_id = {icustay}""".format(paciente=paciente,icustay=estancia),mydb)

callout = pd.read_sql("""SELECT * 
                              FROM callout
                              WHERE subject_id = {paciente} AND hadm_id = {hadmid}""".format(paciente=paciente,hadmid=hadm_id),mydb)

outputevents = pd.read_sql("""SELECT * 
                              FROM outputevents
                              WHERE subject_id = {paciente} AND icustay_id = {icustay} AND hadm_id = {hadmid}""".format(paciente=paciente,icustay=estancia,hadmid=hadm_id),mydb)

transfers = pd.read_sql("""SELECT * 
                              FROM transfers
                              WHERE subject_id = {paciente} AND icustay_id = {icustay}""".format(paciente=paciente,icustay=estancia),mydb)

st.subheader('Antecedentes')
st.dataframe(diagnoses_icd)
# Indicar tambien si el paciente fue readmitido

st.subheader('UCI')
st.dataframe(datetimeevents)

if outputevents.shape[0] > 0:
  st.subheader('Producción de liquidos')
  st.dataframe(outputevents) 

if callout.shape[0] > 0:
  st.subheader('Salida de alta')
  st.dataframe(callout) 

if transfers.shape[0] > 0:
  st.subheader('Transferencias')
  st.dataframe(transfers)  


st.subheader("Cuidadores a cargo del paciente")
if datetimeevents.shape[0] > 0:
    caregivers = pd.read_sql("""SELECT * 
                              FROM caregivers
                              WHERE cgid IN {cgids} """.format(cgids=tuple(datetimeevents['cgid'].unique())),mydb)                  

    st.dataframe(caregivers)

###################################################################################
st.markdown('## Procedimientos')
st.markdown("---")

services = pd.read_sql("""SELECT * 
                              FROM services
                              WHERE subject_id = {paciente} AND hadm_id = {hadmid}""".format(paciente=paciente,hadmid=hadm_id),mydb)

procedures_icd = pd.read_sql("""SELECT pro.seq_num ,dpro.short_title
                              FROM procedures_icd pro
                              JOIN d_icd_procedures dpro
                              ON pro.icd9_code = dpro.icd9_code
                              WHERE subject_id = {paciente} AND hadm_id = {hadmid}
                              ORDER BY pro.seq_num""".format(paciente=paciente,hadmid=hadm_id),mydb)

cptevents = pd.read_sql("""SELECT * 
                              FROM cptevents 
                              WHERE subject_id = {paciente} AND hadm_id = {hadmid}""".format(paciente=paciente,hadmid=hadm_id),mydb)

d_cpt = pd.DataFrame({})
for i in cptevents['CPT_CD'].unique():
  cpt = pd.read_sql("""SELECT * 
                              FROM d_cpt
                              WHERE mincodeinsubsection <= {cptcode} AND maxcodeinsubsection >= {cptcode} """.format(cptcode=i),mydb)
  d_cpt = pd.concat([d_cpt,cpt])


proceduresevents_mv = pd.read_sql("""SELECT * 
                              FROM procedureevents_mv
                              WHERE subject_id = {paciente} AND icustay_id = {icustay}""".format(paciente=paciente,icustay=estancia),mydb)



st.subheader('Anteriores a la estancia en UCI')
st.dataframe(services)
st.dataframe(procedures_icd) # Referente a antecedentes

st.subheader('Aplicados en UCI')
st.dataframe(cptevents) 
st.dataframe(d_cpt)

if proceduresevents_mv.shape[0] > 0:
  st.subheader('Ventilación Mecánica')
  st.dataframe(proceduresevents_mv) # Condicional 

###################################################################################
st.markdown('## Medicamentos')
st.markdown("---")


prescriptions = pd.read_sql("""SELECT * 
                              FROM prescriptions
                              WHERE subject_id = {paciente} AND hadm_id = {hadmid}""".format(paciente=paciente,hadmid=hadm_id),mydb)

inputevents_cv = pd.read_sql("""SELECT * 
                              FROM inputevents_cv
                              WHERE subject_id = {paciente} AND icustay_id = {icustay}""".format(paciente=paciente,icustay=estancia),mydb)

inputevents_mv = pd.read_sql("""SELECT * 
                              FROM inputevents_mv
                              WHERE subject_id = {paciente} AND icustay_id = {icustay}""".format(paciente=paciente,icustay=estancia),mydb)

st.subheader('Fuera de la UCI')
st.dataframe(prescriptions[prescriptions['ICUSTAY_ID'] == 0])

st.subheader('Suministrados en UCI')
st.dataframe(prescriptions[prescriptions['ICUSTAY_ID'] != 0])

if inputevents_cv.shape[0] > 0:
  st.subheader('Via Intravenosa')
  st.dataframe(inputevents_cv) #Intravenosos

if inputevents_mv.shape[0] > 0:
  st.subheader('Via Ventilación Mecánica')
  st.dataframe(inputevents_mv) # Ventilacion Mecanica

###################################################################################
st.markdown('## Pruebas de Laboratorio y microbiologicos')
st.markdown("---")

labevents2 = pd.read_sql("""SELECT * 
                              FROM labevents2
                              WHERE subject_id = {paciente} AND hadm_id = {hadmid}""".format(paciente=paciente,hadmid=hadm_id),mydb)

microbiologyevents = pd.read_sql("""SELECT * 
                              FROM microbiologyevents
                              WHERE subject_id = {paciente} AND hadm_id = {hadmid}""".format(paciente=paciente,hadmid=hadm_id),mydb)

st.dataframe(labevents2)
st.dataframe(microbiologyevents)

if st.button('Descargar'):#Centrar boton en el layout
  st.write(dt.datetime.now())
