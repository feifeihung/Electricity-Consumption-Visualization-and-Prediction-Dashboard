import os
from itertools import groupby

import streamlit as st
import pandas as pd
import altair as alt
import plotly.express as px
import matplotlib.pyplot as plt
import json
import seaborn as sns
import plotly.graph_objects as go

st.set_page_config(
    page_title="US Household Electricity Consumption Dashboard",
    page_icon=':derelict_house_building:' ,
    layout="wide",
    initial_sidebar_state="expanded")

alt.themes.enable("dark")
st.markdown("<h1 style= 'text-align:center;'>Electricity Consumption Dashboard</h1> ", unsafe_allow_html=True)
st.write('')
st.markdown('Data Source: EIA')



df=pd.read_csv('recs2020_public_v7.csv')
df = df.dropna()

#=========================================================================================================
#                                   Features
#=========================================================================================================

#-------------------- average consumption vs.map--------------------
mean_KWH=df['KWH'].groupby(df['state_name']).mean()
mean_KWH_by_state = df.groupby('state_name')['KWH'].mean().reset_index()
mean_KWH_by_state.columns = ['State', 'Average_KWH']

# --------------------Urban/Rural vs energy consumption--------------------
# Urban area: 50,000 or more population
# Urban cluster: at least 2,500 and less than 50,000 population
urban_type_mapping = {
    'U': 'Urban',
    'R': 'Rural',
    'C': 'Urban Cluster',
}
df['UATYP10'] = df['UATYP10'].map(urban_type_mapping)
mean_KWH_by_Urbantype = df.groupby('UATYP10')['KWH'].mean().reset_index()
mean_KWH_by_Urbantype.columns = ['Urban_type', 'Average_KWH']
urban_type_order={'Urban_type':['Urban','Urban Cluster','Rural']}

#-------------------- Weather vs energy consumption--------------------
mean_KWH_by_Climate = df.groupby('BA_climate')['KWH'].mean().reset_index()
mean_KWH_by_Climate.columns = ['Climate_zone', 'Average_KWH']
weather_order={'Climate_zone':['Cold','Hot-Dry','Hot-Humid','Marine','Mixed-Dry',
                               'Mixed-Humid','Subarctic','Very-Cold']}
mean_KWH_by_Climate = mean_KWH_by_Climate.sort_values(by='Average_KWH', ascending=False)
#(2)Heating Degree Days
# HDD65

#(3) Cooling Degree Days
#CDD65

# --------------------House conditions vs energy consumption--------------------
#(1) Total number of rooms in the housing unit, excluding bathrooms; a derived variable
mean_KWH_by_Number_of_rooms = df.groupby('TOTROOMS')['KWH'].mean().reset_index()
mean_KWH_by_Number_of_rooms.columns = ['Number of rooms', 'Average_KWH']


#(2) Major outside wall material
wall_type_mapping = {
    1: 'Brick',
    2:'Wood',
    3: 'Siding(aluminum, fiber cement, vinyl, or steel)',
    4: 'Stucco',
    5: 'Shingle(composition)',
    6: 'Stone',
    7: 'Concrete block',
    99: 'Other'
}
df['WALLTYPE'] = df['WALLTYPE'].map(wall_type_mapping)
mean_KWH_by_Wall_type = df.groupby('WALLTYPE')['KWH'].mean().reset_index()
mean_KWH_by_Wall_type.columns = ['Wall_Type', 'Average_KWH']
wall_type_order={'Wall_Type':[ 'Brick','Wood', 'Siding(aluminum, fiber cement, vinyl, or steel)',
    'Stucco', 'Shingle(composition)', 'Stone', 'Concrete block', 'Other']}

#(3) Total energy-consuming area size
square_footage_mapping = {
    1: 'Less than 600 square feet',
    2: '600 to 799 square feet',
    3: '800 to 999 square feet',
    4: '1,000 to 1,499 square feet',
    5: '1,500 to 1,999 square feet',
    6: '2,000 to 2,499 square feet',
    7: '2,500 to 2,999 square feet',
    8: '3,000 square feet or more'
}
df['SQFTRANGE'] = df['SQFTRANGE'].map(square_footage_mapping)
mean_KWH_by_square_footage = df.groupby('SQFTRANGE')['KWH'].mean().reset_index()
mean_KWH_by_square_footage.columns = ['Square_footage', 'Average_KWH']
area_size_order={'Square_footage':['Less than 600 square feet', '600 to 799 square feet',
                                   '800 to 999 square feet', '1,000 to 1,499 square feet',
                                   '1,500 to 1,999 square feet', '2,000 to 2,499 square feet',
                                   '2,500 to 2,999 square feet', '3,000 square feet or more']}

#(4) Type of housing unit
housing_unit_type_mapping = {
    1: 'Mobile home',
    2: 'Single - family house detached from any other house',
    3: 'Single - family house attached to one or more other houses',
    4: 'Apartment in a building with 2 to 4 units',
    5: 'Apartment in a building with 5 or more units'
}
df['TYPEHUQ'] = df['TYPEHUQ'].map(housing_unit_type_mapping)
mean_KWH_by_housing_unit_type = df.groupby('TYPEHUQ')['KWH'].mean().reset_index()
mean_KWH_by_housing_unit_type.columns = ['House Unit Type', 'Average_KWH']

#(5) Own or rent
own_or_rent_mapping = {
    1: 'Own',
    2: 'Rent',
    3: 'Occupy without payment of rent'
}
df['KOWNRENT'] = df['KOWNRENT'].map(own_or_rent_mapping)
mean_KWH_by_own_or_rent = df.groupby('KOWNRENT')['KWH'].mean().reset_index()
mean_KWH_by_own_or_rent.columns = ['Own or Rent', 'Average_KWH']

# -------------------- Household characteristics vs energy consumption --------------------
#(1)household income level
household_income_mapping = {
    1: 'Less than $5, 000',
    2: '$5, 000 - $7, 499',
    3: '$7, 500 - $9, 999',
    4: '$10, 000 - $12, 499',
    5: '$12, 500 - $14, 999',
    6: '$15, 000 - $19, 999',
    7: '$20, 000 - $24, 999',
    8: '$25, 000 - $29, 999',
    9: '$30, 000 - $34, 999',
    10: '$35, 000 - $39, 999',
    11: '$40, 000 - $49, 999',
    12: '$50, 000 - $59, 999',
    13: '$60, 000 - $74, 999',
    14: '$75, 000 - $99, 999'

}
df['MONEYPY'] = df['MONEYPY'].map(household_income_mapping)
mean_KWH_by_household_income = df.groupby('MONEYPY')['KWH'].mean().reset_index()
mean_KWH_by_household_income.columns = ['Annual Gross Household income', 'Average_KWH']

household_income_order={'MONEYPY':['Less than $5, 000', '$5, 000 - $7, 499', '$7, 500 - $9, 999',
                        '$10, 000 - $12, 499', '$12, 500 - $14, 999', '$15, 000 - $19, 999',
                        '$20, 000 - $24, 999', '$25, 000 - $29, 999', '$30, 000 - $34, 999',
                        '$35, 000 - $39, 999', '$40, 000 - $49, 999', '$50, 000 - $59, 999',
                        '$60, 000 - $74, 999', '$75, 000 - $99, 999']}

income_order={'Annual Gross Household income':['Less than $5, 000', '$5, 000 - $7, 499', '$7, 500 - $9, 999',
                        '$10, 000 - $12, 499', '$12, 500 - $14, 999', '$15, 000 - $19, 999',
                        '$20, 000 - $24, 999', '$25, 000 - $29, 999', '$30, 000 - $34, 999',
                        '$35, 000 - $39, 999', '$40, 000 - $49, 999', '$50, 000 - $59, 999',
                        '$60, 000 - $74, 999', '$75, 000 - $99, 999']}


#(2) Number of household members
mean_KWH_by_Number_of_members = df.groupby('NHSLDMEM')['KWH'].mean().reset_index()
mean_KWH_by_Number_of_members.columns = ['Number of Members', 'Average_KWH']

#(3) Householder (respondent) race
household_race_mapping={
    1: 'White Alone', 2: 'Black or African/American Alone', 3:'American Indian or Alaska Native Alone',
    4: 'Asian Alone', 5: 'Native Hawaiian or Other Pacific Islander Alone',
    6: '2 or More Races Selected'
}
race_order={'Household_Race':['Asian Alone', 'Native Hawaiian or Other Pacific Islander Alone',
                              'American Indian or Alaska Native Alone','White Alone',
                              'Black or African/American Alone', '2 or More Races Selected']
            }
df['HOUSEHOLDER_RACE']=df['HOUSEHOLDER_RACE'].map(household_race_mapping)
mean_KWH_by_Household_race = df.groupby('HOUSEHOLDER_RACE')['KWH'].mean().reset_index()
mean_KWH_by_Household_race.columns = ['Household_Race', 'Average_KWH']

#(4) Highest level of education completed by respondent
household_education_mapping = {
    1: 'Less than high school diploma or GED',
    2: 'High school diploma or GED',
    3: 'Some college or Associate’s degree',
    4: 'Bachelor’s degree',
    5: 'Master’s, Professional, or Doctoral degree'
}
df['EDUCATION'] = df['EDUCATION'].map(household_education_mapping)
mean_KWH_by_Household_education = df.groupby('EDUCATION')['KWH'].mean().reset_index()
mean_KWH_by_Household_education.columns = ['Household_Education_Level', 'Average_KWH']
education_order={'Household_Education_Level':['Less than high school diploma or GED',
                                             'High school diploma or GED',
                                             'Some college or Associate’s degree',
                                             'Bachelor’s degree',
                                             'Master’s, Professional, or Doctoral degree']}

#(5) Ever participated in home energy assistance program
energy_assistant_mapping={1: 'Yes', 0: 'No'}
df['ENERGYASST']=df['ENERGYASST'].map(energy_assistant_mapping)
mean_KWH_by_energy_assistant=df.groupby('ENERGYASST')['KWH'].mean().reset_index()
mean_KWH_by_energy_assistant.columns=['Energy_Assistant', 'Average_KWH']



# ------------------------------ Appliances ------------------------------
#(1) most usage appliances
app_usage=df[['KWHSPH','KWHCOL','KWHWTH','KWHRFG','KWHFRZ','KWHCOK','KWHMICRO',
              'KWHCW','KWHCDR','KWHDWH','KWHLGT','KWHTVREL','KWHDHUM','KWHAHUHEAT',
              'KWHAHUCOL','KWHPLPMP','KWHHTBHEAT','KWHEVCHRG']].mean()
app_category={'KWHSPH':'space heating','KWHCOL':'space cooling','KWHWTH':'water heating',
              'KWHRFG':'refrigerators','KWHFRZ':'freezer','KWHCOK':'cooking',
              'KWHMICRO':'microwaves','KWHCW':'clothes washer','KWHCDR':'clothes dryers',
              'KWHDWH':'dishwashers','KWHLGT':'lighting', 'KWHTVREL':'televisions',
              'KWHDHUM':'dehumidifiers','KWHAHUHEAT':'distributing space heating via furnace fans and boiler pumps',
              'KWHAHUCOL':'furnace fans used for cooling','KWHPLPMP':'hot tub pumps',
              'KWHHTBHEAT':'hot tub heaters', 'KWHEVCHRG':'charging electric vehicles'}
app_usage = app_usage.reset_index()
app_usage.columns = ['Appliances', 'Average_KWH']
app_usage['Appliances']=app_usage['Appliances'].map(app_category)
app_usage = app_usage.sort_values(by='Average_KWH', ascending=False)
print(app_usage)

#(2)Thermostat type
thermostat_mapping={1: 'a manual or non-programmable thermostat',
                    2: 'a programmable thermostat',
                    3: 'a “smart” or Internet-connected thermostat',
                    0: 'Does not have thermostat for heating or cooling',
                    -2: 'Not applicable'}
df['TYPETHERM']=df['TYPETHERM'].map(thermostat_mapping)
mean_KWH_by_thermostat=df.groupby('TYPETHERM')['KWH'].mean().reset_index()
mean_KWH_by_thermostat.columns=['Thermostat_Type','Average_KWH']
print(mean_KWH_by_thermostat)

#(3) Number of smart speakers

mean_KWH_by_smartspeaker=df.groupby('SMARTSPK')['KWH'].mean().reset_index()
mean_KWH_by_smartspeaker.columns=['Number_of_Smart_Speaker','Average_KWH']


#(4) Portion of inside light bulbs that are LED
LED_portion_mapping={1: 'All', 2: 'Most', 3: 'About half', 4: 'Some', 0: 'None' }
df['LGTINLED']=df['LGTINLED'].map(LED_portion_mapping)

mean_KWH_by_led_portion=df.groupby('LGTINLED')['KWH'].mean().reset_index()
mean_KWH_by_led_portion.columns=['LED_Portion','Average_KWH']
led_portion_order={'LED_Portion':['None', 'Some', 'About half', 'Most','All']}


#=========================================================================================================
#                                   histogram graph
#=========================================================================================================

def hist(data,x, title):
    fig = px.histogram(data, x=x, y='Average_KWH', color=x)

    fig.update_layout(
        title_text=f'Average Household Electricity Consumption by {title}',
        xaxis_title=title,
        yaxis_title='Average KWH',
        bargap=0.2,

    )
    st.plotly_chart(fig)
    st.subheader(f"Average Household Electricity Consumption by {title}")
    st.dataframe(data, use_container_width=True)


#=========================================================================================================
#                                   Bar graph
#=========================================================================================================

def bar1(data,x, title,category_orders):
    fig = px.bar(data, x=x, y='Average_KWH', color=x,category_orders=category_orders)

    fig.update_layout(
        title_text=f'Average Household Electricity Consumption by {title}',
        xaxis_title=title,
        yaxis_title='Average KWH',
        bargap=0.2,

    )
    c1,c2=st.columns(2)
    with c1:
        st.plotly_chart(fig)
    with c2:
        st.subheader(f"Average Household Electricity Consumption by {title}")
        st.dataframe(data, use_container_width=True)

def bar2(data,x, title,category_orders):
    fig = px.bar(data, x=x, y='Average_KWH', color=x,category_orders=category_orders)

    fig.update_layout(
        title_text=f'Average Household Electricity Consumption by {title}',
        xaxis_title=title,
        yaxis_title='Average KWH',
        bargap=0.2,

    )
    st.plotly_chart(fig)
    st.subheader(f"Average Household Electricity Consumption by {title}")
    st.dataframe(data, use_container_width=True)



#=========================================================================================================
#                                   scatter plot
#=========================================================================================================

def scatter(data,x,y,title):
    fig = px.scatter(data, x, y, color=x)
    fig.update_layout(
        title_text=f'Average Household Electricity Consumption by {title}',
        xaxis_title=title,
        yaxis_title='KWH',
        bargap=0.2
    )
    st.plotly_chart(fig)
    st.subheader(f"Household Electricity Consumption by {title}")
    st.dataframe(data, use_container_width=True)


#=========================================================================================================
#                                   Box plot
#=========================================================================================================

def boxplot(data,x,y,title,category_orders):
    st.title(title)
    #category_column = st.selectbox('Select category column:', x)

    fig = px.box(data, x=x, y=y,category_orders=category_orders,color=x)
    fig.update_layout(
        title_text=f'Household Electricity Consumption by {title}',
        xaxis_title=title,
        yaxis_title='KWH',
        bargap=0.2
    )
    st.plotly_chart(fig)


#=========================================================================================================
#                                   Custom CSS
#=========================================================================================================

style="""
	<style>
	.stSelectbox >div[data-baseweb="select"]> div {height: 180% !important;
	      padding: 5px; font-family: 'Arial' !important; border: 2px solid #be0051 !important; font-weight: bold; 
	      font-size: 20px; 
	}
	</style>
	"""
st.markdown(style, unsafe_allow_html=True)


sidebar_style = """
<style>
.stSidebar>div {
        height: 200% !important;
        background-color: #D95F1A;
        padding: 4px;
        font-family: sans-serif;
        font-weight: bold;
        font-size: 42px !important;
	}

</style>
"""
st.markdown(sidebar_style, unsafe_allow_html=True)



#=========================================================================================================
#                                   Select Option
#=========================================================================================================
st.sidebar.title('Choose Sector')
page=st.sidebar.radio('', ['Data Visualization', 'Prediction'])
if page=='Predeiction':
    pass
elif page=='Data Visualization':
    option = st.selectbox(
        label='Critical Features for Household Electricity Consumption',
        options=['Location', 'Weather', 'House Conditions', 'Household Characteristics', 'Appliances'])
    if option == 'Location':
        geojson_path = 'contiguous-usa.geojson'
        # https://github.com/ResidentMario/geoplot-data/blob/master/contiguous-usa.geojson
        with open(geojson_path) as f:
            geojson_data = json.load(f)

        fig = px.choropleth(
            mean_KWH_by_state,
            geojson=geojson_data,
            locations='State',  # Column with state names
            featureidkey='properties.state',  # This depends on how state names are stored in the GeoJSON file
            color='Average_KWH',  # Column to use for color scale
            hover_name='State',  # Hover data: state names
            hover_data={'Average_KWH': ':.2f'},  # Format KWH to 2 decimal places
            color_continuous_scale='RdBu',  # Color scale
            labels={'Average_KWH': 'Avg KWH Consumption'},  # Label for the color bar
            scope='usa'  # Focus on the USA
        )

        # Update the layout of the map
        fig.update_layout(
            title_text='Average Household Electricity Consumption by State',
            geo=dict(
                showlakes=True,  # Show lakes
                lakecolor='rgb(255, 255, 255)'
            ),
            width=1000,
            height=700
        )

        # Display the map in Streamlit
        c1, c2 = st.columns(2)
        with c1:
            st.plotly_chart(fig, use_container_width=True)
        with c2:
            st.subheader("Average Household Electricity Consumption by State")
            st.dataframe(mean_KWH_by_state, use_container_width=True)

        bar1(mean_KWH_by_Urbantype, 'Urban_type', 'Urban Type', urban_type_order)

    elif option == 'Weather':
        bar1(mean_KWH_by_Climate, 'Climate_zone', 'Climate Zone', None)
        scatter(df, 'CDD65', 'KWH', 'Cooling Degree Days')
        scatter(df, 'HDD65', 'KWH', 'Heating Degree Days')
    elif option == 'House Conditions':
        # hist(mean_KWH_by_Number_of_rooms, 'Number of rooms', 'Number of Rooms')
        bar1(mean_KWH_by_Number_of_rooms, 'Number of rooms', 'Number of Rooms', None)
        bar1(mean_KWH_by_Wall_type, 'Wall_Type', 'Wall Type', wall_type_order)
        bar1(mean_KWH_by_square_footage, 'Square_footage', 'House Square footage', area_size_order)
        bar1(mean_KWH_by_housing_unit_type, 'House Unit Type', 'House Unit Type', None)
        bar1(mean_KWH_by_own_or_rent, 'Own or Rent', 'Own or Rent', None)
    elif option == 'Household Characteristics':
        # scatter(df, 'NHSLDMEM', 'KWH', 'Number of household members') #(1) Number of household members
        # scatter(df, 'MONEYPY', 'KWH', 'Annual gross household income')
        bar2(mean_KWH_by_household_income, 'Annual Gross Household income', 'Annual Gross Household Income',
             income_order)
        boxplot(df, df['MONEYPY'], df['KWH'], 'Annual Gross Household Income', household_income_order)
        data = df[['MONEYPY', 'KWH']]
        st.dataframe(data, use_container_width=True)
        bar1(mean_KWH_by_Number_of_members, 'Number of Members', 'Number of Household Members', None)
        bar1(mean_KWH_by_Household_education, 'Household_Education_Level', 'Household Education Level', education_order)
        bar1(mean_KWH_by_Household_race, 'Household_Race', 'Household Race', race_order)
        bar1(mean_KWH_by_energy_assistant, 'Energy_Assistant', 'Participating Energy Assistant', None)
    elif option == 'Appliances':
        bar2(app_usage, 'Appliances', 'Appliances', None)
        bar1(mean_KWH_by_thermostat, 'Thermostat_Type', 'Thermostat Type', None)
        bar1(mean_KWH_by_led_portion, 'LED_Portion', 'LED Portion', led_portion_order)
        bar1(mean_KWH_by_smartspeaker, 'Number_of_Smart_Speaker', 'Number of Smart Speaker', None)


#------------------------ Household characteristics vs energy consumption------------------------





#(2) Annual gross household income







#------------------------ Appliances vs energy consumption------------------------
#(1)
