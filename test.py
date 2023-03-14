import base64
import numpy as np  #
import pandas as pd  # 
import plotly.express as px  # 
import streamlit as st  # 🎈 

st.set_page_config(
    page_title="Análisis del área UCI- Crowe Clinic",
    page_icon="🏥",
    layout="wide",
)

#leemos los datasets
admissions = "./dataset/ADMISSIONS.csv"
labevents = pd.read_csv("./dataset/LABEVENTS.csv")
labitems = pd.read_csv("./dataset/D_LABITEMS.csv")
drgcodes = pd.read_csv('./dataset/DRGCODES.csv')
labevents = pd.read_csv('./dataset/LABEVENTS.csv')
micro = pd.read_csv('./dataset/MICROBIOLOGYEVENTS.csv')
prescriptions = pd.read_csv('./dataset/PRESCRIPTIONS.csv')
procedures = pd.read_csv('./dataset/PROCEDURES_ICD.csv')
admissions = pd.read_csv('./dataset/Admissions.csv')
callout = pd.read_csv('./dataset/callout.csv')
icustays = pd.read_csv('./dataset/icustays.csv')
patients = pd.read_csv('./dataset/patients.csv')
services = pd.read_csv('./dataset/services.csv')
caregivers = pd.read_csv('./dataset/CAREGIVERS.csv')
chartevents = pd.read_csv('./dataset/CHARTEVENTS.csv')
datetimeevents = pd.read_csv('./dataset/DATETIMEEVENTS.csv')
imputeventscv = pd.read_csv('./dataset/INPUTEVENTS_CV.csv')
imputeventsmv = pd.read_csv('./dataset/INPUTEVENTS_MV.csv')
transfers = pd.read_csv('./dataset/TRANSFERS.csv')
dcpt = pd.read_csv('./dataset/D_CPT.csv')
ddiagnoses = pd.read_csv('./dataset/D_ICD_DIAGNOSES.csv')
dprocedures = pd.read_csv('./dataset/D_ICD_PROCEDURES.csv')
ditems = pd.read_csv('./dataset/D_ITEMS.csv')
dlabitems = pd.read_csv('./dataset/D_LABITEMS.csv')
noteevents= pd.read_csv('./dataset/NOTEEVENTS.csv')
outputevents= pd.read_csv('./dataset/OUTPUTEVENTS.csv')
procedureevents_mv = pd.read_csv('./dataset/PROCEDUREEVENTS_MV.csv')
cptevents = pd.read_csv('./dataset/CPTEVENTS.csv')
diagnoses_icd = pd.read_csv('./dataset/DIAGNOSES_ICD.csv') 

# read csv from a URL
@st.cache_data
def get_data() -> pd.DataFrame:
    return admissions

df = get_data()

# dashboard title
st.title("Análisis del área UCI de Crowe Clinic ")
st.subheader(" Por DataSight Consulting")
with open('./images/icu.jpg', "rb") as image_file:
    encoded_string = base64.b64encode(image_file.read())
st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url(data:image/{"gif"};base64,{encoded_string.decode()});
            background-attachment: fixed;
            background-size: cover
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

# top-level filters
st.subheader('KPIs')
adm_filter = st.selectbox("Selecciona el tipo de admisión", pd.unique(df["admission_type"]),key="1")
insurance = st.selectbox("Selecciona el seguro del paciente", pd.unique(df['insurance']),key="2")
# selecciona la etnia
etnia = st.multiselect(
    'Selecciona la etnia del paciente', pd.unique(df["ethnicity"]), default = 'WHITE')

# creating a single-element container
placeholder = st.empty()

# dataframe filter
df = df[df["admission_type"] == adm_filter ]
df = df[df["insurance"] == insurance ]
df = df[df["ethnicity"].isin(etnia)]

df["diagnosis_new"] = df["diagnosis"] * np.random.choice(range(1, 5))
df["marital_status_new"] = df["marital_status"] * np.random.choice(range(1, 5))

# creating KPIs

with placeholder.container():

    # creando los kpis
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)

    # fill in those three columns with respective metrics or KPIs

    # tasa de mortalidad
    filtered = df[df['discharge_location'].str.contains('DEAD')]
    death_ratio = filtered.shape[0] / df['discharge_location'].shape[0]
    # tasa de reingreso
    df.drop_duplicates(inplace=True)
    df['subject_id'].value_counts()
    #¿Qué es el índice de reingreso?
    #El reingreso ha sido definido como todo ingreso con idéntico diagnóstico principal en los 30 días siguientes al alta.
    tasa_reingreso = df.groupby(['subject_id','diagnosis'])['subject_id'].count()
    tasa_re = tasa_reingreso.value_counts()
    tasa_re_2 = tasa_re[tasa_re.index > 1].sum() / tasa_re.sum() * 100

    kpi1.metric(
        label="Tasa de mortalidad",
        value= f"{round(death_ratio*100,2)} % ",
        delta=-10 + death_ratio,
    )

    kpi2.metric(
        label="Tasa de reingreso",
        value= f" {round(tasa_re_2,2)} %",
        delta=-10 + tasa_re_2,
    )
    kpi3.metric(
                label="Tiempo de estancia en la UCI",
                value=f"{round(40,2)} % ",
                delta=-round(40 / 100) * 100,
            )
    
    kpi4.metric(
        label="Tasa de reinfecciones",
        value=f" {round(60,2)} % ",
        delta=-round(40 / 100) * 100,
    )

    # create two columns for charts
    fig_col1, fig_col2 = st.columns(2)
    with fig_col1:
        st.markdown("### Top 5 de diagnósticos más frecuentes")
        x = df["diagnosis"].value_counts().keys()
        y =  df["diagnosis"].value_counts().values
        top5_d = x[0:5]
        top5_dy = y[0:5]
        fig = px.bar(
            data_frame=df, x=top5_d, y= top5_dy 
        )
        st.write(fig)
        
    with fig_col2:
        st.markdown("### Resultados de las pruebas de laboratorio por paciente")
        lab = labevents.merge(labitems, left_on='itemid', right_on='itemid')
        count = 0
        lab.drop_duplicates(inplace=True)
        user_filter = st.selectbox("Selecciona el id del paciente", pd.unique(lab['subject_id']),key= count)
        count =+1
        filtered_data = lab[lab['subject_id'] == user_filter]
        st.dataframe(filtered_data)

    st.header('Análisis descriptivo')
    st.markdown("### -----------------------------------------------------------------------------")
    fig3, fig4 = st.columns(2)

    with fig3:
        st.markdown("### Pacientes por sexo")
        patient = patients.merge(df, left_on='subject_id', right_on='subject_id')
        x = patient['gender'].value_counts().keys()
        y = patient['gender'].value_counts().values
        fig3 = px.bar(data_frame=patient, x=x, y = y )
        st.write(fig3)

    with fig4:
        st.markdown("### Pacientes por estado civil")
        patient = patients.merge(df, left_on='subject_id', right_on='subject_id')
        x = patient['marital_status'].value_counts().keys()
        y = patient['marital_status'].value_counts().values
        fig4 = px.bar(data_frame=patient, x=x, y =y )
        st.write(fig4)
    
    fig5, fig6 = st.columns(2)

    with fig5:
        st.markdown("### Pacientes por edad")
        patient = patients.merge(df, left_on='subject_id', right_on='subject_id')
        yearnac = pd.to_datetime(patient['dob'])
        yearmu = pd.to_datetime(patient['dod'])
        patient['age'] = yearmu.dt.year - yearnac.dt.year
        fig5 = px.histogram(data_frame=patient, x="age")
        st.write(fig5)

    with fig6:
        st.markdown("### Pacientes por admission_location")
        patient = patients.merge(df, left_on='subject_id', right_on='subject_id')
        x = patient['admission_location'].value_counts().keys()
        y = patient['admission_location'].value_counts().values
        fig6 = px.bar(data_frame=patient, x=x, y =y)
        st.write(fig6)

    st.markdown("### Vista de la base de datos")
    lista_de_tablas = ['admissions','labevents','chartevents']
    selectedtable = st.selectbox("Selecciona la tabla", lista_de_tablas, key="4")
    dataframe = pd.read_csv('./dataset/'+selectedtable+ '.csv')
    st.dataframe(dataframe)