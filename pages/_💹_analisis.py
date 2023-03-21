import base64
import numpy as np  #
import pandas as pd  # 
import plotly.express as px  # 
import streamlit as st  # 🎈
import mysql.connector
from datetime import datetime

mydb = mysql.connector.connect(
  host= st.secrets["DB_HOST"],
  user=st.secrets["DB_USER"],
  password=st.secrets["DB_PASSWORD"],
  database="proyectdb"
)

################## Cargar Data ##########################
admissions = pd.read_sql("""SELECT *
                            FROM admissions_hechos""",mydb,parse_dates=['INTIME','OUTTIME'])

icustays = pd.read_sql("""SELECT *
                            FROM icustays""",mydb)

patients = pd.read_sql("""SELECT *
                            FROM patient""",mydb)

prescriptions = pd.read_sql("""SELECT *
                            FROM prescriptions""",mydb)

inputevents_cv = pd.read_sql("""SELECT *
                            FROM inputevents_cv""",mydb)

inputevents_mv = pd.read_sql("""SELECT *
                            FROM inputevents_mv""",mydb)

outputevents = pd.read_sql("""SELECT *
                            FROM outputevents""",mydb)

proceduresevents_mv = pd.read_sql("""SELECT *
                            FROM procedureevents_mv""",mydb)


###################################################################################
d_items = pd.read_csv('./EDA_UCI/dataset/D_ITEMS.csv')
st.sidebar.markdown("# Análisis descriptivo de las tablas")
st.sidebar.markdown("# Seleccione las tablas")
tables = ['patients','prescriptions','icustays','inputevents_mv','cptevents']
tabla_seleccionada = st.sidebar.selectbox('Seleccione las tablas',tables)
st.header('Análisis descriptivo')
st.markdown("---")
if tabla_seleccionada == 'patients':
   
    adm_filter = st.selectbox("Selecciona el tipo de admisión", pd.unique(admissions["ADMISSION_TYPE"]),key="1")
    insurance = st.selectbox("Selecciona el seguro del paciente", pd.unique(admissions['INSURANCE']),key="2")
    # selecciona la etnia
    etnia = st.multiselect(
        'Selecciona la etnia del paciente', pd.unique(admissions["ETHNIVITY"]), default = 'WHITE')

    # creating a single-element container
    placeholder = st.empty()

    # dataframe filter
    admissions = admissions[(admissions["ADMISSION_TYPE"] == adm_filter) & (admissions["INSURANCE"] == insurance) & (admissions["ethnicity"].isin(etnia))]
    fig3, fig4 = st.columns(2)
    fig5, fig6 = st.columns(2)


    with fig3:
        st.markdown("### Pacientes por sexo")
        patient = patients.merge(admissions, left_on='subject_id', right_on='subject_id')
        x = patient['gender'].value_counts().keys()
        y = patient['gender'].value_counts().values
        fig3 = px.bar(data_frame=patient, x=x, y = y )
        st.plotly_chart(fig3,use_container_width=True)

    with fig4:
        st.markdown("### Pacientes por estado civil")
        patient = patients.merge(admissions, left_on='subject_id', right_on='subject_id')
        x = patient['marital_status'].value_counts().keys()
        y = patient['marital_status'].value_counts().values
        fig4 = px.bar(data_frame=patient, x=x, y =y )
        st.plotly_chart(fig4,use_container_width=True)

    with fig5:
        st.markdown("### Pacientes por edad")
        patient = patients.merge(admissions, left_on='subject_id', right_on='subject_id')
        yearnac = pd.to_datetime(patient['dob'])
        yearmu = pd.to_datetime(patient['dod'])
        patient['age'] = yearmu.dt.year - yearnac.dt.year
        fig5 = px.histogram(data_frame=patient, x="age")
        st.plotly_chart(fig5,use_container_width=True)

    with fig6:
        st.markdown("### Pacientes por admission_location")
        patient = patients.merge(admissions, left_on='subject_id', right_on='subject_id')
        x = patient['admission_location'].value_counts().keys()
        y = patient['admission_location'].value_counts().values
        fig6 = px.bar(data_frame=patient, x=x, y =y)
        st.plotly_chart(fig6,use_container_width=True)

if tabla_seleccionada == 'prescriptions':
    fig3, fig4 = st.columns(2)
    fig5, fig6 = st.columns(2)
    with fig3:
        st.markdown("### Medicamentos más utilizados")
        x = prescriptions['DRUG'].value_counts().keys()
        y = prescriptions['DRUG'].value_counts().values
        fig3 = px.bar(data_frame=prescriptions, x=x, y = y )
        st.plotly_chart(fig3,use_container_width=True)

    with fig4:
        st.markdown("### Ruta de la medicación")
        x = prescriptions['ROUTE'].value_counts().keys()
        y = prescriptions['ROUTE'].value_counts().values
        fig4 = px.bar(data_frame=prescriptions, x=x, y =y )
        st.plotly_chart(fig4,use_container_width=True)


    st.markdown("### Medicamentos dados en el tiempo")
    prescriptions['STARTDATE'] = prescriptions['STARTDATE'].apply(pd.to_datetime)
    prescriptions['month'] = prescriptions['STARTDATE'].dt.to_period('M')
    max_value = prescriptions['STARTDATE'].max()
    min_value = prescriptions['STARTDATE'].min()
    mind, maxd  = st.date_input('Seleccione el rango de fecha', [min_value, max_value])
    maxd = datetime.strptime(str(maxd), '%Y-%m-%d')
    mind = datetime.strptime(str(mind), '%Y-%m-%d')
    filtered_prescriptions = prescriptions[(prescriptions['STARTDATE'] > mind) & (prescriptions['STARTDATE'] < maxd)]
    #filtered_prescriptions = prescriptions[prescriptions['startdate'] > mind]
    y = filtered_prescriptions.groupby(['month'])['drug'].count().values
    x = filtered_prescriptions.groupby(['month'])['drug'].count().index
    x = x.astype(str)
    #fig7 = px.line(data_frame=filtered_prescriptions, x=x, y = y)
    fig7 = px.line( x=x, y= y)
    st.plotly_chart(fig7,use_container_width=True)

if tabla_seleccionada == 'icustays':
    figb1, figb2 = st.columns(2)
    figb3, figb4 = st.columns(2)
    with figb1:
        values = pd.unique(icustays['icustay_id'])
        value = len(values)
        st.metric('Cantidad de registros', value, delta=None, delta_color="normal", help=None, label_visibility="visible")
    with figb2:    
        icustays['careunit_change'] = np.where(icustays['last_careunit'] != icustays['first_careunit'], 1, 0)
        icustays['ward_change'] = np.where(icustays['first_wardid'] != icustays['last_wardid'], 1, 0)
        cambios = icustays['careunit_change'].value_counts()
        cambios_sala = icustays['ward_change'].value_counts()
        permanencias = cambios[cambios.index == 0]
        cambios = cambios[cambios.index == 1]
        permanencias_sala = cambios_sala[cambios_sala.index == 0]
        cambios_sala = cambios_sala[cambios_sala.index == 1]
        permaprop = (int(permanencias) / (int(permanencias) + int(cambios))) * 100
        permaprops = (int(permanencias_sala) / (int(permanencias_sala) + int(cambios_sala))) * 100
        st.metric('Permanencia misma unidad UCI', f"{ round(permaprop,2) } %", delta=None, delta_color="normal", help=None, label_visibility="visible")
    with figb3:    
        st.metric('Permanencia misma sala UCI', f"{round(permaprops,2) } %", delta=None, delta_color="normal", help=None, label_visibility="visible")
    with figb4:  
        icustays['los'].dropna(inplace=True)
        st.metric('Promedio estancia', f"{round(icustays['los'].mean(),2) } días" , delta=None, delta_color="normal", help=None, label_visibility="visible")

    st.markdown("### Fuente de los datos")
    x = icustays['dbsource'].value_counts().keys()
    y = icustays['dbsource'].value_counts().values
    fig4 = px.bar(data_frame=icustays, x=x, y = y )
    st.plotly_chart(fig4,use_container_width=True)

if tabla_seleccionada == 'inputevents_mv':
    
    st.markdown("### Categorías de medicamentos utilizadas")
    inpute = inputevents_mv.merge(d_items, left_on='itemid', right_on='itemid')
    x = inpute.category.value_counts(dropna=False).keys()
    y = inpute.category.value_counts(dropna=False).values
    fig3 = px.bar(data_frame=inpute, x = x, y = y )
    st.plotly_chart(fig3,use_container_width=True)

    st.markdown("### Cantidad histórica promedio de cada medicina")
    #historical average amount of each med.
    inpute['amount'].dropna(inplace=True)
    inpute['amountuom'].dropna(inplace=True)
    inpute['label'].dropna(inplace=True)
    average = inpute.groupby(['label','amountuom'])['amount'].mean()
    average = average.reset_index()
    average.rename(columns={"amount": "average_amount","amountuom": "unit","label": "item"}, inplace = True)
    st.dataframe(average)

    #Filtro por mes o año
    st.markdown("## Filtrar por mes o año")

    inpute['starttime'] = inpute['starttime'].apply(pd.to_datetime)
    inpute['start_year'] = inpute['starttime'].dt.year
    inpute['start_month'] = inpute['starttime'].dt.month

    mes_año = st.radio('Selecciona filtro por mes y año', ('Mes','Año'))
    if mes_año == 'Mes':
        month = st.selectbox('Selecciona el mes', sorted(pd.unique(inpute['start_month'])))
        inpute = inpute[inpute['start_month'] == int(month)]
        average_month = inpute.groupby(['label','amountuom'])['amount'].mean()
        average_month = average_month.reset_index()
        average_month.rename(columns={"amount": "average_amount","label": "item","amountuom": "unit"}, inplace = True)
        if average_month.empty:
            st.markdown('# No hay información para estos filtros')
        else:
            st.dataframe(average_month)       

    #filtrar medicina por año
    if mes_año == 'Año':
        year= st.selectbox('Selecciona el año', sorted(pd.unique(inpute['start_year'])))
        inpute = inpute[inpute['start_year'] == int(year)]
        average_year = inpute.groupby(['label','amountuom'])['amount'].mean()
        average_year = average_year.reset_index()
        average_year.rename(columns={"amount": "average_amount","label": "item","amountuom": "unit"}, inplace = True)
        if average_year.empty:
            st.markdown('No hay información para estos filtros')
        else:
            st.dataframe(average_year)

    #Filtro por año rango
    rango_año = st.slider(
    "Selecciona el rango de años",
    value=(int(inpute['start_year'].max())-10,int(inpute['start_year'].max())), min_value= int(inpute['start_year'].min()), max_value=int(inpute['start_year'].max()))

    inpute2 = inpute[(inpute['start_year'] > int(rango_año[0])) & (inpute['start_year'] < int(rango_año[1]))]
    average_year2 = inpute2.groupby(['label','amountuom'])['amount'].mean()
    average_year2 = average_year2.reset_index()
    average_year2.rename(columns={"amount": "average_amount","label": "item","amountuom": "unit"}, inplace = True)
    if average_year2.empty:
        st.markdown('No hay información para estos filtros')
    else:
        st.dataframe(average_year2)

   

  






