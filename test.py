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


######### Temporal ##########
#leemos los datasets

labevents = pd.read_csv("./EDA_UCI/dataset/LABEVENTS.csv")
labitems = pd.read_csv("./EDA_UCI/dataset/D_LABITEMS.csv")
admissions = pd.read_csv('./EDA_UCI/dataset/ADMISSIONS.csv')
icustays = pd.read_csv('./EDA_UCI/dataset/ICUSTAYS.csv')
ditems = pd.read_csv('./EDA_UCI/dataset/D_ITEMS.csv')
dlabitems = pd.read_csv('./EDA_UCI/dataset/D_LABITEMS.csv')
patients = pd.read_csv('./EDA_UCI/dataset/PATIENTS.csv')


# read csv from a URL
@st.cache_data
def get_data() -> pd.DataFrame:
    return admissions

df = get_data()

# dashboard title
st.title(" Análisis del área UCI de Crowe Clinic ")
st.subheader(" Por DataSight Consulting")

'''
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
'''

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
df = df[(df["admission_type"] == adm_filter) & (df["insurance"] == insurance) & (df["ethnicity"].isin(etnia))]


df["diagnosis_new"] = df["diagnosis"] * np.random.choice(range(1, 5))
df["marital_status_new"] = df["marital_status"] * np.random.choice(range(1, 5))

# create KPIs

################## Cambios en SQl
admissions['dischtime'] = admissions.dischtime.apply(pd.to_datetime)

icustays['intime'] = icustays.intime.apply(pd.to_datetime)
icustays['outtime'] = icustays.outtime.apply(pd.to_datetime)


## Tasa Mortalidad
def tasa_mortalidad(admissions):
    admissions['dischtime_year'] = admissions.dischtime.dt.year
    admissions['dischtime_month'] = admissions.dischtime.dt.month

    tasa = pd.DataFrame(admissions.groupby(['dischtime_year','dischtime_month'])['hospital_expire_flag'].apply(lambda x: (x.sum()/x.count())))
    tasa.rename(columns={'hospital_expire_flag':'tasa_mortalidad'},inplace=True)

    return tasa

## Tasa Reingreso
df.drop_duplicates(inplace=True)
df['subject_id'].value_counts()
#¿Qué es el índice de reingreso?
#El reingreso ha sido definido como todo ingreso con idéntico diagnóstico principal en los 30 días siguientes al alta.
tasa_reingreso = df.groupby(['subject_id','diagnosis'])['subject_id'].count()
tasa_re = tasa_reingreso.value_counts()
tasa_re_2 = tasa_re[tasa_re.index > 1].sum() / tasa_re.sum() * 100

## Tiempo de estancia promedio
def tiempo_estancia_promedio(icustay):
    icustay['month_outtime'] = icustay.outtime.dt.month
    icustay['year_outtime'] = icustay.outtime.dt.year

    tiempo = pd.DataFrame(icustay.groupby(['year_outtime','month_outtime'])['los'].mean())
    tiempo.rename(columns={'los':'tiempo_estancia_promedio'},inplace=True)

    return tiempo

## Top 5 diagnosticos
def top5_diagnostico(admissions):
    return pd.DataFrame(admissions.diagnosis.value_counts()).head(5)



with placeholder.container():

    # creando los kpis
    kpi1, kpi2, kpi3 = st.columns(3)

    mortalidad = tasa_mortalidad(df)
    kpi1.metric(
        label="Tasa de mortalidad",
        value= f"{round(mortalidad.iloc[-1,-1]*100,2)} % ",
        delta= 0
    )

    kpi2.metric(
        label="Tasa de reingreso",
        value= f" {round(tasa_re_2,2)} %",
        delta= 0,
    )

    tiempo = tiempo_estancia_promedio(icustays)
    kpi3.metric(
                label="Tiempo de estancia promedio en la UCI",
                value=f"{round(tiempo.iloc[-1,-1])} dias ",
                delta= 0
            )    

    # create two columns for charts
    fig_col1, fig_col2 = st.columns([2,3])
    with fig_col1:
        st.markdown("### Top 5 de diagnósticos más frecuentes")
        top5 = top5_diagnostico(df)

        fig = px.bar(top5)
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig,use_container_width=True)
        
    with fig_col2:
        st.markdown("### Resultados de las pruebas de laboratorio por paciente")
        lab = labevents.merge(labitems, left_on='itemid', right_on='itemid')
        count = 0
        lab.drop_duplicates(inplace=True)
        user_filter = st.selectbox("Selecciona el id del paciente", pd.unique(lab['subject_id']),key= count)
        count =+1
        filtered_data = lab[lab['subject_id'] == user_filter]
        st.dataframe(use_container_width=True)

    st.header('Análisis descriptivo')
    st.markdown("---")
    fig3, fig4 = st.columns(2)

    with fig3:
        st.markdown("### Pacientes por sexo")
        patient = patients.merge(df, left_on='subject_id', right_on='subject_id')
        x = patient['gender'].value_counts().keys()
        y = patient['gender'].value_counts().values
        fig3 = px.bar(data_frame=patient, x=x, y = y )
        st.plotly_chart(fig3,use_container_width=True)

    with fig4:
        st.markdown("### Pacientes por estado civil")
        patient = patients.merge(df, left_on='subject_id', right_on='subject_id')
        x = patient['marital_status'].value_counts().keys()
        y = patient['marital_status'].value_counts().values
        fig4 = px.bar(data_frame=patient, x=x, y =y )
        st.plotly_chart(fig4,use_container_width=True)
    
    fig5, fig6 = st.columns(2)

    with fig5:
        st.markdown("### Pacientes por edad")
        patient = patients.merge(df, left_on='subject_id', right_on='subject_id')
        yearnac = pd.to_datetime(patient['dob'])
        yearmu = pd.to_datetime(patient['dod'])
        patient['age'] = yearmu.dt.year - yearnac.dt.year
        fig5 = px.histogram(data_frame=patient, x="age")
        st.plotly_chart(fig5,use_container_width=True)

    with fig6:
        st.markdown("### Pacientes por admission_location")
        patient = patients.merge(df, left_on='subject_id', right_on='subject_id')
        x = patient['admission_location'].value_counts().keys()
        y = patient['admission_location'].value_counts().values
        fig6 = px.bar(data_frame=patient, x=x, y =y)
        st.plotly_chart(fig6,use_container_width=True)

    st.markdown("### Vista de la base de datos")
    lista_de_tablas = ['ADMISSIONS','LABEVENTS','CHARTEVENTS']
    selectedtable = st.selectbox("Selecciona la tabla", lista_de_tablas, key="4")
    dataframe = pd.read_csv('./EDA_UCI/dataset/'+selectedtable+ '.csv')
    st.dataframe(dataframe)