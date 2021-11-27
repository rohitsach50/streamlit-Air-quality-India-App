import folium
import mysql.connector as con
import pandas as pd
import numpy as np
from folium import FeatureGroup
from folium.plugins import MarkerCluster

import streamlit as st
from streamlit_folium import folium_static 
import json
import os


#Connecting TO MYSQL Database and Importing Data
DB_USER= st.secrets["DB_USER"]
DB_PASSWORD=st.secrets["DB_PASSWORD"]
HOST=st.secrets["HOST"]

mydb = con.connect(user = DB_USER, password =DB_PASSWORD, host =DB_HOST, port = '3306')

cur = mydb.cursor()
cur.execute("use test_db;")
cur.execute("select a.Station_Name,a.PM25,a.Date,c.State,c.Latitude,c.Longitude from air_quality_info as a,city_info as c where a.Station_Name=c.Station_Name and a.Date = (select max(Date) TOday from air_quality_info as a)")
current_data=cur.fetchall()
col=['Station','PM25','Date','State','Latitude','Longitude']
current_data=pd.DataFrame(data=current_data,columns=col)
current_data = current_data.astype({'Latitude': np.float,'Longitude': np.float,'PM25':np.float})
india_states = json.load(open('states_india.geojson','r'))

# Code for Streamlit App
st.set_page_config(layout="wide")
states= [x for x in current_data['State'].unique()] 

col1,col2,col3 = st.columns((1,4,1))

col2.write("Air Quality Of India")
choice = col1.selectbox("Select UT/State", states,index=17)
# if choice == "Delhi":
#     col3.write("test successful")



m = folium.Map(location=[23, 77.216721], zoom_start=4,control_scale=True)
folium.GeoJson(india_states, name="geojson").add_to(m)
last_update=current_data['Date'][0]
col3.title(last_update)


markerCluster = MarkerCluster().add_to(m)
for i, row in current_data.iterrows():
    lat = current_data.loc[i,'Latitude']
    lng = current_data.loc[i,'Longitude']

    station = current_data.at[i,'Station']
    popup = current_data.loc[i,'Station'] +'<br>' + str(current_data.loc[i, 'State'])+'<br>' + str(current_data.loc[i, 'PM25'])

    if current_data.loc[i,'PM25'] <=50:
        color = 'darkgreen'
    elif math.isnan(current_data.loc[i,'PM25']):
        color = 'beige'
    elif current_data.loc[i,'PM25'] >=51 and current_data.loc[i,'PM25']<=100:
        color = 'green'
    elif current_data.loc[i,'PM25'] >=101 and current_data.loc[i,'PM25'] <=150:
        color = 'orange'
    elif current_data.loc[i,'PM25'] >=151 and current_data.loc[i,'PM25'] <=200:
        color = 'darkred'
    elif current_data.loc[i,'PM25'] >=201 and current_data.loc[i,'PM25'] <=300:
        color = 'darkpurple'
    elif current_data.loc[i,'PM25'] >=301 and current_data.loc[i,'PM25'] <=500:
        color = 'gray'
    else:
        color = 'black'
    folium.Marker(location=[lat, lng],popup=popup,icon=folium.Icon(color=color,icon='map-pin',prefix='fa')).add_to(markerCluster)
with col2:
    folium_static(m)
m.save("first.html")
mydb.close()


