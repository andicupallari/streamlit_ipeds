import pandas as pd 
import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

import plotly.express as px


import matplotlib as mpl
mpl.use("agg")


st.header('Where to find talent in the US to increase diversity and inclusion accross races and gender?')

@st.cache
def load_data():
    df = pd.read_csv('completions.csv')
    return df

# Will only run once if already cached
data = load_data()


data.rename(columns = {'LONGITUD': 'longitude', 'LATITUDE': 'latitude'}, inplace = True)


major_options = sorted(list(data.cip_label.dropna().unique()))
default_major = major_options.index('Computer Science')
majors = st.sidebar.multiselect('Select a Field of Study', major_options, default =  ['Computer Science', 'Finance, General', 'Economics, General'])
race = st.sidebar.selectbox("Select candidate's race", ['African American','Asian', 'Latino/ Hispanic'])
gender = st.sidebar.selectbox("Select candidate's gender", ['male', 'female', 'all'])

an_by_state = st.checkbox("Show Analysis by State", True, key=1)
if an_by_state:
	state_options = sorted(list(data.STABBR.dropna().unique()))
	default_ix = state_options.index('MA')
	state = st.selectbox('Select a State',state_options, index = default_ix)
	data_filtered = data.loc[(data['STABBR'] == state), :]
else:
	data_filtered = data

degree_options = sorted(list(data.award_level.dropna().unique()))
default_degree = degree_options.index("Bachelor's degree")
award_level = st.sidebar.selectbox('Select Degree Awarded', degree_options, index = default_degree)

default_cols = ['INSTNM',  'ADDR', 'CITY', 'STABBR', 'ZIP',
'longitude', 'latitude',
'cip_label', 'award_level']

if race == 'African American' and gender == 'male':
	data_filtered = data_filtered.loc[:, ['african_american_m'] + default_cols]
elif race == 'African American' and gender == 'female':
	data_filtered = data_filtered.loc[:, ['african_american_w'] + default_cols]
elif race == 'African American' and gender == 'all':
	data_filtered = data_filtered.loc[:, ['african_american_t'] + default_cols]

elif race == 'Asian' and gender == 'male':
	data_filtered = data_filtered.loc[:, ['asian_m'] + default_cols]
elif race == 'Asian' and gender == 'female':
	data_filtered = data_filtered.loc[:, ['asian_w'] + default_cols]
elif race == 'Asian' and gender == 'all':
	data_filtered = data_filtered.loc[:, ['asian_t'] + default_cols]

elif race == 'Latino/ Hispanic' and gender == 'male':
	data_filtered = data_filtered.loc[:, ['hispanic_m'] + default_cols]
elif race == 'Latino/ Hispanic' and gender == 'female':
	data_filtered = data_filtered.loc[:, ['hispanic_w'] + default_cols]
elif race == 'Latino/ Hispanic' and gender == 'all':
	data_filtered = data_filtered.loc[:, ['hispanic_t'] + default_cols]

# plot a map 
data_filtered = data_filtered.loc[(data_filtered['cip_label'].isin(majors)) & (data_filtered['award_level'] == award_level), :]
data_filtered = data_filtered[data_filtered[data_filtered.columns[0]]>0]
midpoint = (np.average(data_filtered["latitude"]), np.average(data_filtered["longitude"]))
name_main_column = data_filtered.columns[0]
# st.subheader('Universities in {} with most {} {} students graduating with a {}: '.format(state, race, gender, award_level ))
# st.map(data_filtered.dropna(how ="any"))

if an_by_state:
	zoom = 6
else:
	zoom = 2

px.set_mapbox_access_token('pk.eyJ1IjoiYWN1cGFsbGFyaSIsImEiOiJja3Q4NXFsM20wejFxMnVzMWxpbmFhODRkIn0.Yv8PS7w77NmVOWir9b304w')
fig = px.scatter_mapbox(data_frame=data_filtered, lat='latitude', lon='longitude', size =name_main_column, color = 'cip_label',
	color_continuous_scale=px.colors.cyclical.IceFire, zoom=zoom,
	hover_data = ['INSTNM'], mapbox_style = 'light')

st.plotly_chart(fig)

st.write(data_filtered.sort_values(name_main_column, ascending = False).reset_index(drop =True))#.loc[:10,:'ZIP'])

aggregate_all_majors = st.checkbox("Aggregate results for all selected majors, by university", True, key=2)
if aggregate_all_majors:
	st.markdown("***")

	st.header('Total number of candidates for all selected majors')
	unique_universities = data_filtered['INSTNM'].unique()

	data_filtered_one_row_per_college  =  data_filtered.groupby('INSTNM').head(1).reset_index(drop = True).sort_values('INSTNM')
	data_filtered_one_row_per_college.drop(columns = ['cip_label'], inplace = True)

	data_total_vals  = data_filtered.groupby('INSTNM')[name_main_column].sum().reset_index()
	name_main_column_new = name_main_column+'_all_majors'

	data_total_vals.rename(columns = {name_main_column:name_main_column_new}, inplace = True)



	data_filtered_one_row_per_college = data_filtered_one_row_per_college.merge(data_total_vals, on = 'INSTNM')
	data_filtered_one_row_per_college.drop(columns = [data_filtered_one_row_per_college.columns[0]], inplace = True)
	data_filtered_one_row_per_college.rename(columns = {data_filtered_one_row_per_college.columns[-1]: name_main_column }, inplace = True)
	first_column = data_filtered_one_row_per_college.pop(name_main_column)
	data_filtered_one_row_per_college.insert(0, name_main_column, first_column)

	fig1 = px.scatter_mapbox(data_frame=data_filtered_one_row_per_college, lat='latitude', lon='longitude', size =name_main_column, 
		color_continuous_scale=px.colors.cyclical.IceFire, zoom=zoom,
		hover_data = ['INSTNM'], mapbox_style = 'light')

	st.plotly_chart(fig1)

	st.write(data_filtered_one_row_per_college.sort_values(name_main_column, ascending = False).reset_index(drop =True))


