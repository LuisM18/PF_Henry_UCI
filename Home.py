import base64
import numpy as np  #
import pandas as pd  # 
import plotly.express as px  # 
import streamlit as st
import mysql.connector
from datetime import datetime
from PIL import Image

st.set_page_config(
    page_title="Analysis of the ICU area- Crowe Clinic",
    page_icon="🏥",
    layout="wide",
)

st.sidebar.markdown('###Links related to the database')

url = 'https://github.com/LuisM18/PF_Henry_UCI'
url2 = 'https://drive.google.com/drive/folders/19I8VMpCp3ylpVTRGGG0W4aGKt-4f664X'

st.sidebar.markdown(f'''
<a href={url}><button>GitHub</button></a>
''',
unsafe_allow_html=True)

st.sidebar.markdown(f'''
<a href={url2}><button>Database</button></a>
''',
unsafe_allow_html=True)

############### Conexion SQL #######################
mydb = mysql.connector.connect(
  host= st.secrets["DB_HOST"],
  user=st.secrets["DB_USER"],
  password=st.secrets["DB_PASSWORD"],
  database="proyectdb"
)

#Logo y titulo 
col1, col2, col3= st.columns([1,5,1])
with col1:
    croweclinic = Image.open('./images/croweclinichdwithout.png')
    st.image(croweclinic, width = 175)
with col3:
    datasight = Image.open('./images/datasighthdwithoutmine.png')
    st.image(datasight, width = 175)

st.markdown("<h1 style='text-align: center; color: white;'>Analysis of the Crowe Clinic ICU area</h1>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align: right; color: white;'>By DataSight Consulting</h3>", unsafe_allow_html=True)

with open('./images/a_photography_of_Crowe clinic_hospital6.png', "rb") as image_file:
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


####################### Crear KPIs
st.markdown("<h3 style='text-align: center; color: white;'>Key Perfomance Indicators</h3>", unsafe_allow_html=True)
placeholder = st.empty()

## Tasa Mortalidad
def tasa_mortalidad(admissions):

    admissions['dischtime_year'] = admissions['DISCHTIME'].dt.year
    admissions['dischtime_month'] = admissions['DISCHTIME'].dt.month

    tasa = pd.DataFrame(admissions.groupby(['dischtime_year','dischtime_month'])['HOSPITAL_EXPIRE_FLAG'].apply(lambda x: (x.sum()/x.count())))
    tasa.rename(columns={'HOSPITAL_EXPIRE_FLAG':'tasa_mortalidad'},inplace=True)

    return tasa

## Tasa Reingreso
def tasa_reingreso(admissions):
    admissions['ADMITTIME_YEAR'] = admissions['ADMITTIME'].dt.year
    admissions['ADMITTIME_MONTH'] = admissions['ADMITTIME'].dt.month

    tasa = pd.DataFrame(admissions.groupby(['ADMITTIME_YEAR','ADMITTIME_MONTH'])['SUBJECT_ID'].apply(lambda x: (x.count()-1)/x.count()))
    tasa.rename(columns={'SUBJECT_ID':'tasa_reingreso'},inplace=True)

    return tasa

## Tiempo de estancia promedio
def tiempo_estancia_promedio(icustay):

    icustay['month_outtime'] = icustay['OUTTIME'].dt.month
    icustay['year_outtime'] = icustay['OUTTIME'].dt.year

    tiempo = pd.DataFrame(icustay.groupby(['year_outtime','month_outtime'])['LOS'].mean())
    tiempo.rename(columns={'LOS':'tiempo_estancia_promedio'},inplace=True)

    return tiempo

## Top 5 diagnosticos
def top5_diagnostico(admissions):
    return pd.DataFrame(admissions['DIAGNOSIS'].value_counts()).head(5)

def delta(expresion):
    if 'nan' in expresion :
        return "0 %"
    else: 
        return expresion

############################################################
admissions = pd.read_sql("""SELECT *
                            FROM admissions_hechos""",mydb,parse_dates=['ADMITTIME','DISCHTIME'])

mortalidad = tasa_mortalidad(admissions)

reingreso = tasa_reingreso(admissions)

icustays = pd.read_sql("""SELECT *
                            FROM icustay_hechos""",mydb,parse_dates=['INTIME','OUTTIME'])

tiempo = tiempo_estancia_promedio(icustays)

##########################################################

with placeholder.container():

    # creando los kpis
    kpi1, kpi2, kpi3 = st.columns(3)


    kpi1.metric(
        label = "Mortality rate last month",
        value = f"{round(mortalidad.iloc[-1,-1]*100,2)} % ",
        delta = delta(f"{round((mortalidad.iloc[-1,-1]-mortalidad.iloc[-2,-1]/mortalidad.iloc[-2,-1])*100,2)} % "),
        help = 'The goal is to reduce or maintain the mortality rate by up to 20%'
    )


    kpi2.metric(
        label = "Readmissions rate last month",
        value = f" {round(reingreso.iloc[-1,-1],2)} %",
        delta = delta(f"{round((reingreso.iloc[-1,-1]-reingreso.iloc[-2,-1]/reingreso.iloc[-2,-1])*100,2)} % "),
        help = 'The goal is to reduce readmissions as much as possible.'
    )


kpi3.metric(
            label="Average length of stay in the ICU last month",
            value= f"{round(tiempo.iloc[-1,-1])} days",
            delta= f"{round((tiempo.iloc[-1,-1]-tiempo.iloc[-2,-1]/tiempo.iloc[-2,-1])*100,2)} % ",
            help = 'The objective is to reduce and/or maintain the stay time of 5 days'
        )    

####################################################################Top 5################################
st.markdown("<h3 style='text-align: center; color: white;'>Top 5 most frequent diagnoses</h3>", unsafe_allow_html=True)
top5 = top5_diagnostico(admissions)
fig = px.bar(top5,labels=dict(value='Cases',index='Diagnose'))
fig.update_layout(showlegend=False)
st.plotly_chart(fig,use_container_width=True)       

########################################################################## Mortalidad #######################################
st.markdown("<h3 style='text-align: center; color: white;'>Mortality rate by month and year</h3>", unsafe_allow_html=True)
max_value = admissions['DISCHTIME'].max().to_pydatetime()
min_value = admissions['DISCHTIME'].min().to_pydatetime()
mind, maxd = st.slider('Select date range',value=(min_value,max_value))
admissions = admissions[(admissions['DISCHTIME'] > mind) & (admissions['DISCHTIME'] < maxd)]

tasa = tasa_mortalidad(admissions)
y = tasa['tasa_mortalidad']
yearmonth = tasa.index.to_series().apply(lambda x: '{0}-{1}'.format(*x))

fig3 = px.line(x = yearmonth.values,y = y,labels=dict(y='Mortality rate',x='Date'))
fig3.update_yaxes(tickformat=".2%")
fig3.update_xaxes(tickformat='%b\n%Y')
st.plotly_chart(fig3,use_container_width=True)


######################################################################33 Tiempo de Estancia ###############################
st.markdown("<h3 style='text-align: center; color: white;'>Average length of stay in ICU by month and year</h3>", unsafe_allow_html=True)
max_value = icustays['OUTTIME'].max().to_pydatetime()
min_value = icustays['OUTTIME'].min().to_pydatetime()
mindd, maxdd = st.slider('Select date range',value=(min_value,max_value))
icustays = icustays[(icustays['OUTTIME'] > mindd) & (icustays['OUTTIME'] < maxdd)]

tiempo = tiempo_estancia_promedio(icustays)
y = tiempo['tiempo_estancia_promedio']
yearmonth = tiempo.index.to_series().apply(lambda x: '{0}-{1}'.format(*x))

fig4 = px.line(x = yearmonth.values,y = y,labels=dict(x='Date',y='Average time(days)'))
fig4.update_xaxes(tickformat='%b\n%Y')
st.plotly_chart(fig4,use_container_width=True)

###################################################### Tasa Reingreso ########################
st.markdown("<h3 style='text-align: center; color: white;'>Readmissions rate by month and year</h3>", unsafe_allow_html=True)
max_value = admissions['ADMITTIME'].max().to_pydatetime()
min_value = admissions['ADMITTIME'].min().to_pydatetime()
mind, maxd = st.slider('Select date range',value=(min_value,max_value))
admissions = admissions[(admissions['ADMITTIME'] > mind) & (admissions['ADMITTIME'] < maxd)]

reingreso = tasa_reingreso(admissions)
y = reingreso['tasa_reingreso']
yearmonth = reingreso.index.to_series().apply(lambda x: '{0}-{1}'.format(*x))

fig5 = px.line(x = yearmonth.values,y = y,labels=dict(y='Readmission rate',x='Date'))
fig5.update_yaxes(tickformat=".2%")
fig5.update_xaxes(tickformat='%b\n%Y')
st.plotly_chart(fig5,use_container_width=True)
