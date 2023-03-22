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
                            FROM icustay_hechos""",mydb)

patients = pd.read_sql("""SELECT *
                            FROM patient_dim""",mydb)

prescriptions = pd.read_sql("""SELECT *
                            FROM prescriptions""",mydb)

inputevents_mv = pd.read_sql("""SELECT *
                            FROM inputevents_mv""",mydb)


d_items = pd.read_sql("""SELECT *
                            FROM d_items""",mydb)

cptevents = pd.read_sql("""SELECT *
                            FROM cptevents""",mydb)

###################################################################################

st.sidebar.markdown("# Análisis descriptivo de las tablas")
st.sidebar.markdown("# Seleccione las tablas")
tables = ['Pacientes','Prescripciones','Estancia en UCI','Ventilación Mecánica','Códigos de terminología procesal']
tabla_seleccionada = st.sidebar.selectbox('Seleccione las tablas',tables)

st.markdown("<h1 style='text-align: center; color: white;'>Análisis descriptivo</h1>", unsafe_allow_html=True)
st.markdown("---")
if tabla_seleccionada == 'Pacientes':
   
    admission_options = pd.read_sql("""SELECT DISTINCT ADMTYPE_NAME  FROM admissions_type""",mydb)
    adm_filter = st.selectbox("Selecciona el tipo de admisión", admission_options,key="1")

    insurance_options = pd.read_sql("""SELECT DISTINCT INSURANCE_NAME FROM insurance""",mydb)
    insurance = st.selectbox("Selecciona el seguro del paciente", insurance_options,key="2")

    etnia_options = pd.read_sql("""SELECT DISTINCT ETHNICITY FROM ethnicity""",mydb)
    etnia = st.multiselect('Selecciona la etnia del paciente', etnia_options, default = ['WHITE','OTHER'])

    # creating a single-element container
    placeholder = st.empty()

    # dataframe filter
    type_id = pd.read_sql("""SELECT ADMTYPE_ID 
                            FROM admissions_type
                            WHERE ADMTYPE_NAME = '%s'""" % adm_filter,mydb)
    
    insurance_id = pd.read_sql("""SELECT INSURANCE_ID 
                            FROM insurance
                            WHERE INSURANCE_NAME = '%s'""" % insurance,mydb) 
    
    etnia_id = pd.read_sql("""SELECT ETHNICITY_ID
                            FROM ethnicity
                            WHERE ETHNICITY IN {etnia}""".format(etnia=tuple(etnia)),mydb)

    # dataframe filter

    admissions = admissions[(admissions["ADMTYPE_ID"] == type_id) & (admissions["INSURANCE_ID"] == insurance_id) & (admissions["ETHNICITY_id"].isin(etnia_id))]
    fig3, fig4 = st.columns(2)
    fig5, fig6 = st.columns(2)

    st.markdown("<h3 style='text-align: center; color: white;'>Pacientes por sexo</h3>", unsafe_allow_html=True)
    genero = pd.read_sql("""SELECT DISTINCT GENDER, COUNT(GENDER)
                            FROM patient_dim
                            GROUP BY GENDER""",mydb)
    fig3 = px.bar(genero,x='GENDER',y= 'COUNT(GENDER)', labels = {
                     'GENDER': "Sexo",
                     'COUNT(GENDER)': "Cantidad de registros",
                 })
    st.plotly_chart(fig3,use_container_width=True)

    st.markdown("<h3 style='text-align: center; color: white;'>Pacientes por estado civil</h3>", unsafe_allow_html=True)
    estado_civil = pd.read_sql("""SELECT MARIT_STATUS_RESULT, COUNT(MARIT_STATUS_RESULT)
                                    FROM admissions_hechos a 
                                    RIGHT JOIN  marital_status m
                                    ON a.MARIT_STATUS_ID = m.MARIT_STATUS_ID
                                    GROUP BY MARIT_STATUS_RESULT;""",mydb)

    fig4 = px.bar(estado_civil, x="MARIT_STATUS_RESULT", y ="COUNT(MARIT_STATUS_RESULT)", labels = {
                     'MARIT_STATUS_RESULT': "Estado civil",
                     'COUNT(MARIT_STATUS_RESULT)': "Cantidad de registros",
                 }) 
    st.plotly_chart(fig4,use_container_width=True)

    st.markdown("<h3 style='text-align: center; color: white;'>Pacientes por edad</h3>", unsafe_allow_html=True) 
    yearnac = pd.to_datetime(patients['DOB'])
    yearmu = pd.to_datetime(patients['DOD'])
    patients['AGE'] = yearmu.dt.year - yearnac.dt.year
    fig5 = px.histogram(data_frame=patients, x="AGE", labels = {
                     'AGE': "Edad",
                 })
    st.plotly_chart(fig5,use_container_width=True)

    st.markdown("<h3 style='text-align: center; color: white;'>Lugares donde los pacientes fueron admitidos</h3>", unsafe_allow_html=True)
    location = pd.read_sql("""SELECT ADMLOCATION_NAME, COUNT(ADMLOCATION_NAME)
                                FROM admissions_hechos a 
                                RIGHT JOIN  admissions_location al
                                ON a.ADMLOCATION_ID = al.ADMLOCATION_ID
                                GROUP BY ADMLOCATION_NAME;""",mydb)

    fig6 = px.bar(location, x="ADMLOCATION_NAME", y ="COUNT(ADMLOCATION_NAME)", labels = {
                     'ADMLOCATION_NAME': "Lugares",
                     'COUNT(ADMLOCATION_NAME)': 'Cantidad de registros'
                 })
    st.plotly_chart(fig6,use_container_width=True)

if tabla_seleccionada == 'Prescripciones':
    fig3, fig4 = st.columns(2)
    fig5, fig6 = st.columns(2)
    st.markdown("<h3 style='text-align: center; color: white;'>Top N Medicamentos más utilizados</h3>", unsafe_allow_html=True)
    x = prescriptions['DRUG'].value_counts().keys()
    y = prescriptions['DRUG'].value_counts().values
    fig3 = px.bar(data_frame=prescriptions, x = x, y = y , labels = {
                     'x': "Medicamento",
                     'y': 'Cantidad de registros'
                 })
    st.plotly_chart(fig3,use_container_width=True)

    st.markdown("<h3 style='text-align: center; color: white;'>Ruta de la medicación</h3>", unsafe_allow_html=True)
    x = prescriptions['ROUTE'].value_counts().keys()
    y = prescriptions['ROUTE'].value_counts().values
    fig4 = px.bar(data_frame=prescriptions, x = x, y = y, labels = {
                     'x': "Ruta",
                     'y': 'Cantidad de registros'
                 })
    st.plotly_chart(fig4,use_container_width=True)

    st.markdown("<h3 style='text-align: center; color: white;'>Cantidad de medicamentos aplicados en el tiempo</h3>", unsafe_allow_html=True)
    prescriptions['STARTDATE'] = prescriptions['STARTDATE'].apply(pd.to_datetime)
    prescriptions['month'] = prescriptions['STARTDATE'].dt.to_period('M')
    max_value = prescriptions['STARTDATE'].max()
    min_value = prescriptions['STARTDATE'].min()
    mind, maxd  = st.date_input('Seleccione el rango de fecha', [min_value, max_value])
    maxd = datetime.strptime(str(maxd), '%Y-%m-%d')
    mind = datetime.strptime(str(mind), '%Y-%m-%d')
    filtered_prescriptions = prescriptions[(prescriptions['STARTDATE'] > mind) & (prescriptions['STARTDATE'] < maxd)]
    #filtered_prescriptions = prescriptions[prescriptions['startdate'] > mind]
    y = filtered_prescriptions.groupby(['month'])['DRUG'].count().values
    x = filtered_prescriptions.groupby(['month'])['DRUG'].count().index
    if len(x) != 1:
        x = x.astype(str)
        #fig7 = px.line(data_frame=filtered_prescriptions, x=x, y = y)
        fig7 = px.line( x = x, y = y, labels = {
                     'x': "Cantidad de medicamentos",
                     'y': 'Cantidad de registros'
                 })
        st.plotly_chart(fig7,use_container_width=True)
    else:
        st.write('No hay información para los filtros seleccionados.')

if tabla_seleccionada == 'Estancia en UCI':
    figb1, figb2 = st.columns(2)
    figb3, figb4 = st.columns(2)
    with figb1:
        values = pd.unique(icustays['ICUSTAY_ID'])
        value = len(values)
        st.metric('Cantidad de registros', value, delta=None, delta_color="normal", help=None, label_visibility="visible")
    with figb2:    
        icustays['careunit_change'] = np.where(icustays['LAST_CAREUNIT'] != icustays['FIRST_CAREUNIT'], 1, 0)
        icustays['ward_change'] = np.where(icustays['FIRST_WARDID'] != icustays['LAST_WARDID'], 1, 0)
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
        icustays['LOS'].dropna(inplace=True)
        st.metric('Promedio estancia', f"{round(icustays['LOS'].mean(),2) } días" , delta=None, delta_color="normal", help=None, label_visibility="visible")

    st.markdown("<h3 style='text-align: center; color: white;'>Fuente de los datos</h3>", unsafe_allow_html=True)
    x = icustays['DBSOURCE'].value_counts().keys()
    y = icustays['DBSOURCE'].value_counts().values
    fig4 = px.bar(data_frame=icustays, x = x, y = y,labels = {
                     'x': "Fuente",
                     'y': 'Cantidad de registros'
                 }) 
    st.plotly_chart(fig4,use_container_width=True)

if tabla_seleccionada == 'Ventilación Mecánica':
    
    st.markdown("### Categorías de medicamentos utilizadas")
    inpute = inputevents_mv.merge(d_items, left_on='ITEMID', right_on='ITEMID')
    x = inpute.category.value_counts(dropna=False).keys()
    y = inpute.category.value_counts(dropna=False).values
    fig3 = px.bar(data_frame=inpute, x = x, y = y )
    st.plotly_chart(fig3,use_container_width=True)

    st.markdown("### Cantidad histórica promedio de cada medicina")
    #historical average AMOUNT of each med.
    inpute['AMOUNT'].dropna(inplace=True)
    inpute['AMOUNTUOM'].dropna(inplace=True)
    inpute['LABEL'].dropna(inplace=True)
    average = inpute.groupby(['LABEL','AMOUNTUOM'])['AMOUNT'].mean()
    average = average.reset_index()
    average.rename(columns={"AMOUNT": "average_amount","AMOUNTUOM": "unit","LABEL": "item"}, inplace = True)
    st.dataframe(average)

    #Filtro por mes o año
    st.markdown("## Filtrar por mes o año")

    inpute['STARTTIME'] = inpute['STARTTIME'].apply(pd.to_datetime)
    inpute['start_year'] = inpute['STARTTIME'].dt.year
    inpute['start_month'] = inpute['STARTTIME'].dt.month

    mes_año = st.radio('Selecciona filtro por mes y año', ('Mes','Año'))
    if mes_año == 'Mes':
        month = st.selectbox('Selecciona el mes', sorted(pd.unique(inpute['start_month'])))
        inpute = inpute[inpute['start_month'] == int(month)]
        average_month = inpute.groupby(['LABEL','AMOUNTUOM'])['AMOUNT'].mean()
        average_month = average_month.reset_index()
        average_month.rename(columns={"AMOUNT": "average_AMOUNT","LABEL": "item","AMOUNTUOM": "unit"}, inplace = True)
        if average_month.empty:
            st.markdown('# No hay información para estos filtros')
        else:
            st.dataframe(average_month)       

    #filtrar medicina por año
    if mes_año == 'Año':
        year= st.selectbox('Selecciona el año', sorted(pd.unique(inpute['start_year'])))
        inpute = inpute[inpute['start_year'] == int(year)]
        average_year = inpute.groupby(['LABEL','AMOUNTUOM'])['AMOUNT'].mean()
        average_year = average_year.reset_index()
        average_year.rename(columns={"AMOUNT": "average_AMOUNT","LABEL": "item","AMOUNTUOM": "unit"}, inplace = True)
        if average_year.empty:
            st.markdown('No hay información para estos filtros')
        else:
            st.dataframe(average_year)

    #Filtro por año rango
    rango_año = st.slider(
    "Selecciona el rango de años",
    value=(int(inpute['start_year'].max())-10,int(inpute['start_year'].max())), min_value= int(inpute['start_year'].min()), max_value=int(inpute['start_year'].max()))

    inpute2 = inpute[(inpute['start_year'] > int(rango_año[0])) & (inpute['start_year'] < int(rango_año[1]))]
    average_year2 = inpute2.groupby(['LABEL','AMOUNTUOM'])['AMOUNT'].mean()
    average_year2 = average_year2.reset_index()
    average_year2.rename(columns={"AMOUNT": "average_AMOUNT","LABEL": "item","AMOUNTUOM": "unit"}, inplace = True)
    if average_year2.empty:
        st.markdown('No hay información para estos filtros')
    else:
        st.dataframe(average_year2)

if tabla_seleccionada == 'Códigos de terminología procesal':
    st.markdown("<h3 style='text-align: center; color: white;'>Top 5 subsecciones más repetidas</h3>", unsafe_allow_html=True)
    #cptevents['SUBSECTIONHEADER'].dropna(inplace=True)
    data_cptevents = cptevents['SUBSECTIONHEADER'].value_counts()
    x = data_cptevents.keys()[0:5]
    y = data_cptevents.values[0:5]
    fig4 = px.bar(data_frame=data_cptevents, x = x, y = y, labels={
                     'x': "Subsecciones",
                     'y': "Cantidad de registros",
                 }) 
    st.plotly_chart(fig4,use_container_width=True)

    st.markdown("<h3 style='text-align: center; color: white;'>Top 5 secciones más repetidas</h3>", unsafe_allow_html=True)
    #cptevents['SECTIONHEADER'].dropna(inplace=True)
    datas_cptevents = cptevents['SECTIONHEADER'].value_counts()
    x = datas_cptevents.keys()[0:5]
    y = datas_cptevents.values[0:5]
    fig5 = px.bar(data_frame=datas_cptevents, x = x, y = y, labels={
                     'x': "Secciones",
                     'y': "Cantidad de registros",
                 }) 
    st.plotly_chart(fig5,use_container_width=True)

    st.markdown("<h3 style='text-align: center; color: white;'>Centro de coste que facturó</h3>", unsafe_allow_html=True)
    #cptevents['COSTCENTER'].dropna(inplace=True)
    cost_cptevents = cptevents['COSTCENTER'].value_counts()
    x = cost_cptevents.keys()[0:5]
    y = cost_cptevents.values[0:5]
    fig6 = px.bar(data_frame=cost_cptevents, x = x, y = y,labels={
                     'x': "Centro de coste",
                     'y': "Cantidad de registros",
                 })
    st.plotly_chart(fig6,use_container_width=True)
  






