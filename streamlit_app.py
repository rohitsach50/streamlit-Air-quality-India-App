import folium
import mysql.connector as con
import pandas as pd
import numpy as np
from folium import FeatureGroup
from folium.plugins import MarkerCluster
import math
import streamlit as st
from streamlit_folium import folium_static 
import json
import os
import plotly.express as px



#Connecting TO MYSQL Database and Importing Data
DB_USER= st.secrets["DB_USER"]
DB_PASSWORD=st.secrets["DB_PASSWORD"]
DB_HOST=st.secrets["DB_HOST"]
MAPBOX_KEY=st.secrets["MAPBOX_KEY"]

mydb = con.connect(user = DB_USER, password =DB_PASSWORD, host =DB_HOST, port = '3306')
px.set_mapbox_access_token(MAPBOX_KEY)

cur = mydb.cursor()
cur.execute("use test_db;")
cur.execute("select a.Station_Name,a.PM25,a.Date,c.State,c.Latitude,c.Longitude from air_quality_info as a,city_info as c where a.Station_Name=c.Station_Name and a.Date = (select max(Date) TOday from air_quality_info as a)")
current_data=cur.fetchall()
col=['Station','PM25','Date','State','Latitude','Longitude']
current_data=pd.DataFrame(data=current_data,columns=col)
current_data = current_data.astype({'Latitude': np.float,'Longitude': np.float,'PM25':np.float})


data=pd.read_csv("state wise centroids_2011.csv")
states=[x for x in data['State']]
states.sort()
states.insert(0,"Select a State")

# Code for Streamlit App
st.set_page_config(layout="wide")
 

col1,col2,col3 = st.columns((1,4,1))

col2.write(# **_Air Quality Of India_**)
choice = col1.selectbox("Select UT/State", states,index=0)


last_update=current_data['Date'][0]
col3.title(last_update)
state_dict={}

for i, row in data.iterrows():
    
    state_dict[row.State]=[row.Latitude,row.Longitude]    
        
          
m = folium.Map(location=[23, 77.216721], zoom_start=4,control_scale=True)
markerCluster = MarkerCluster()
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



if choice:
    if choice in state_dict:
        m2 = folium.Map(location=state_dict[choice], zoom_start=7,control_scale=True)
        markerCluster.add_to(m2)
        with col2:
            folium_static(m2)
    else:
        with col2:
            markerCluster.add_to(m)
            folium_static(m)


mydb.close()


