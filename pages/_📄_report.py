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

st.markdown("<h1 style='text-align: center; color: white;'> Hoja de informe de la UCI</h1>", unsafe_allow_html=True)
st.markdown("---")

#Traemos de la base de datos

admitted = pd.read_sql("""SELECT admittime 
                              FROM admissions
                              WHERE subject_id = {paciente} AND hadm_id = {hadmid}
                              ORDER BY admittime DESC""".format(paciente=paciente,hadmid =hadm_id),mydb)
admitted = pd.DataFrame(admitted)
admitted= admitted['admittime'].values[0] 

age = pd.read_sql("""SELECT (YEAR(DOD_HOSP)- YEAR(DOB)) as age 
                              FROM patient
                              WHERE subject_id = {paciente} """.format(paciente=paciente),mydb)   
age = pd.DataFrame(age)    
age = age['age'].values[0]                 

gender = pd.read_sql("""SELECT gender
                              FROM patient
                              WHERE subject_id = {paciente} """.format(paciente=paciente),mydb) 

gender = pd.DataFrame(gender)
gender = gender['gender'].values[0]  

diagnoses_long = pd.read_sql("""SELECT dd.long_title 
                              FROM diagnoses_icd d
                              JOIN d_icd_diagnoses dd
                              ON (d.icd9_code = dd.icd9_code) 
                              WHERE subject_id = {paciente} AND hadm_id = {hadmid}
                              ORDER BY d.seq_num""".format(paciente=paciente,hadmid=hadm_id),mydb)

patient = pd.read_sql("""SELECT * 
                              FROM patient
                              WHERE subject_id = {paciente} """.format(paciente=paciente),mydb)

subject = pd.read_sql("""SELECT SUBJECT_ID 
                              FROM patient
                              WHERE subject_id = {paciente} """.format(paciente=paciente),mydb)
subject = pd.DataFrame(subject)
subject = subject['SUBJECT_ID'].values[0]  

admission= pd.read_sql("""SELECT *
                              FROM admissions
                              WHERE subject_id = {paciente} AND hadm_id = {hadmid}
                              ORDER BY admittime DESC""".format(paciente=paciente,hadmid =hadm_id),mydb)

discharge= pd.read_sql("""SELECT DISCHARGE_LOCATION 
                              FROM admissions
                              WHERE subject_id = {paciente} AND hadm_id = {hadmid}
                              ORDER BY admittime DESC""".format(paciente=paciente,hadmid =hadm_id),mydb)

procedures_ant = pd.read_sql("""SELECT dpro.short_title
                              FROM procedures_icd pro
                              JOIN d_icd_procedures dpro
                              ON pro.icd9_code = dpro.icd9_code
                              WHERE subject_id = {paciente} AND hadm_id = {hadmid}
                              ORDER BY pro.seq_num""".format(paciente=paciente,hadmid=hadm_id),mydb)

cptevents = pd.read_sql("""SELECT * 
                              FROM cptevents 
                              WHERE subject_id = {paciente} AND hadm_id = {hadmid}""".format(paciente=paciente,hadmid=hadm_id),mydb)

d_cpt2 = pd.DataFrame({})
for i in cptevents['CPT_CD'].unique():
  cpt = pd.read_sql("""SELECT subsectionheader 
                              FROM d_cpt
                              WHERE mincodeinsubsection <= {cptcode} AND maxcodeinsubsection >= {cptcode} """.format(cptcode=i),mydb)
  d_cpt2= pd.concat([d_cpt2,cpt])

value = pd.read_sql("""SELECT valuenum
                              FROM labevents2
                              WHERE subject_id = {paciente} AND hadm_id = {hadmid}""".format(paciente=paciente,hadmid=hadm_id),mydb)

valueuom = pd.read_sql("""SELECT valueuom
                              FROM labevents2
                              WHERE subject_id = {paciente} AND hadm_id = {hadmid}""".format(paciente=paciente,hadmid=hadm_id),mydb)


itemidlabs = pd.read_sql("""SELECT labevents2.itemid, D_LABITEMS.label
                              FROM labevents2
                              INNER JOIN D_LABITEMS ON D_LABITEMS.itemid=labevents2.itemid
                              WHERE subject_id = {paciente} AND hadm_id = {hadmid}
                              """.format(paciente=paciente,hadmid=hadm_id),mydb)

proceduresevents_mv = pd.read_sql("""SELECT * 
                              FROM procedureevents_mv
                              WHERE subject_id = {paciente} AND icustay_id = {icustay}""".format(paciente=paciente,icustay=estancia),mydb)

procedures_icd = pd.read_sql("""SELECT pro.seq_num ,dpro.short_title
                              FROM procedures_icd pro
                              JOIN d_icd_procedures dpro
                              ON pro.icd9_code = dpro.icd9_code
                              WHERE subject_id = {paciente} AND hadm_id = {hadmid}
                              ORDER BY pro.seq_num""".format(paciente=paciente,hadmid=hadm_id),mydb)
d_cpt = pd.DataFrame({})
for i in cptevents['CPT_CD'].unique():
  cpt = pd.read_sql("""SELECT * 
                              FROM d_cpt
                              WHERE mincodeinsubsection <= {cptcode} AND maxcodeinsubsection >= {cptcode} """.format(cptcode=i),mydb)
  d_cpt = pd.concat([d_cpt,cpt])


#Reporte

col2, col3, col4 = st.columns([3,1,1])

with col2:
  st.markdown('ADMITIDO: {admitted}'. format(admitted = admitted))
with col3:
  st.markdown('CÓDIGO: {subject}'. format(subject = subject))

col5, col6, col7 = st.columns([3,2,2])

with col5:
  st.markdown('NOMBRE COMPLETO:') 
with col6:
  st.markdown('EDAD:{age}'.format(age = age)) 
with col7:
  st.markdown('SEXO:')
  st.write(gender) 
st.markdown('SITUACIÓN:')
st.markdown('HISTORIA MÉDICA DEL PACIENTE')
st.dataframe(diagnoses_long['long_title'])

col8, col9 = st.columns([3,2])

with col8:
  st.markdown('TESTS AND IMAGING')
  st.markdown('PROCEDIMIENTOS')
  st.markdown('Anteriores a UCI')
  st.dataframe(procedures_ant)
  st.markdown('Durante UCI')
  #st.dataframe(procedures_icd)
  st.dataframe(cptevents) 
  st.dataframe(d_cpt)     

  if proceduresevents_mv.shape[0] > 0:
    st.subheader('Ventilación Mecánica')
    st.dataframe(proceduresevents_mv) # Condicional 

with col9:
  st.markdown('LABS')
  valueslabs = pd.concat([itemidlabs, value,valueuom], axis=1)
  st.dataframe(valueslabs)

st.markdown('DESCARGO')

discharge = pd.DataFrame(discharge)

st.markdown(discharge['DISCHARGE_LOCATION'].values[0])

#Descargar reporte
if st.button('Descargar'):#Centrar boton en el layout
  st.write(dt.datetime.now())




