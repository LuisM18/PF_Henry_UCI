import pandas as pd  # 
import plotly.express as px  # 
import streamlit as st 
import mysql.connector
import datetime as dt
import streamlit.components.v1 as components
import requests

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
cptevents.drop(columns=['ROW_ID','SUBJECT_ID','HADM_ID','CPT_NUMBER','TICKET_ID_SEQ'],inplace=True)
cptevents.set_index('CPT_CD', inplace=True)

d_cpt = pd.DataFrame({})
for i in cptevents.index.unique():
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

prescriptionsf = prescriptions[prescriptions['ICUSTAY_ID'] == 0]
prescriptionsf.drop(columns=['SUBJECT_ID','HADM_ID','ICUSTAY_ID','DRUG_NAME_POE','DRUG_NAME_GENERIC'],inplace=True)
prescriptionsf.set_index('ROW_ID',inplace=True)

prescriptionsuci = prescriptions[prescriptions['ICUSTAY_ID'] == 0]
prescriptionsuci.drop(columns=['SUBJECT_ID','HADM_ID','ICUSTAY_ID','DRUG_NAME_POE','DRUG_NAME_GENERIC'],inplace=True)
prescriptionsuci.set_index('ROW_ID',inplace=True)

inputevents_cv = pd.read_sql("""SELECT d.LABEL ,d.CATEGORY, i.*  
                              FROM inputevents_cv i
                              RIGHT JOIN d_items d
                              ON i.ITEMID = d.ITEMID
                              WHERE i.subject_id = {paciente} AND i.icustay_id = {icustay}""".format(paciente=paciente,icustay=estancia),mydb)
inputevents_cv.drop(columns=['ROW_ID','SUBJECT_ID','HADM_ID','ICUSTAY_ID','ITEMID','LINKORDERID'],inplace=True)
inputevents_cv.set_index('ORDERID',inplace=True)

inputevents_mv = pd.read_sql("""SELECT d.LABEL ,d.CATEGORY, i.*  
                              FROM inputevents_mv i
                              RIGHT JOIN d_items d
                              ON i.ITEMID = d.ITEMID
                              WHERE i.subject_id = {paciente} AND i.icustay_id = {icustay}""".format(paciente=paciente,icustay=estancia),mydb)
inputevents_mv.drop(columns=['ROW_ID','SUBJECT_ID','HADM_ID','ICUSTAY_ID','ITEMID','LINKORDERID','CONTINUEINNEXTDEPT','CANCELREASON','COMMENTS_STATUS'],inplace=True)
inputevents_mv.set_index('ORDERID',inplace=True)


st.subheader('Fuera de la UCI')
if prescriptionsf.shape[0] > 0:
  st.table(prescriptionsf)
else: st.markdown('Ninguna')

st.subheader('Suministrados en UCI')
if prescriptionsuci.shape[0] > 0:
  st.table(prescriptionsuci)
else: st.markdown('Ninguna')


if inputevents_cv.shape[0] > 0:
  st.subheader('Via Intravenosa')
  st.table(inputevents_cv) #Intravenosos

if inputevents_mv.shape[0] > 0:
  st.subheader('Via Ventilación Mecánica')
  st.table(inputevents_mv) # Ventilacion Mecanica

###################################################################################
st.markdown("<h1 style='text-align: center; color: white;'> Pruebas de Laboratorio y Microbiologicos</h1>", unsafe_allow_html=True)
st.markdown("---")

labevents2 = pd.read_sql("""SELECT d.LABEL ,d.CATEGORY, lb.* 
                              FROM labevents lb
                              RIGHT JOIN d_items d
                              ON lb.ITEMID = d.ITEMID
                              WHERE lb.subject_id = {paciente} AND lb.hadm_id = {hadmid}""".format(paciente=paciente,hadmid=hadm_id),mydb)
labevents2.drop(columns=['SUBJECT_ID','HADM_ID','ITEMID'],inplace=True)
labevents2.set_index('ROW_ID',inplace=True)


microbiologyevents = pd.read_sql("""SELECT d.LABEL ,d.CATEGORY, m.*  
                              FROM microbiologyevents m
                              RIGHT JOIN d_items d
                              ON m.SPEC_ITEMID = d.ITEMID
                              WHERE m.subject_id = {paciente} AND m.hadm_id = {hadmid}""".format(paciente=paciente,hadmid=hadm_id),mydb)
microbiologyevents.drop(columns=['SUBJECT_ID','HADM_ID','SPEC_ITEMID'],inplace=True)
microbiologyevents.set_index('ROW_ID',inplace=True)

st.subheader('Laboratorios')
if labevents2.shape[0] > 0:
  st.table(labevents2)
  
st.subheader('Estudios microbiológicos')
if microbiologyevents.shape[0] > 0:
  st.table(microbiologyevents)


########################################################


@st.cache_data
def load_unpkg(src: str) -> str:
    return requests.get(src).text


HTML_2_CANVAS = load_unpkg("https://unpkg.com/html2canvas@1.4.1/dist/html2canvas.js")
JSPDF = load_unpkg("https://unpkg.com/jspdf@latest/dist/jspdf.umd.min.js")
BUTTON_TEXT = "Descargar"

if st.button(BUTTON_TEXT):
  NOMBRE = "{id_paciente}_{fecha}".format(id_paciente=paciente,fecha=dt.datetime.now().strftime('%Y%m%d_%I:%M%p'))
  components.html(
            f"""
<script>{HTML_2_CANVAS}</script>
<script>{JSPDF}</script>
<script>
const html2canvas = window.html2canvas
const {{ jsPDF }} = window.jspdf

const streamlitDoc = window.parent.document;
const stApp = streamlitDoc.querySelector('.main > .block-container');

const buttons = Array.from(streamlitDoc.querySelectorAll('.stButton > button'));
const pdfButton = buttons.find(el => el.innerText === '{BUTTON_TEXT}');
const docHeight = stApp.scrollHeight ;
const docWidth = stApp.scrollWidth ;

let topLeftMargin = 1.5;
let pdfWidth = docHeight + (topLeftMargin * 2);
let pdfHeight = (pdfWidth * 1.5) + (topLeftMargin * 2);
let canvasImageWidth = docWidth;
let canvasImageHeight = docHeight;

let totalPDFPages = Math.ceil(docHeight / pdfHeight)-1;

pdfButton.innerText = '{NOMBRE}';

html2canvas(stApp, {{ allowTaint: true }}).then(function (canvas) {{

    canvas.getContext('2d');
    let imgData = canvas.toDataURL("image/jpeg", 1.0);

    let pdf = new jsPDF('p', 'px', [pdfWidth, pdfHeight]);
    pdf.addImage(imgData, 'JPG', topLeftMargin, topLeftMargin, canvasImageWidth, canvasImageHeight);

    for (var i = 1; i <= totalPDFPages; i++) {{
        pdf.addPage();
        pdf.addImage(imgData, 'JPG', topLeftMargin, -(pdfHeight * i) + (topLeftMargin*4), canvasImageWidth, canvasImageHeight);
    }}

    pdf.save('{NOMBRE}.pdf');
    pdfButton.innerText = '{NOMBRE}';
}})

</script>
""",
            height=0,
            width=0,
        )







