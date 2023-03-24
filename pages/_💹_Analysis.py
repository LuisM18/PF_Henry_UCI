import base64
import numpy as np  #
import pandas as pd  # 
import plotly.express as px  # 
import streamlit as st  # 🎈
import mysql.connector
from datetime import datetime
from PIL import Image

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

insurance = pd.read_sql("""SELECT *
                            FROM insurance""",mydb)

ethnic = pd.read_sql("""SELECT *
                            FROM ETHNICITY""",mydb)

###################################################################################

st.sidebar.markdown("# Descriptive analysis of the tables")
st.sidebar.markdown("# Select the table to view")
tables = ['General','Patients','Prescriptions','ICU Stays','Mechanic ventilation','Procedural Terminology Codes']
tabla_seleccionada = st.sidebar.selectbox('Select the table',tables)
datasight = Image.open('./images/datasighthdwithoutmine.png')
st.sidebar.write('')
st.sidebar.write('')
st.markdown(
    """
    <style>
        [data-testid=stSidebar] [data-testid=stImage]{
            text-align: center;
            display: block;
            margin-left: auto;
            margin-right: auto;
            width: 100%;
        }
    </style>
    """, unsafe_allow_html=True
)

with st.sidebar:
    st.image(datasight, width = 150)
st.markdown("<h1 style='text-align: center; color: white;'>Descriptive Analysis</h1>", unsafe_allow_html=True)
st.markdown("---")
if tabla_seleccionada == 'General':
    col1, col2, col3 = st.columns(3)
    quantity = pd.unique(admissions['SUBJECT_ID'])
    col2.metric(label = 'Patients admitted to the ICU', value = quantity.shape[0])
    css='''
[data-testid="metric-container"] {
    width: fit-content;
    margin: auto;
}

[data-testid="metric-container"] > div {
    width: fit-content;
    margin: auto;
}

[data-testid="metric-container"] label {
    width: fit-content;
    margin: auto;
}
'''
    st.markdown(f'<style>{css}</style>',unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center; color: white;'>Percentage of patients by insurance</h3>", unsafe_allow_html=True)
    insurance_names = insurance['INSURANCE_NAME']
    insurance_counts = admissions['INSURANCE_ID'].value_counts()
    porcentaje_insurance = insurance_counts / insurance_counts.values.sum()
    porcentaje_insurance  = round(porcentaje_insurance * 100,2)

    porcentaje_insurance = pd.DataFrame(porcentaje_insurance)
    insurance_data = porcentaje_insurance.merge(insurance, left_on= porcentaje_insurance.index , right_on='INSURANCE_ID')
    insurance_data.rename(columns = {'INSURANCE_ID_x':'Percentage','INSURANCE_NAME':'Insurance'}, inplace = True)
    fig3 = px.pie(data_frame = insurance_data, values = 'Percentage', names = 'Insurance')
    st.plotly_chart(fig3,use_container_width=True)

    st.markdown("<h3 style='text-align: center; color: white;'>Percentage of patients by sex</h3>", unsafe_allow_html=True)
    gender_counts = patients['GENDER'].value_counts()
    porcentaje_gender = gender_counts / gender_counts.values.sum()
    porcentaje_gender  = round(porcentaje_gender * 100,2)
    fig4 = px.pie(data_frame = porcentaje_gender, values = porcentaje_gender, names = porcentaje_gender.index, labels = {'F': 'Femenino','M':'Masculino'})
    st.plotly_chart(fig4,use_container_width=True)

    st.markdown("<h3 style='text-align: center; color: white;'>Percentage of patients by ethnicity</h3>", unsafe_allow_html=True)
    ethnic_counts = admissions['ETHNICITY_id'].value_counts()
    porcentaje_ethnic = ethnic_counts / ethnic_counts.values.sum()
    porcentaje_ethnic  = round(porcentaje_ethnic * 100,2)
    porcentaje_ethnic = pd.DataFrame(porcentaje_ethnic)
    ethnic_data = porcentaje_ethnic.merge(ethnic, left_on= porcentaje_ethnic.index , right_on='ETHNICITY_ID')
    ethnic_data.rename(columns = {'ETHNICITY_id':'Percentage','ETHNICITY':'Ethnicity'}, inplace = True)
    fig5 = px.pie(data_frame = ethnic_data, values = 'Percentage', names = 'Ethnicity')
    st.plotly_chart(fig5,use_container_width=True)

if tabla_seleccionada == 'Patients':
   
    admission_options = pd.read_sql("""SELECT DISTINCT ADMTYPE_NAME  FROM admissions_type""",mydb)
    adm_filter = st.selectbox("Select the type of admission", admission_options,key="1")

    insurance_options = pd.read_sql("""SELECT DISTINCT INSURANCE_NAME FROM insurance""",mydb)
    insurance = st.selectbox("Select patient insurance", insurance_options,key="2")

    etnia_options = pd.read_sql("""SELECT DISTINCT ETHNICITY FROM ethnicity""",mydb)
    etnia = st.multiselect('Select ethnicity', etnia_options, default = ['WHITE','OTHER'])

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

    st.markdown("<h3 style='text-align: center; color: white;'>Patients by sex</h3>", unsafe_allow_html=True)
    genero = pd.read_sql("""SELECT DISTINCT GENDER, COUNT(GENDER)
                            FROM patient_dim
                            GROUP BY GENDER""",mydb)
    
    genero['percentage'] = genero['COUNT(GENDER)']/genero['COUNT(GENDER)'].sum()
    genero['percentage'] = round(genero['percentage'] * 100 ,2)

    fig3 = px.pie(genero,names='GENDER',values= 'percentage', labels = {
                     'GENDER': "Sex",
                     'percentage': "Percentage",
                 })
    st.plotly_chart(fig3,use_container_width=True)

    st.markdown("<h3 style='text-align: center; color: white;'>Pacientes por estado civil</h3>", unsafe_allow_html=True)
    estado_civil = pd.read_sql("""SELECT MARIT_STATUS_RESULT, COUNT(MARIT_STATUS_RESULT)
                                    FROM admissions_hechos a 
                                    RIGHT JOIN  marital_status m
                                    ON a.MARIT_STATUS_ID = m.MARIT_STATUS_ID
                                    GROUP BY MARIT_STATUS_RESULT;""",mydb)
    
    estado_civil = estado_civil.sort_values('COUNT(MARIT_STATUS_RESULT)',ascending=False)
    estado_civil['percentage'] = estado_civil['COUNT(MARIT_STATUS_RESULT)']/estado_civil['COUNT(MARIT_STATUS_RESULT)'].sum()
    estado_civil ['percentage'] = round(estado_civil ['percentage'] * 100 ,2)

    fig4 = px.bar(estado_civil, x="MARIT_STATUS_RESULT", y ="percentage", labels = {
                     'MARIT_STATUS_RESULT': "Marital Status",
                     'percentage': "Percentage",
                 }) 
    st.plotly_chart(fig4,use_container_width=True)

    st.markdown("<h3 style='text-align: center; color: white;'>Histogram of the ages of the patients</h3>", unsafe_allow_html=True) 
    yearnac = pd.to_datetime(patients['DOB'])
    yearmu = pd.to_datetime(patients['DOD'])
    patients['AGE'] = yearmu.dt.year - yearnac.dt.year
    patients = patients[patients['AGE'] < 150]
    fig5 = px.histogram(data_frame=patients, x="AGE", labels = {
                     'AGE': "Age",
                 })
    st.plotly_chart(fig5,use_container_width=True)

    st.markdown("<h3 style='text-align: center; color: white;'>Locations from which patients were admitted</h3>", unsafe_allow_html=True)
    location = pd.read_sql("""SELECT ADMLOCATION_NAME, COUNT(ADMLOCATION_NAME)
                                FROM admissions_hechos a 
                                RIGHT JOIN  admissions_location al
                                ON a.ADMLOCATION_ID = al.ADMLOCATION_ID
                                GROUP BY ADMLOCATION_NAME;""",mydb)
    location = location.sort_values('COUNT(ADMLOCATION_NAME)',ascending=False)
    location['percentage'] = location['COUNT(ADMLOCATION_NAME)']/location['COUNT(ADMLOCATION_NAME)'].sum()
    location['percentage'] = round(location['percentage'] * 100 ,2)

    fig6 = px.bar(location, x="ADMLOCATION_NAME", y ="percentage", labels = {
                     'ADMLOCATION_NAME': "Location",
                     'percentage': 'Percentage'
                 })
    st.plotly_chart(fig6,use_container_width=True)

if tabla_seleccionada == 'Prescriptions':
    fig3, fig4 = st.columns(2)
    fig5, fig6 = st.columns(2)
    st.markdown("<h3 style='text-align: center; color: white;'>Top N most used drugs</h3>", unsafe_allow_html=True)
    number = st.select_slider('Selecciona n', options = range(5,31) ,value = 5, key = '1')
    x = prescriptions['DRUG'].value_counts().keys()[0:number]
    y = prescriptions['DRUG'].value_counts().values[0:number]
    fig3 = px.bar(data_frame=prescriptions, x = x, y = y , labels = {
                     'x': "Drug",
                     'y': 'Quantity'
                 })
    st.plotly_chart(fig3,use_container_width=True)

    st.markdown("<h3 style='text-align: center; color: white;'>Medication route</h3>", unsafe_allow_html=True)
    number = st.select_slider('Selecciona n', options = range(5,31) ,value = 5, key = '2')
    x = prescriptions['ROUTE'].value_counts().keys()[0:number] 
    y = prescriptions['ROUTE'].value_counts().values[0:number] 
    fig4 = px.bar(data_frame=prescriptions, x = x, y = y, labels = {
                     'x': "Route",
                     'y': 'Quantity'
                 })
    st.plotly_chart(fig4,use_container_width=True)

    st.markdown("<h3 style='text-align: center; color: white;'>Quantity of drugs supplied over time</h3>", unsafe_allow_html=True)
    prescriptions['STARTDATE'] = prescriptions['STARTDATE'].apply(pd.to_datetime)
    prescriptions['month'] = prescriptions['STARTDATE'].dt.to_period('M')
    max_value = prescriptions['STARTDATE'].max().to_pydatetime()
    min_value = prescriptions['STARTDATE'].min().to_pydatetime()
    mind, maxd  = st.slider('Select date range',value= (min_value, max_value))

    filtered_prescriptions = prescriptions[(prescriptions['STARTDATE'] > mind) & (prescriptions['STARTDATE'] < maxd)]
    #filtered_prescriptions = prescriptions[prescriptions['startdate'] > mind]
    y = filtered_prescriptions.groupby(['month'])['DRUG'].count().values
    x = filtered_prescriptions.groupby(['month'])['DRUG'].count().index
    if len(x) != 1:
        x = x.astype(str)
        #fig7 = px.line(data_frame=filtered_prescriptions, x=x, y = y)
        fig7 = px.line( x = x, y = y, labels = {
                     'x': "Amount of drugs",
                     'y': 'Quantity'
                 })
        st.plotly_chart(fig7,use_container_width=True)
    else:
        st.write('There is no information for the selected filters.')

if tabla_seleccionada == 'ICU Stays':
    figb1, figb2 = st.columns(2)
    figb3, figb4 = st.columns(2)
    with figb1:
        values = pd.unique(icustays['ICUSTAY_ID'])
        value = len(values)
        st.metric('Number of records', value, delta=None, delta_color="normal", help=None, label_visibility="visible")
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
        st.metric('Permanence in the same ICU unit', f"{ round(permaprop,2) } %", delta=None, delta_color="normal", help=None, label_visibility="visible")
    with figb3:    
        st.metric('Permanence in the same ICU ward', f"{round(permaprops,2) } %", delta=None, delta_color="normal", help=None, label_visibility="visible")
    with figb4:  
        icustays['LOS'].dropna(inplace=True)
        st.metric('Average ICU stay', f"{round(icustays['LOS'].mean(),2) } days" , delta=None, delta_color="normal", help=None, label_visibility="visible")

    st.markdown("<h3 style='text-align: center; color: white;'>Data source</h3>", unsafe_allow_html=True)

    x = icustays['DBSOURCE'].value_counts().keys()
    y = icustays['DBSOURCE'].value_counts().values / icustays['DBSOURCE'].value_counts().values.sum()
    y = y * 100
    y = y.round(2)
    fig4 = px.pie(data_frame=icustays, names = x, values = y, labels = {
                     'x': "Source",
                     'y': 'Percentage'
                 }) 
    st.plotly_chart(fig4,use_container_width=True)

if tabla_seleccionada == 'Mechanic ventilation':
    st.markdown("<h3 style='text-align: center; color: white;'>Categories of medicines used</h3>", unsafe_allow_html=True)
    inpute = inputevents_mv.merge(d_items, left_on='ITEMID', right_on='ITEMID')
    x = inpute['CATEGORY'].value_counts(dropna=False).keys()
    y = inpute['CATEGORY'].value_counts(dropna=False).values
    fig3 = px.bar(data_frame=inpute, x = x, y = y, labels = 
                  {'x' : 'Category', 'y': 'Number of records'} )
    st.plotly_chart(fig3,use_container_width=True)
    st.markdown("<h3 style='text-align: center; color: white;'>Historical average quantity of each medicine</h3>", unsafe_allow_html=True)
    #historical average AMOUNT of each med.
    inpute['AMOUNT'].dropna(inplace=True)
    inpute['AMOUNTUOM'].dropna(inplace=True)
    inpute['LABEL'].dropna(inplace=True)
    average = inpute.groupby(['LABEL','AMOUNTUOM'])['AMOUNT'].mean()
    average = average.reset_index()
    average.rename(columns={"AMOUNT": "average_amount","AMOUNTUOM": "unit","LABEL": "item"}, inplace = True)
    st.dataframe(average)

    #Filter by day or month
    st.markdown("<h3 style='text-align: center; color: white;'>Filter by month or year</h3>", unsafe_allow_html=True)
    inpute['STARTTIME'] = inpute['STARTTIME'].apply(pd.to_datetime)
    inpute['start_year'] = inpute['STARTTIME'].dt.year
    inpute['start_month'] = inpute['STARTTIME'].dt.month

    mes_año = st.radio('Select filter by month and year', ('Month','Year'))
    if mes_año == 'Month':
        month = st.selectbox('Select month', sorted(pd.unique(inpute['start_month'])))
        inpute3 = inpute[inpute['start_month'] == int(month)]
        average_month = inpute3.groupby(['LABEL','AMOUNTUOM'])['AMOUNT'].mean()
        average_month = average_month.reset_index()
        average_month.rename(columns={"AMOUNT": "average_AMOUNT","LABEL": "item","AMOUNTUOM": "unit"}, inplace = True)
        if average_month.empty:
            st.markdown('# There is no information for the selected filters.')
        else:
            st.dataframe(average_month)       

    #filtrar medicina por año
    if mes_año == 'Year':
        year= st.selectbox('Select year', sorted(pd.unique(inpute['start_year'])))
        inpute4 = inpute[inpute['start_year'] == int(year)]
        average_year = inpute4.groupby(['LABEL','AMOUNTUOM'])['AMOUNT'].mean()
        average_year = average_year.reset_index()
        average_year.rename(columns={"AMOUNT": "average_AMOUNT","LABEL": "item","AMOUNTUOM": "unit"}, inplace = True)
        if average_year.empty:
            st.markdown('There is no information for the selected filters.')
        else:
            st.dataframe(average_year)
    
    st.markdown("<h3 style='text-align: center; color: white;'>Filter by range of years</h3>", unsafe_allow_html=True)
    #Filtro por año rango
    rango_año = st.slider(
    "Select the year range",
    value=(int(inpute['start_year'].max())-10,int(inpute['start_year'].max())), min_value= int(inpute['start_year'].min()), max_value=int(inpute['start_year'].max()))
    st.write(rango_año)
    inpute2 = inpute[(inpute['start_year'] > int(rango_año[0])) & (inpute['start_year'] < int(rango_año[1]))]
    average_year2 = inpute2.groupby(['LABEL','AMOUNTUOM'])['AMOUNT'].mean()
    average_year2 = average_year2.reset_index()
    average_year2.rename(columns={"AMOUNT": "average_AMOUNT","LABEL": "item","AMOUNTUOM": "unit"}, inplace = True)
    if average_year2.empty:
        st.markdown('There is no information for the selected filters.')
    else:
        st.dataframe(average_year2)

if tabla_seleccionada == 'Procedural Terminology Codes':
    st.markdown("<h3 style='text-align: center; color: white;'>Top N most repeated subsections</h3>", unsafe_allow_html=True)
    #cptevents['SUBSECTIONHEADER'].dropna(inplace=True)
    data_cptevents = cptevents['SUBSECTIONHEADER'].value_counts()
    number = st.select_slider('Select n', options = range(1,10) ,value = 5, key = '3')
    x = data_cptevents.keys()[0:number]
    y = data_cptevents.values[0:number]
    fig4 = px.bar(data_frame=data_cptevents, x = x, y = y, labels={
                     'x': "Subsections",
                     'y': "Number of records",
                 }) 
    st.plotly_chart(fig4,use_container_width=True)

    st.markdown("<h3 style='text-align: center; color: white;'>Top N most repeated sections</h3>", unsafe_allow_html=True)
    #cptevents['SECTIONHEADER'].dropna(inplace=True)
    datas_cptevents = cptevents['SECTIONHEADER'].value_counts()
    number = st.select_slider('Select n', options = range(1,5) ,value = 3, key = '4')
    x = datas_cptevents.keys()[0:number]
    y = datas_cptevents.values[0:number]
    fig5 = px.bar(data_frame=datas_cptevents, x = x, y = y, labels={
                     'x': "Sections",
                     'y': "Number of records",
                 }) 
    st.plotly_chart(fig5,use_container_width=True)

    st.markdown("<h3 style='text-align: center; color: white;'>Cost center that invoiced</h3>", unsafe_allow_html=True)
    #cptevents['COSTCENTER'].dropna(inplace=True)
    cost_cptevents = cptevents['COSTCENTER'].value_counts()
    x = cost_cptevents.keys()
    y = cost_cptevents.values
    fig6 = px.pie(data_frame=cost_cptevents, names = x, values = y,labels={
                     'x': "Cost center",
                     'y': "Number of records",
                 })
    st.plotly_chart(fig6,use_container_width=True)
  






