import pandas as pd  # 
import plotly.express as px  # 
import streamlit as st 
<<<<<<< HEAD
=======
import mysql.connector
import datetime as dt
>>>>>>> 6d4f5399 (Agreando informacion en patients)

st.set_page_config(
    page_title="Pacientes",
    page_icon="🏥",
    layout="wide",
)

############## Cargar Data ###################################
<<<<<<< HEAD
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
=======
mydb = mysql.connector.connect(
  host="proyectdb.mysql.database.azure.com",
  user="administrador123",
  password="pasword123.",
  database="proyectdb"
)

admissions = pd.read_sql("""SELECT subject_id
                            FROM admissions""",mydb)

>>>>>>> 6d4f5399 (Agreando informacion en patients)
###################################################################################

st.markdown("# **Reporte de Paciente**")
st.subheader()
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
st.dataframe(icustays)

###################################################################################
st.markdown('## Historial clinico en la UCI')
st.markdown("---")

<<<<<<< HEAD
st.subheader('Costos del paciente')
st.markdown("---")
=======

diagnoses_icd = pd.read_sql("""SELECT d.seq_num, d.subject_id, d.hadm_id,dd.long_title 
                              FROM diagnoses_icd d
                              JOIN d_icd_diagnoses dd
                              ON (d.icd9_code = dd.icd9_code) 
                              WHERE subject_id = {paciente} AND hadm_id = {hadmid}
                              ORDER BY d.seq_num""".format(paciente=paciente,hadmid=hadm_id),mydb)


datetimeevents = pd.read_sql("""SELECT * 
                              FROM datetimeevents
                              WHERE subject_id = {paciente} AND icustay_id = {icustay}""".format(paciente=paciente,icustay=estancia),mydb)

#hadm_id = datetimeevents.

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
# Readmitido

st.subheader('UCI')
st.dataframe(datetimeevents)
st.dataframe(callout) #condicional
st.dataframe(outputevents) # condicional
st.dataframe(transfers)

if callout.shape[0] == 0:
    st.markdown('Salida de alta')
    


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

procedures_icd = pd.read_sql("""SELECT * 
                              FROM procedures_icd
                              WHERE subject_id = {paciente} AND hadm_id = {hadmid}""".format(paciente=paciente,hadmid=hadm_id),mydb)

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

st.subheader('Anteriores a UCI')
st.dataframe(prescriptions[prescriptions['ICUSTAY_ID'] == 0])

st.subheader('Suministrados en UCI')
st.dataframe(prescriptions[prescriptions['ICUSTAY_ID'] != 0])
st.dataframe(inputevents_cv) #Intravenosos
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
   
 
>>>>>>> 6d4f5399 (Agreando informacion en patients)
