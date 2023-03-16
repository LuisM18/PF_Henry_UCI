import base64
import numpy as np  #
import pandas as pd  # 
import plotly.express as px  # 
import streamlit as st
from datetime import datetime

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


with open('./images/a_photography_of_Crowe clinic_hospital3.png', "rb") as image_file:
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


# top-level filters
st.subheader('KPIs')
placeholder = st.empty()
# create KPIs

################## Cambios en SQl
df['dischtime'] = df.dischtime.apply(pd.to_datetime)

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
        label="Tasa de mortalidad último mes",
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
                label="Tiempo de estancia promedio en la UCI último mes",
                value=f"{round(tiempo.iloc[-1,-1])} días ",
                delta= 0
            )    

    st.markdown("### Top 5 de diagnósticos más frecuentes")
    top5 = top5_diagnostico(df)
    fig = px.bar(top5)
    fig.update_layout(showlegend=False)
    st.plotly_chart(fig,use_container_width=True)       

    st.markdown("### Tasa de mortalidad por mes y año")
    max_value = df['dischtime'].max()
    min_value = df['dischtime'].min()
    mind, maxd  = st.date_input('Seleccione el rango de fecha', [min_value, max_value])
    maxd = datetime.strptime(str(maxd), '%Y-%m-%d')
    mind = datetime.strptime(str(mind), '%Y-%m-%d')
    df = df[(df['dischtime'] > mind) & (df['dischtime'] < maxd)]
    tasa = tasa_mortalidad(df)
    y = tasa['tasa_mortalidad']
    yearmonth = tasa.index.to_series().apply(lambda x: '{0}-{1}'.format(*x))
    fig3 = px.line(x = yearmonth.values,y = y*100)
    st.plotly_chart(fig3,use_container_width=True)
    
    st.markdown("### Tiempo promedio de estancia en UCI en días por mes y año")
    max_value = icustays['outtime'].max()
    min_value = icustays['outtime'].min()
    mind, maxd  = st.date_input('Seleccione el rango de fecha', [min_value, max_value])
    maxd = datetime.strptime(str(maxd), '%Y-%m-%d')
    mind = datetime.strptime(str(mind), '%Y-%m-%d')
    icustays = icustays[(icustays['outtime'] > mind) & (icustays['outtime'] < maxd)]
    tiempo = tiempo_estancia_promedio(icustays)
    y = tiempo['tiempo_estancia_promedio']
    yearmonth = tiempo.index.to_series().apply(lambda x: '{0}-{1}'.format(*x))
    fig4 = px.line(x = yearmonth.values,y = y)
    st.plotly_chart(fig4,use_container_width=True)

    st.markdown("### Vista de la base de datos")
    lista_de_tablas = ['ADMISSIONS','LABEVENTS','CHARTEVENTS']
    selectedtable = st.selectbox("Selecciona la tabla", lista_de_tablas, key="4")
    dataframe = pd.read_csv('./EDA_UCI/dataset/'+selectedtable+ '.csv')
    st.dataframe(dataframe)