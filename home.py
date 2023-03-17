import base64
import numpy as np  #
import pandas as pd  # 
import plotly.express as px  # 
import streamlit as st
import mysql.connector
from datetime import datetime


st.set_page_config(
    page_title="Análisis del área UCI- Crowe Clinic",
    page_icon="🏥",
    layout="wide",
)

st.sidebar.markdown('### Links relacionados a la base de datos')

url = 'https://github.com/LuisM18/PF_Henry_UCI'
url2 = 'https://drive.google.com/drive/folders/19I8VMpCp3ylpVTRGGG0W4aGKt-4f664X'

st.sidebar.markdown(f'''
<a href={url}><button>GitHub</button></a>
''',
unsafe_allow_html=True)

st.sidebar.markdown(f'''
<a href={url2}><button>Base de Datos</button></a>
''',
unsafe_allow_html=True)

############### Conexion SQL #######################
mydb = mysql.connector.connect(
  host= st.secrets["DB_HOST"],
  user=st.secrets["DB_USER"],
  password=st.secrets["DB_PASSWORD"],
  database="proyectdb"
)

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


####################### Crear KPIs
st.subheader('KPIs')
placeholder = st.empty()

## Tasa Mortalidad
def tasa_mortalidad(admissions):

    admissions['dischtime_year'] = admissions['DISCHTIME'].dt.year
    admissions['dischtime_month'] = admissions['DISCHTIME'].dt.month

    tasa = pd.DataFrame(admissions.groupby(['dischtime_year','dischtime_month'])['HOSPITAL_EXPIRE_FLAG'].apply(lambda x: (x.sum()/x.count())))
    tasa.rename(columns={'HOSPITAL_EXPIRE_FLAG':'tasa_mortalidad'},inplace=True)

    return tasa

## Tasa Reingreso
#df.drop_duplicates(inplace=True)
#df['subject_id'].value_counts()
#¿Qué es el índice de reingreso?
#El reingreso ha sido definido como todo ingreso con idéntico diagnóstico principal en los 30 días siguientes al alta.
#tasa_reingreso = df.groupby(['subject_id','diagnosis'])['subject_id'].count()
#tasa_re = tasa_reingreso.value_counts()
#tasa_re_2 = tasa_re[tasa_re.index > 1].sum() / tasa_re.sum() * 100

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


with placeholder.container():

    # creando los kpis
    kpi1, kpi2, kpi3 = st.columns(3)

    admissions = pd.read_sql("""SELECT *
                             FROM admissions""",mydb,parse_dates=['DISCHTIME'])


    mortalidad = tasa_mortalidad(admissions)
    kpi1.metric(
        label="Tasa de mortalidad último mes",
        value= f"{round(mortalidad.iloc[-1,-1]*100,2)} % ",
        delta= f"{round((mortalidad.iloc[-1,-1]-mortalidad.iloc[-2,-1]/mortalidad.iloc[-2,-1])*100,2)} % "
    )

    kpi2.metric(
        label="Tasa de reingreso",
        value= f" {round(2.8,2)} %",
        delta= 0
    )

icustays = pd.read_sql("""SELECT *
                            FROM icustays""",mydb,parse_dates=['INTIME','OUTTIME'])

tiempo = tiempo_estancia_promedio(icustays)
kpi3.metric(
            label="Tiempo de estancia promedio en la UCI último mes",
            value= f"{round(tiempo.iloc[-1,-1])} días ",
            delta= f"{round((tiempo.iloc[-1,-1]-tiempo.iloc[-2,-1]/tiempo.iloc[-2,-1])*100,2)} % "
        )    

st.markdown("### Top 5 de diagnósticos más frecuentes")
top5 = top5_diagnostico(admissions)
fig = px.bar(top5,labels=dict(value='Casos',index='Diagnóstico'))
fig.update_layout(showlegend=False)
st.plotly_chart(fig,use_container_width=True)       

st.markdown("### Tasa de mortalidad por mes y año")
max_value = admissions['DISCHTIME'].max()
min_value = admissions['DISCHTIME'].min()
mind, maxd  = st.date_input('Seleccione el rango de fecha', [min_value, max_value])
maxd = datetime.strptime(str(maxd), '%Y-%m-%d')
mind = datetime.strptime(str(mind), '%Y-%m-%d')
admissions = admissions[(admissions['DISCHTIME'] > mind) & (admissions['DISCHTIME'] < maxd)]

tasa = tasa_mortalidad(admissions)
y = tasa['tasa_mortalidad']
yearmonth = tasa.index.to_series().apply(lambda x: '{0}-{1}'.format(*x))

fig3 = px.line(x = yearmonth.values,y = y,labels=dict(y='Porcentaje de Mortalidad',x='Fecha'))
fig3.update_yaxes(tickformat=".2%")
fig3.update_xaxes(tickformat='%b\n%Y')
st.plotly_chart(fig3,use_container_width=True)

st.markdown("### Tiempo promedio de estancia en UCI por mes y año")
max_value = icustays['OUTTIME'].max()
min_value = icustays['OUTTIME'].min()

mind, maxd  = st.date_input('Seleccione el rango de fecha', [min_value, max_value])
maxd = datetime.strptime(str(maxd), '%Y-%m-%d')
mind = datetime.strptime(str(mind), '%Y-%m-%d')

icustays = icustays[(icustays['OUTTIME'] > mind) & (icustays['OUTTIME'] < maxd)]
y = tiempo['tiempo_estancia_promedio']
yearmonth = tiempo.index.to_series().apply(lambda x: '{0}-{1}'.format(*x))
fig4 = px.line(x = yearmonth.values,y = y,labels=dict(x='Fecha',y='Tiempo promedio (dias)'))
fig4.update_xaxes(tickformat='%b\n%Y')
st.plotly_chart(fig4,use_container_width=True)

