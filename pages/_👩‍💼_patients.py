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
  host= st.secrets["DB_HOST"],
  user=st.secrets["DB_USER"],
  password=st.secrets["DB_PASSWORD"],
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
st.markdown("<h1 style='text-align: center; color: white;'> Información de Admisión</h1>", unsafe_allow_html=True)
st.markdown("---")

patient = pd.read_sql("""SELECT * 
                              FROM patient
                              WHERE subject_id = {paciente} """.format(paciente=paciente),mydb)
admission = pd.read_sql("""SELECT * 
                              FROM admissions_hechos
                              WHERE subject_id = {paciente} AND hadm_id = {hadmid}
                              ORDER BY admittime DESC""".format(paciente=paciente,hadmid =hadm_id),mydb)

age = pd.read_sql("""SELECT (YEAR(DOD)- YEAR(DOB)) as age 
                              FROM patient
                              WHERE SUBJECT_ID = {paciente} """.format(paciente=paciente),mydb)   
age = pd.DataFrame(age)    
age = age['age'].values[0]     

col2, col3, col4 = st.columns(3)

with col2:
  st.markdown('ADMITIDO:  {admitted}'. format(admitted = admission['ADMITTIME'].values[0]))
with col3:
  st.markdown('CÓDIGO:  {subject}'. format(subject = paciente))
with col4:
  st.markdown('TIEMPO EN UCI: {los} horas'.format(los= round(icustays['LOS'].values[0]*24)))

col5, col6, col7 = st.columns(3)

with col5:
  st.markdown('NOMBRE COMPLETO: XXXXXX XXXXXX') 
with col6:
  st.markdown('EDAD:  {age} años'.format(age = age)) 
with col7:
  st.markdown('SEXO:  {gender}'.format(gender= patient['GENDER'].values[0]))

if admission['DEATHTIME'].values[0] != None:
  st.markdown('FECHA DE MUERTE: {death}'.format(death= admission['DEATHTIME'].values[0]))



###################################################################################
st.markdown("<h1 style='text-align: center; color: white;'> Historial clinico en la UCI</h1>", unsafe_allow_html=True)
st.markdown("---")


diagnoses_icd = pd.read_sql("""SELECT d.seq_num AS '#' ,dd.long_title AS DIAGNOSTICO 
                              FROM diagnoses_icd d
                              JOIN d_icd_diagnoses dd
                              ON (d.icd9_code = dd.icd9_code) 
                              WHERE subject_id = {paciente} AND hadm_id = {hadmid}
                              ORDER BY d.seq_num""".format(paciente=paciente,hadmid=hadm_id),mydb)
diagnoses_icd.set_index('#',inplace=True)


datetimeevents = pd.read_sql("""SELECT DISTINCT CGID
                              FROM datetimeevents 
                              WHERE subject_id = {paciente} AND icustay_id = {icustay}""".format(paciente=paciente,icustay=estancia),mydb)


callout = pd.read_sql("""SELECT *
                              FROM callout
                              WHERE subject_id = {paciente} AND hadm_id = {hadmid}""".format(paciente=paciente,hadmid=hadm_id),mydb)
callout.drop(columns=['SUBJECT_ID','HADM_ID'],inplace=True)
callout.set_index('ROW_ID',inplace=True)

outputevents = pd.read_sql("""SELECT o.* , d.LABEL ,d.CATEGORY 
                              FROM outputevents o
                              RIGHT JOIN d_items d
                              ON o.ITEMID = d.ITEMID
                              WHERE o.subject_id = {paciente} AND o.icustay_id = {icustay} AND o.hadm_id = {hadmid}""".format(paciente=paciente,icustay=estancia,hadmid=hadm_id),mydb)
outputevents.drop(columns=['SUBJECT_ID','ICUSTAY_ID','HADM_ID','ITEMID','STOPPED','NEWBOTTLE',],inplace=True)
outputevents.set_index('ROW_ID',inplace=True)

transfers = pd.read_sql("""SELECT * 
                              FROM transfers
                              WHERE subject_id = {paciente} AND icustay_id = {icustay}""".format(paciente=paciente,icustay=estancia),mydb)
transfers.drop(columns=['SUBJECT_ID','HADM_ID','ICUSTAY_ID'],inplace=True)
transfers.set_index('ROW_ID', inplace=True)

st.subheader('Antecedentes')
st.table(diagnoses_icd)
# Indicar tambien si el paciente fue readmitido

if outputevents.shape[0] > 0:
  st.subheader('Producción de liquidos')
  st.table(outputevents) 

if callout.shape[0] > 0:
  st.subheader('Salida de alta')
  st.table(callout) 

if transfers.shape[0] > 0:
  st.subheader('Transferencias')
  st.table(transfers)  


st.subheader("Cuidadores a cargo del paciente")
if datetimeevents.shape[0] > 0:
    caregivers = pd.read_sql("""SELECT CGID,LABEL, DESCRIPTION 
                              FROM caregivers
                              WHERE cgid IN {cgids} """.format(cgids=tuple(datetimeevents['CGID'].unique())),mydb)
    caregivers.set_index('CGID',inplace=True)                  

    st.table(caregivers)

###################################################################################
st.markdown("<h1 style='text-align: center; color: white;'> Procedimientos</h1>", unsafe_allow_html=True)
st.markdown("---")

procedures_icd = pd.read_sql("""SELECT pro.seq_num ,dpro.short_title AS PROCEDIMIENTO
                              FROM procedures_icd pro
                              JOIN d_icd_procedures dpro
                              ON pro.icd9_code = dpro.icd9_code
                              WHERE subject_id = {paciente} AND hadm_id = {hadmid}
                              ORDER BY pro.seq_num""".format(paciente=paciente,hadmid=hadm_id),mydb)
procedures_icd.set_index('seq_num',inplace=True)

cptevents = pd.read_sql("""SELECT * 
                              FROM cptevents 
                              WHERE subject_id = {paciente} AND hadm_id = {hadmid}""".format(paciente=paciente,hadmid=hadm_id),mydb)
cptevents.drop(columns=['SUBJECT_ID','HADM_ID'],inplace=True)
cptevents.set_index('ROW_ID', inplace=True)

d_cpt = pd.DataFrame({})
for i in cptevents['CPT_CD'].unique():
  cpt = pd.read_sql("""SELECT * 
                              FROM d_cpt
                              WHERE mincodeinsubsection <= {cptcode} AND maxcodeinsubsection >= {cptcode} """.format(cptcode=i),mydb)
  d_cpt = pd.concat([d_cpt,cpt])


proceduresevents_mv = pd.read_sql("""SELECT d.LABEL ,d.CATEGORY, p.* 
                              FROM procedureevents_mv p
                              RIGHT JOIN d_items d
                              ON p.ITEMID = d.ITEMID
                              WHERE p.subject_id = {paciente} AND p.icustay_id = {icustay}""".format(paciente=paciente,icustay=estancia),mydb)
proceduresevents_mv.drop(columns=['ROW_ID','SUBJECT_ID','HADM_ID','ICUSTAY_ID','ITEMID','LINKORDERID','ORDERCATEGORYNAME','SECONDARYORDERCATEGORYNAME','CONTINUEINNEXTDEPT','CANCELREASON','COMMENTS_EDITEDBY','COMMENTS_CANCELEDBY','COMMENTS_DATE'],inplace=True)
proceduresevents_mv.set_index('ORDERID', inplace=True)



st.subheader('Anteriores a la estancia en UCI')
st.table(procedures_icd) # Referente a antecedentes

st.subheader('Aplicados en UCI')
if cptevents.shape[0] > 0:
  st.table(cptevents) 

if d_cpt.shape[0] > 0:
  st.table(d_cpt)

if proceduresevents_mv.shape[0] > 0:
  st.subheader('Ventilación Mecánica')
  st.table(proceduresevents_mv) # Condicional 

###################################################################################
st.markdown("<h1 style='text-align: center; color: white;'> Medicamentos</h1>", unsafe_allow_html=True)
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
st.markdown("<h1 style='text-align: center; color: white;'> Pruebas de Laboratorio y Microbiologicos</h1>", unsafe_allow_html=True)
st.markdown("---")

labevents2 = pd.read_sql("""SELECT * 
                              FROM labevents
                              WHERE subject_id = {paciente} AND hadm_id = {hadmid}""".format(paciente=paciente,hadmid=hadm_id),mydb)

microbiologyevents = pd.read_sql("""SELECT * 
                              FROM microbiologyevents
                              WHERE subject_id = {paciente} AND hadm_id = {hadmid}""".format(paciente=paciente,hadmid=hadm_id),mydb)

st.dataframe(labevents2)
st.dataframe(microbiologyevents)

if st.button('Descargar'):#Centrar boton en el layout
  st.write(dt.datetime.now())
