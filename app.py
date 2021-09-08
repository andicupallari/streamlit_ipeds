import pandas as pd 
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

import plotly.express as px

import folium
from folium.plugins import HeatMap

import requests, os
from gwpy.timeseries import TimeSeries
from gwosc.locate import get_urls
from gwosc import datasets
from gwosc.api import fetch_event_json

from copy import deepcopy
import base64
import pydeck as pdk
import plotly.express as px
from pydeck.types import String


# from helper import make_audio_file

# Use the non-interactive Agg backend, which is recommended as a
# thread-safe backend.
# See https://matplotlib.org/3.3.2/faq/howto_faq.html#working-with-threads.
import matplotlib as mpl
mpl.use("agg")

import numpy as np
import time

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

default_cols = ['INSTNM',
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

# st.subheader('Universities in {} with most {} {} students graduating with a {}: '.format(state, race, gender, award_level ))
# st.map(data_filtered.dropna(how ="any"))

if an_by_state:
	zoom = 6
else:
	zoom = 2

px.set_mapbox_access_token('pk.eyJ1IjoiYWN1cGFsbGFyaSIsImEiOiJja3Q4NXFsM20wejFxMnVzMWxpbmFhODRkIn0.Yv8PS7w77NmVOWir9b304w')
fig = px.scatter_mapbox(data_frame=data_filtered, lat='latitude', lon='longitude', size =data_filtered.columns[0], color = 'cip_label',
	color_continuous_scale=px.colors.cyclical.IceFire, zoom=zoom,
	hover_data = ['INSTNM'], mapbox_style = 'light')

st.plotly_chart(fig)

st.write(data_filtered.sort_values(data_filtered.columns[0], ascending = False).reset_index(drop =True))#.loc[:10,:'ZIP'])

aggregate_all_majors = st.checkbox("Aggregate results for all selected majors, by university", True, key=2)
if aggregate_all_majors:
	st.subheader('Total number of candidates for all selected majors')
	unique_universities = data_filtered['INSTNM'].unique()

	data_filtered_aggregated_by_school  =  data_filtered.groupby('INSTNM').head(1).reset_index(drop = True).sort_values('INSTNM')

	data_filtered_aggregated_by_school = data_filtered_aggregated_by_school.merge(data_filtered.groupby('INSTNM')[data_filtered.columns[0]].sum().reset_index(), on = 'INSTNM')
	fig = px.scatter_mapbox(data_frame=data_filtered_aggregated_by_school, lat='latitude', lon='longitude', size =data_filtered_aggregated_by_school.columns[0], 
		color_continuous_scale=px.colors.cyclical.IceFire, zoom=zoom,
		hover_data = ['INSTNM'], mapbox_style = 'light')

	st.plotly_chart(fig)

	st.write(data_filtered_aggregated_by_school.sort_values(data_filtered_aggregated_by_school.columns[0], ascending = False).reset_index(drop =True))




# from urllib.request import urlopen
# import json
# with urlopen('https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json') as response:
#     counties = json.load(response)

# fig = px.choropleth_mapbox(data_filtered, geojson = counties,  locations = 'FIPS', color =data_filtered.columns[0],
# range_color=(0, 12),
#                            mapbox_style="carto-positron",
#                            zoom=8, center = {"lat": midpoint[0], "lon": midpoint[1]},
#                            opacity=0.5,)
# fig.update_layout(margin = {'r':0, 't':0, 'l':0, 'b':0, })
# st.plotly_chart(fig)

# st.pydeck_chart(pdk.Deck(
#     map_style ="mapbox://styles / mapbox / light-v9",
#     initial_view_state ={
#         "latitude": midpoint[0],
#         "longitude": midpoint[1],
#     },
#     layers =[
#         pdk.Layer(
#         "HeatmapLayer",
#         opacity=0.9,
#         get_fill_color=[255, 0, 0],
#         get_line_color=[0, 0, 0],
#         pickable = False,
#         data = data_filtered,#[[data_filtered.columns[0]]+ ['latitude', 'longitude']],
#         get_position =["longitude", "latitude"],
#         auto_highlight = True,
#         aggregation=String('MEAN'),
#     	get_weight=data_filtered.columns[0]
#         ),
#     ],
# ))