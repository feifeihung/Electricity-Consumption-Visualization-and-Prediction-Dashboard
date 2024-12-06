import os
from itertools import groupby
from operator import concat
from pickle import FALSE

import streamlit as st
import pandas as pd
import altair as alt
import plotly.express as px
import matplotlib.pyplot as plt
import json
import seaborn as sns
import plotly.graph_objects as go
import joblib
from PIL import Image





df=pd.read_csv('recs2020_public_v7.csv')
df = df.dropna()
alt.themes.enable('dark')


#=========================================================================================================
#                                   Custom CSS
#=========================================================================================================

st.set_page_config(
    page_title="US Household Electricity Consumption Dashboard",
    page_icon=':derelict_house_building:' ,
    layout="wide",
    initial_sidebar_state="expanded")

background_style = """
<style>
    /* Set background color for the main content */
    .stApp {
        background-color:#000000; /* Choose your preferred color here #FFDAB9 */
	color: white; 
    }
    ##FFDAB9
        /* Increase font size and adjust DataFrame styling */
    .dataframe, .dataframe th, .dataframe td {
        font-size: 30px; /* Adjust this to your preferred font size */
        background-color: black; /* Set a background color if desired */
        padding: 10px; /* Increase padding for better spacing */
</style>
"""



# Apply the CSS style
st.markdown(background_style, unsafe_allow_html=True)

st.markdown("<h1 style= 'text-align:center; color:white;  '>U.S. Household Electricity Consumption Dashboard</h1> ", unsafe_allow_html=True)
st.write('')



selectbox_style="""
	<style>
	.stSelectbox >div[data-baseweb="select"]> div {height: 180% !important;
	      padding: 5px; font-family: 'Arial' !important; border: 2px solid #be0051 !important; font-weight: bold; 
	      font-size: 20px; 
	}
	</style>
	"""
st.markdown(selectbox_style, unsafe_allow_html=True)

selectnumber_style="""
	<style>
	.stNumberInput >div > input {
        height: 180% !important;
        padding: 5px;
        font-family: 'Arial' !important;
        border: 2px solid #be0051 !important;
        font-weight: bold;
        font-size: 20px;
    }
	</style>
	"""
st.markdown(selectnumber_style, unsafe_allow_html=True)



sidebar_style = """
<style>
    /* Set sidebar background color */
    .stSidebar {
        background-color: #D95F1A; color: #FAFAFA !important/* Sidebar background color */
    }
    /* Ensure all text in the sidebar is white */
    .stSidebar, .stSidebar * {
        color: #FAFAFA !important; font-size: 25px /* Set all text in sidebar to white */
    }
    /* Specifically target radio button labels */
    div[role="radiogroup"] label {
        color: #FAFAFA !important; 
	font-size: 44px !important; font-weight: bold;/* Force radio button text to white */
    }
    div[role="radiogroup"] {
        font-size: 25px !important; padding: 5px; font-weight: bold;/* This affects the entire radio group, including labels */
    }
</style>
"""
alt.themes.enable('dark')
st.markdown(sidebar_style, unsafe_allow_html=True)

with st.sidebar:
	st.markdown("<h1 style= 'color:#FAFAFA; font-size: 30px '> Select a Sector </h1>", unsafe_allow_html=True)

#data_viz_button = st.sidebar.button("Data Visualization",use_container_width=False,icon="🚨",on_click=callable,)
#prediction_button = st.sidebar.button("Prediction",use_container_width=False,icon="🚨",on_click=callable,)


	#page=st.sidebar.radio('Prediction', options=['📈Model Prediction', '📈Scenario Prediction'])
	page=st.sidebar.radio('',["📊Data Visualization", "📈Prediction"])



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

# Summer thermostat setting or temperature in home when someone is home during the day
COOLCNTL_mapping={1: 'Set one temperature and leave it there most of the time',
                  2: 'Manually adjust the temperature',
                  3: 'Programmable or smart thermostat automatically adjusts the temperature',
                  4: 'Turn equipment on or off as needed',
                  5: 'Our household does not have control over the temperature',
                  99: 'Other',
                  -2: 'Not applicable'}
df['COOLCNTL']=df['COOLCNTL'].map(COOLCNTL_mapping)
mean_KWH_by_COOLCNTL=df.groupby('COOLCNTL')['KWH'].mean().reset_index()
mean_KWH_by_COOLCNTL.columns=['Summer Temperature Control','Average_KWH']
print(mean_KWH_by_COOLCNTL)

#(3) Number of smart speakers

mean_KWH_by_smartspeaker=df.groupby('SMARTSPK')['KWH'].mean().reset_index()
mean_KWH_by_smartspeaker.columns=['Number_of_Smart_Speaker','Average_KWH']


#(4) Portion of inside light bulbs that are LED
LED_portion_mapping={1: 'All', 2: 'Most', 3: 'About half', 4: 'Some', 0: 'None' }
df['LGTINLED']=df['LGTINLED'].map(LED_portion_mapping)

mean_KWH_by_led_portion=df.groupby('LGTINLED')['KWH'].mean().reset_index()
mean_KWH_by_led_portion.columns=['LED_Portion','Average_KWH']
led_portion_order={'LED_Portion':['None', 'Some', 'About half', 'Most','All']}

#(5) Number of televisions used

FUELHEAT_mapping={5: 'Electricity',
                  1: 'Natural gas from underground pipes',
                  2: 'Propane (bottled gas)',
                  3: 'Fuel oil',
                  7: 'Wood or pellets',
                  99: 'Other',
                  -2: 'Not applicable'}
df['FUELHEAT']=df['FUELHEAT'].map(FUELHEAT_mapping)
mean_KWH_by_FUELHEAT=df.groupby('FUELHEAT')['KWH'].mean().reset_index()
mean_KWH_by_FUELHEAT.columns=['Space Heating Fuel','Average_KWH']



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
    #c1,c2=st.columns(2)
    c1, c2 = st.columns((3, 1.5), gap='medium')
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
#                                   Select Option
#=========================================================================================================
#st.sidebar.title('Choose Sector')
#page=st.sidebar.radio(['','Data Visualization', 'Prediction'])
import pickle


if page=='📊Data Visualization':
    st.markdown('Data Source: EIA')
    option = st.selectbox(
        label='Critical Features for Household Electricity Consumption',
        options=['Location', 'Weather', 'House Conditions', 'Household Characteristics', 'Appliances'])
    if option == 'Location':
        geojson_path = 'contiguous-usa.geojson'
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
            color_continuous_scale='viridis',  # Color scale
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
            coloraxis_colorbar=dict(
                title="Avg KWH",  # Title of the color bar
                len=0.8,  # Length of the color bar (50% of map height)
                thickness=15,  # Thickness in pixels
                # x=1.05,  # X position (moves it away from the map)
                # y=0.5,  # Y position (centers it vertically)
            ),
            width=800,
            height=500
        )

        # Display the map in Streamlit

        c1, c2 = st.columns((3, 1.5), gap='medium')
        with c1:
            st.plotly_chart(fig, use_container_width=False)
        with c2:
            mean_KWH_by_state = mean_KWH_by_state.sort_values(by='Average_KWH', ascending=False)
            st.markdown('#### Top States')

            st.dataframe(mean_KWH_by_state,
                         column_order=("State", "Average_KWH"),
                         hide_index=True,
                         width=None,
                         column_config={
                             "State": st.column_config.TextColumn(
                                 "State",
                             ),
                             "Average_KWH": st.column_config.ProgressColumn(
                                 "Average Electricity Consumption",
                                 format="%f",
                                 min_value=0,
                                 max_value=max(mean_KWH_by_state.Average_KWH),
                             )}
                         ,use_container_width=True)
#            st.subheader("Average Household Electricity Consumption by State")
#            st.dataframe(mean_KWH_by_state, use_container_width=True)

        bar1(mean_KWH_by_Urbantype, 'Urban_type', 'Urban Type', urban_type_order)

    elif option == 'Weather':
        bar1(mean_KWH_by_Climate, 'Climate_zone', 'Climate Zone', None)
        scatter(df, 'CDD65', 'KWH', 'Cooling Degree Days')
        scatter(df, 'HDD65', 'KWH', 'Heating Degree Days')

    elif option == 'House Conditions':
        # hist(mean_KWH_by_Number_of_rooms, 'Number of rooms', 'Number of Rooms')
        bar1(mean_KWH_by_Number_of_rooms, 'Number of rooms', 'Number of Rooms', None)
        #bar1(mean_KWH_by_Wall_type, 'Wall_Type', 'Wall Type', wall_type_order)
        bar1(mean_KWH_by_square_footage, 'Square_footage', 'House Square footage', area_size_order)
        bar1(mean_KWH_by_housing_unit_type, 'House Unit Type', 'House Unit Type', None)
        bar1(mean_KWH_by_Wall_type, 'Wall_Type', 'Wall Type', wall_type_order)

    elif option == 'Household Characteristics':
        # scatter(df, 'NHSLDMEM', 'KWH', 'Number of household members') #(1) Number of household members
        # scatter(df, 'MONEYPY', 'KWH', 'Annual gross household income')
        bar1(mean_KWH_by_Number_of_members, 'Number of Members', 'Number of Household Members', None)
        bar2(mean_KWH_by_household_income, 'Annual Gross Household income', 'Annual Gross Household Income',
             income_order)
        boxplot(df, df['MONEYPY'], df['KWH'], 'Annual Gross Household Income', household_income_order)
        data = df[['MONEYPY', 'KWH']]
        st.dataframe(data, use_container_width=True)
        bar1(mean_KWH_by_Household_education, 'Household_Education_Level', 'Household Education Level', education_order)
        bar1(mean_KWH_by_Household_race, 'Household_Race', 'Household Race', race_order)
        bar1(mean_KWH_by_energy_assistant, 'Energy_Assistant', 'Participating Energy Assistant', None)

    elif option == 'Appliances':
        bar2(app_usage, 'Appliances', 'Appliances', None)
        bar1(mean_KWH_by_FUELHEAT, 'Space Heating Fuel', 'Space Heating Fuel', None)
        bar1(mean_KWH_by_thermostat, 'Thermostat_Type', 'Thermostat Type', None)
        bar1(mean_KWH_by_COOLCNTL, 'Summer Temperature Control', 'Summer Temperature Control', None)
        bar1(mean_KWH_by_led_portion, 'LED_Portion', 'LED Portion', led_portion_order)
        bar1(mean_KWH_by_smartspeaker, 'Number_of_Smart_Speaker', 'Number of Smart Speaker', None)




#------------------------------------------Model Prediction------------------------------------------
elif page=='📈Prediction':
    prediction_option = st.sidebar.selectbox('choose Model Prediction/Scenario Prediction',
                                         ["Model Prediction", "Scenario Prediction"])
    if prediction_option=="Model Prediction":
        import pandas as pd
        import warnings
        import joblib
        warnings.filterwarnings("ignore")
        model = joblib.load('xgb.joblib')
        final_data = pd.read_csv('final_data.csv')
        df = final_data.drop('KWH', axis=1)

        st.title('Prediction of Household Annual Electricity Consumption')

        prediction = model.predict(df)
        data = pd.read_csv('recs2020_public_v7.csv')
        data1 = data[data.KWH <= 80000]
        data1['KWH'] = prediction
        fig = px.scatter(data1, data1['DOEID'], data1['KWH'])
        fig.update_layout(
            title_text='Predictive Annual Electricity Consumption',
            xaxis_title='Household ID',
            yaxis_title='KWH',
            bargap=0.2,
            width=800,
            height=450
        )
        st.plotly_chart(fig)
        st.subheader('Predictive Annual Electricity Consumption')
        data1 = data1.rename(columns={'DOEID': 'Household ID'})
        st.dataframe([data1['Household ID'],data1['KWH']], use_container_width=True)


        st.title('Prediction of One Household Annual Electricity Consumption')
        state_name = st.selectbox('State', ['Alabama', 'Alaska', 'Arizona', 'Arkansas', 'California',
                                            'Colorado', 'Connecticut', 'Delaware', 'District of Columbia',
                                            'Florida', 'Georgia', 'Hawaii', 'Idaho', 'Illinois', 'Indiana',
                                            'Iowa', 'Kansas', 'Kentucky', 'Louisiana', 'Maine', 'Maryland',
                                            'Massachusetts', 'Michigan', 'Minnesota', 'Mississippi', 'Missouri',
                                            'Montana', 'Nebraska', 'Nevada', 'New Hampshire', 'New Jersey',
                                            'New Mexico', 'New York', 'North Carolina', 'North Dakota',
                                            'Ohio', 'Oklahoma', 'Oregon', 'Pennsylvania', 'Rhode Island', 'South',
                                            'Carolina', 'South Dakota', 'Tennessee', 'Texas', 'Utah', 'Vermont',
                                            'Virginia', 'Washington', 'West Virginia', 'Wisconsin', 'Wyoming'])
        df2 = final_data[final_data['state_name'] == state_name]
        region = df2['REGIONC'].unique()[0]
        statepostal = df2['state_postal'].unique()[0]
        division = df2['DIVISION'].unique()[0]
        statefip = df2['STATE_FIPS'].unique()[0]
        uatype=df2['UATYP10'].unique()[0]
        climate = df2['BA_climate'].unique()
        #IECCclimatecode = df2['IECC_climate_code'].unique()[0]

        climate_zone = st.selectbox('Cilmate_Zone', climate)
        if climate_zone:
            IECCclimatecode = df2[df2['BA_climate'] == climate_zone]['IECC_climate_code'].unique()[0]
            #st.write(f"IECC Climate Code: {IECCclimatecode}")
        #IECCclimatecode = df2[df2['BA_climate']==climate_zone][0]
        SQFTEST = st.number_input('House Size(square feet)', value=None,
                                  placeholder="Enter the square feet of your house")  # enter value
        NHSLDMEM = st.selectbox('Number of Household Members', [1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
        YEARMADERANGE_mapping = {
            'Before 1950': '1',
            '1950 to 1959': '2',
            '1960 to 1969': '3',
            '1970 to 1979': '4',
            '1980 to 1989': '5',
            '1990 to 1999': '6',
            '2000 to 2009': '7',
            '2010 to 2015': '8',
            '2016 to 2020': '9',
         }
        YEARMADERANGE = st.selectbox('Range When Housing Unit Was Built',['Before 1950', '1950 to 1959', '1960 to 1969', '1970 to 1979', '1980 to 1989',
             '1990 to 1999', '2000 to 2009', '2010 to 2015', '2016 to 2020'])
        YEARMADERANGE_numeric = YEARMADERANGE_mapping[YEARMADERANGE]

        housing_unit_type_mapping = {
            1: 'Mobile home',
            2: 'Single - family house detached from any other house',
            3: 'Single - family house attached to one or more other houses',
            4: 'Apartment in a building with 2 to 4 units',
            5: 'Apartment in a building with 5 or more units'
        }
        #TYPEHUQ = st.selectbox('Housing unit type',['Mobile home', 'Single - family house detached from any other house',
        #                                          'Single - family house attached to one or more other houses',
        #                                          'Apartment in a building with 2 to 4 units',
        #                                          'Apartment in a building with 5 or more units'])
        #TYPEHUQ_numeric =housing_unit_type_mapping[TYPEHUQ]

        input_data = {
            'REGIONC': [region],
            'state_postal': [statepostal],
            'BA_climate': [climate_zone],
            'UATYP10': [uatype],
            'DIVISION': [division],
            'state_name': [state_name],
            'STATE_FIPS': [statefip],
            'IECC_climate_code': [IECCclimatecode],
            #'TOTROOMS': [TOTROOMS],
            # 'MONEYPY': [MONEYPY_numeric],
            'YEARMADERANGE':[YEARMADERANGE_numeric],
            'SQFTEST': [SQFTEST],
            'NHSLDMEM': [NHSLDMEM],
            #'TYPEHUQ': [TYPEHUQ],
            #'ELWATER': [ELWATER_numeric],
            #'FUELHEAT': [FUELHEAT_numeric],
            #'TOTCSQFT': [TOTCSQFT],
            #'TOTHSQFT': [TOTHSQFT],
            #'LGTIN1TO4': [LGTIN1TO4],
            # 'TVCOLOR': [TVCOLOR],
            #'HHAGE': [HHAGE]
        }


        def inputdata(state_name):
            # df2 = processed_data[processed_data['state_name'] == state_name]
            df2 = final_data[final_data['state_name'] == state_name]
            mean_values = df2.mean(numeric_only=True)
            for feature in mean_values.index:
                if feature not in input_data:
                    input_data[feature] = [mean_values[feature]]
            return input_data


        inputdata(state_name)
        input_data_df = pd.DataFrame(input_data)

        # Make the prediction
        if st.button("Predict", type='primary'):
            prediction = model.predict(input_data_df)
            # st.write("Predicted Electricity Consumption (KWH):", prediction[0])

            # st.markdown(
            #    f"""
            #            <div style="font-size:20px; color:#EB5406; font-weight: bold; font-style: italic; ">
            #                Predicted Household Electricity Consumption (KWH): {prediction[0]}
            #            </div>
            #            """,
            #    unsafe_allow_html=True
            # )
            average_state = final_data[final_data['state_name'] == state_name]['KWH'].mean()
            average = final_data['KWH'].mean()

            labels = ['Predictive Household', 'Average State Household', 'Average U.S. Household']
            values = [prediction[0], average_state, average]
            fig = px.bar(
                x=labels,
                y=values,
                color=labels,
                labels={'x': 'Categories', 'y': 'Values'},
                title="Household Energy Consumption"
            )
            fig.update_layout(
                xaxis_title="Categories",
                yaxis_title="Electricity Consumption (KWH)",
                title_font_size=20
            )

            # st.pyplot(fig)

            c1, c2 = st.columns((1, 1), gap='medium')
            with c2:
                st.plotly_chart(fig)
            with c1:
                st.markdown(
                    f"""
                                                <div style="font-size:25px; color:#EB5406; font-weight: bold; font-style: italic; ">
                                                    Predicted Household Electricity Consumption (kWh): {prediction[0]}
                                                </div>
                                                """,
                    unsafe_allow_html=True
                )












    # ------------------------------------------Scenario Prediction------------------------------------------


    elif prediction_option == "Scenario Prediction":
        import pandas as pd
        import warnings
        import joblib

        warnings.filterwarnings("ignore")

        model = joblib.load('xgb.joblib')

        final_data = pd.read_csv('final_data.csv')
        df = final_data.drop('KWH', axis=1)

        df_0 = df.drop(columns=['HDD65', 'CDD65'])

        HDD65_1 = df['HDD65'] * 1
        CDD65_1 = df['CDD65'] * 1
        df1 = pd.concat([df_0, HDD65_1.rename('HDD65'), CDD65_1.rename('CDD65')], axis=1)

        HDD65_2 = df['HDD65'] * 1.5
        CDD65_2 = df['CDD65'] * 1.5
        df2 = pd.concat([df_0, HDD65_2.rename('HDD65'), CDD65_2.rename('CDD65')], axis=1)

        # Make the prediction

        prediction_1 = model.predict(df1)
        prediction_2 = model.predict(df2)

        labels = ['Max', 'Mean', 'Min']
        values_1 = [prediction_1.max(), prediction_1.mean(), prediction_1.min()]
        values_2 = [prediction_2.max(), prediction_2.mean(), prediction_2.min()]


        def predic_bar(labels, values):
            fig = px.bar(
                x=labels,
                y=values,
                color=labels,
                labels={'x': 'Categories', 'y': 'Values'},
                title="Predictive Household Electricity Consumption in U.S"
            )
            fig.update_layout(
                xaxis_title="Categories",
                yaxis_title="Electricity Consumption (KWH)",
                title_font_size=20,
                width=800,
                height=450
            )

            st.plotly_chart(fig)


        df2['KWH'] = prediction_2
        mean_KWH = df2['KWH'].groupby(df2['state_name']).mean()
        mean_KWH_by_state_2 = df2['KWH'].groupby(df2['state_name']).mean().reset_index()
        mean_KWH_by_state_2.columns = ['State', 'Average_KWH']

        geojson_path = 'contiguous-usa.geojson'
        # https://github.com/ResidentMario/geoplot-data/blob/master/contiguous-usa.geojson
        with open(geojson_path, encoding='utf8') as f:
            geojson_data = json.load(f)

        fig = px.choropleth(
            mean_KWH_by_state_2,
            geojson=geojson_data,
            locations='State',  # Column with state names
            featureidkey='properties.state',  # This depends on how state names are stored in the GeoJSON file
            color='Average_KWH',  # Column to use for color scale
            hover_name='State',  # Hover data: state names
            hover_data={'Average_KWH': ':.2f'},  # Format KWH to 2 decimal places
            color_continuous_scale='greens',  # Color scale
            labels={'Average_KWH': 'Avg KWH Consumption'},  # Label for the color bar
            scope='usa'  # Focus on the USA
        )

        # Update the layout of the map
        fig.update_layout(
            title_text='Predictive Average Household Electricity Consumption by State',
            geo=dict(
                showlakes=True,  # Show lakes
                lakecolor='rgb(255, 255, 255)'
            ),
            coloraxis_colorbar=dict(
                title="Avg KWH",  # Title of the color bar
                len=0.8,  # Length of the color bar (50% of map height)
                thickness=15,  # Thickness in pixels
                # x=1.05,  # X position (moves it away from the map)
                # y=0.5,  # Y position (centers it vertically)
            ),
            width=800,
            height=450

        )








        # -----------------------------Scenario I: Surge Climate Change------------------------------------

        st.title('Scenario I: Surge Climate Change')
        st.write('HDD65 increases 25% and CDD65 increases 25%')
        # both HDD and CDD have increasing trend: https://www.eia.gov/outlooks/steo/data/browser/#/?v=28&f=A&s=&start=1999&end=2023&chartindexed=2&linechart=ZWCDPUS~ZWHDPUS~&maptype=0&ctype=linechart&map=&id=
        c1, c2 = st.columns((1, 2), gap='medium')
        with c1:
            max_row = df2.loc[df2['KWH'].idxmax()]
            max_state = max_row['state_name']
            max_value = max_row['KWH']
            st.metric(label=f"Max Consumption Household: {max_state}", value=f"{max_value:.2f} kWh")
            predic_bar(labels, values_2)

        with c2:
            max_row = mean_KWH_by_state_2.loc[mean_KWH_by_state_2['Average_KWH'].idxmax()]
            max_state = max_row['State']
            max_value = max_row['Average_KWH']

            min_row = mean_KWH_by_state_2.loc[mean_KWH_by_state_2['Average_KWH'].idxmin()]
            min_state = min_row['State']
            min_value = min_row['Average_KWH']
            c1, c2 = st.columns((1, 1), gap='medium')
            with c1:
                st.metric(label=max_state, value=f"{max_value:.2f} kWh", delta='Max')

            with c2:
                st.metric(label=min_state, value=f"{min_value:.2f} kWh", delta='Min')
            st.plotly_chart(fig, use_container_width=False)

        st.write(
            """
            <style>
            [data-testid="stMetric"] {
                border: 5px solid #959595; /* Add a light grey border */
                border-radius: 15px;    /* Rounded corners */
                padding: 10px;         /* Add some padding inside the border */
                background-color: #ccc; /* Optional: Light background for a better visual effect */
                font-weight: bold;
            }
            [data-testid="stMetricDelta"] svg {
                display: none; /* Hides the delta arrow */
            }
            </style>
            """,
            unsafe_allow_html=True,
        )

        st.title('Scenario II: Groundwater temperatures rise')
        st.write('Annual average ground water temperature increases 6.3°F')
        # The study, which was published in Nature Geoscience, indicates that by 2100,
        # groundwater temperatures will rise by 6.3°F.
        # https://www.ngwa.org/detail/news/2024/07/12/study-indicates-groundwater-temperature-increasing-6.3-f-by-2100#:~:text=The%20study%2C%20which%20was%20published,the%20strictest%20drinking%20water%20guidelines.
        GWT_1 = df['GWT'] + 6.3
        df_01 = df.drop('GWT', axis=1)
        df3 = pd.concat([df_01, GWT_1.rename('GWT')], axis=1)
        prediction_3 = model.predict(df3)
        labels = ['Max', 'Mean', 'Min']
        values_3 = [prediction_3.max(), prediction_3.mean(), prediction_3.min()]

        df3['KWH'] = prediction_3
        mean_KWH_by_state_3 = df3['KWH'].groupby(df3['state_name']).mean().reset_index()
        mean_KWH_by_state_3.columns = ['State', 'Average_KWH']

        geojson_path = 'contiguous-usa.geojson'

        with open(geojson_path, encoding='utf8') as f:
            geojson_data = json.load(f)

        fig = px.choropleth(
            mean_KWH_by_state_3,
            geojson=geojson_data,
            locations='State',  # Column with state names
            featureidkey='properties.state',  # This depends on how state names are stored in the GeoJSON file
            color='Average_KWH',  # Column to use for color scale
            hover_name='State',  # Hover data: state names
            hover_data={'Average_KWH': ':.2f'},  # Format KWH to 2 decimal places
            color_continuous_scale='blues',  # Color scale
            labels={'Average_KWH': 'Avg KWH Consumption'},  # Label for the color bar
            scope='usa'  # Focus on the USA
        )

        # Update the layout of the map
        fig.update_layout(
            title_text='Predictive Average Household Electricity Consumption by State',
            geo=dict(
                showlakes=True,  # Show lakes
                lakecolor='rgb(255, 255, 255)'
            ),
            coloraxis_colorbar=dict(
                title="Avg KWH",  # Title of the color bar
                len=0.8,  # Length of the color bar (50% of map height)
                thickness=15,  # Thickness in pixels
                # x=1.05,  # X position (moves it away from the map)
                # y=0.5,  # Y position (centers it vertically)
            ),
            width=800,
            height=450

        )
        c1, c2 = st.columns((1, 2), gap='medium')
        with c1:
            max_row = df3.loc[df3['KWH'].idxmax()]
            max_state = max_row['state_name']
            max_value = max_row['KWH']
            st.metric(label=f"Max Consumption Household: {max_state}", value=f"{max_value:.2f} kWh")
            predic_bar(labels, values_3)

        with c2:
            max_row = mean_KWH_by_state_3.loc[mean_KWH_by_state_3['Average_KWH'].idxmax()]
            max_state = max_row['State']
            max_value = max_row['Average_KWH']

            min_row = mean_KWH_by_state_3.loc[mean_KWH_by_state_3['Average_KWH'].idxmin()]
            min_state = min_row['State']
            min_value = min_row['Average_KWH']
            c1, c2 = st.columns((1, 1), gap='medium')
            with c1:
                st.metric(label=max_state, value=f"{max_value:.2f} kWh", delta='Max')

            with c2:
                st.metric(label=min_state, value=f"{min_value:.2f} kWh", delta='Min')
            st.plotly_chart(fig, use_container_width=False)

        # -----------------------------Scenario II: Consumer Behavior Changes------------------------------------

        st.title('Scenario III: Consumer Behavior Changes')
        st.write('Winter thermostat setting in home increases 1 °F (when no one is home during the day)')
        TEMPGONE_1 = df['TEMPGONE'] + 1
        df_02 = df.drop('TEMPGONE', axis=1)
        df4 = pd.concat([df_02, TEMPGONE_1.rename('TEMPGONE')], axis=1)
        prediction_4 = model.predict(df4)
        labels = ['Max', 'Mean', 'Min']
        values_4 = [prediction_4.max(), prediction_4.mean(), prediction_4.min()]

        df4['KWH'] = prediction_4
        mean_KWH_by_state_4 = df4['KWH'].groupby(df4['state_name']).mean().reset_index()
        mean_KWH_by_state_4.columns = ['State', 'Average_KWH']

        geojson_path = 'contiguous-usa.geojson'

        with open(geojson_path, encoding='utf8') as f:
            geojson_data = json.load(f)

        fig = px.choropleth(
            mean_KWH_by_state_4,
            geojson=geojson_data,
            locations='State',  # Column with state names
            featureidkey='properties.state',  # This depends on how state names are stored in the GeoJSON file
            color='Average_KWH',  # Column to use for color scale
            hover_name='State',  # Hover data: state names
            hover_data={'Average_KWH': ':.2f'},  # Format KWH to 2 decimal places
            color_continuous_scale='reds',  # Color scale
            labels={'Average_KWH': 'Avg KWH Consumption'},  # Label for the color bar
            scope='usa'  # Focus on the USA
        )

        # Update the layout of the map
        fig.update_layout(
            title_text='Predictive Average Household Electricity Consumption by State',
            geo=dict(
                showlakes=True,  # Show lakes
                lakecolor='rgb(255, 255, 255)'
            ),
            coloraxis_colorbar=dict(
                title="Avg KWH",  # Title of the color bar
                len=0.8,  # Length of the color bar (50% of map height)
                thickness=15,  # Thickness in pixels
                # x=1.05,  # X position (moves it away from the map)
                # y=0.5,  # Y position (centers it vertically)
            ),
            width=800,
            height=450

        )
        c1, c2 = st.columns((1, 2), gap='medium')
        with c1:
            max_row = df4.loc[df4['KWH'].idxmax()]
            max_state = max_row['state_name']
            max_value = max_row['KWH']
            st.metric(label=f"Max Consumption Household: {max_state}", value=f"{max_value:.2f} kWh")
            predic_bar(labels, values_4)

        with c2:
            max_row = mean_KWH_by_state_4.loc[mean_KWH_by_state_4['Average_KWH'].idxmax()]
            max_state = max_row['State']
            max_value = max_row['Average_KWH']

            min_row = mean_KWH_by_state_4.loc[mean_KWH_by_state_4['Average_KWH'].idxmin()]
            min_state = min_row['State']
            min_value = min_row['Average_KWH']
            c1, c2 = st.columns((1, 1), gap='medium')
            with c1:
                st.metric(label=max_state, value=f"{max_value:.2f} kWh", delta='Max')

            with c2:
                st.metric(label=min_state, value=f"{min_value:.2f} kWh", delta='Min')
            st.plotly_chart(fig, use_container_width=False)









#------------------------------------------Scenario Prediction------------------------------------------

#elif page1=='📈Scenario Prediction':


    # %%





















    
    
        













