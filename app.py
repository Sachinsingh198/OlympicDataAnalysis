import streamlit as st
import pandas as pd
import preprocessor, helper
import plotly.express as px
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.figure_factory as ff

st.set_page_config(page_title="Olympic Analysis", layout="wide", page_icon="🏅")

# Load Data
df = pd.read_csv('athlete_events.csv')
region_df = pd.read_csv('noc_regions.csv')
df = preprocessor.preprocess(df, region_df)

# Sidebar
st.sidebar.title("🏅 Olympic Analysis Dashboard")
st.sidebar.image('Olympics-Emblem.png', use_column_width=True)

user_menu = st.sidebar.radio(
    'Select an option',
    ('Medal Tally', 'Overall Analysis', 'Country-wise Analysis', 'Athlete-wise Analysis')
)

# ------------------- MEDAL TALLY -------------------
if user_menu == 'Medal Tally':
    st.sidebar.header("Medal Tally Filters")
    years, countries = helper.country_year_list(df)
    selected_year = st.sidebar.selectbox("Select Year", years)
    selected_country  = st.sidebar.selectbox("Select Country", countries)
    
    medal_tally = helper.fetch_medal_tally(df, selected_year, selected_country)

    # Dynamic title
    if selected_year == 'Overall' and selected_country == 'Overall':
        st.title('🏆 Overall Olympic Medal Tally')
    elif selected_year != 'Overall' and selected_country == 'Overall':
        st.title(f'🏆 Medal Tally in {selected_year} Olympics')
    elif selected_year == 'Overall' and selected_country != 'Overall':
        st.title(f'🏆 {selected_country} Overall Performance')
    else:
        st.title(f'🏆 {selected_country} in {selected_year} Olympics')
    
    st.dataframe(medal_tally.style.background_gradient(cmap='YlGnBu'))

# ------------------- OVERALL ANALYSIS -------------------
elif user_menu == 'Overall Analysis':
    st.title("📊 Top Statistics")
    
    editions = df['Year'].nunique() - 1
    cities = df['City'].nunique()
    sports = df['Sport'].nunique()
    events = df['Event'].nunique()
    atheletes = df['Name'].nunique()
    nations = df['region'].nunique()
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Editions", editions)
    col2.metric("Cities", cities)
    col3.metric("Sports", sports)
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Events", events)
    col2.metric("Athletes", atheletes)
    col3.metric("Nations", nations)
    
    # Time series plots
    st.subheader("🌎 Participating Nations Over the Years")
    nations_over_time = helper.data_over_time(df, 'region')
    fig = px.line(nations_over_time, x='Edition', y='region', markers=True)
    st.plotly_chart(fig, use_container_width=True)
    
    st.subheader("🏟️ Number of Events Over Time")
    events_over_time = helper.data_over_time(df, 'Event')
    fig = px.line(events_over_time, x='Edition', y='Event', markers=True)
    st.plotly_chart(fig, use_container_width=True)
    
    st.subheader("🏃 Athletes Over the Years")
    atheletes_over_time = helper.data_over_time(df, 'Name')
    fig = px.line(atheletes_over_time, x='Edition', y='Name', markers=True)
    st.plotly_chart(fig, use_container_width=True)
    
    st.subheader("🔥 Events per Sport Over Time")
    pivot_df = df.drop_duplicates(['Year','Sport','Event']).pivot_table(
        index='Sport', columns='Year', values='Event', aggfunc='count').fillna(0).astype(int)
    fig, ax = plt.subplots(figsize=(20, 12))
    sns.heatmap(pivot_df, annot=True, cmap='coolwarm', linewidths=0.5)
    st.pyplot(fig)

    # Most Successful Athletes
    st.subheader("🏅 Most Successful Athletes")
    sport_list = df['Sport'].unique().tolist()
    sport_list.sort()
    sport_list.insert(0, "Overall")
    selected_sport = st.selectbox('Select a Sport', sport_list)
    st.dataframe(helper.most_successful(df, selected_sport).style.highlight_max(axis=0, color='gold'))

# ------------------- COUNTRY-WISE ANALYSIS -------------------
elif user_menu == "Country-wise Analysis":
    st.title("🌍 Country Wise Analysis")
    countries_list = df['region'].dropna().unique().tolist()
    countries_list.sort()
    countries_list.insert(0, "Overall")
    selected_country = st.sidebar.selectbox('Select a Country', countries_list)
    
    # Medal tally
    country_df = helper.yearwise_medal_tally(df, selected_country)
    fig = px.line(country_df, x='Year', y='Medal', markers=True)
    st.subheader(f"{selected_country} Medal Tally Over the Years")
    st.plotly_chart(fig, use_container_width=True)
    
    # Heatmap
    if selected_country != "Overall":
        st.subheader(f"{selected_country} Excels in the Following Sports")
        pt = helper.country_event_heatmap(df, selected_country)
        if pt is not None and not pt.empty:
            fig, ax = plt.subplots(figsize=(20,12))
            sns.heatmap(pt, annot=True, cmap='YlGnBu', linewidths=0.5)
            st.pyplot(fig)
        else:
            st.warning("No heatmap data available for this country.")
    
    # Top 10 Athletes
    st.subheader(f"Top 10 Athletes of {selected_country}")
    top10_df = helper.most_successful_atheletes_country(df, selected_country)
    st.dataframe(top10_df.style.highlight_max(axis=0, color='gold'))

# ------------------- ATHLETE-WISE ANALYSIS -------------------
elif user_menu == 'Athlete-wise Analysis':
    st.title("🏃 Athlete Analysis")
    athelete_df = df.drop_duplicates(subset=['Name','region'])
    
    # Age Distribution
    st.subheader("📊 Distribution of Age")
    x1 = athelete_df['Age'].dropna()
    x2 = athelete_df[athelete_df['Medal']=='Gold']['Age'].dropna()
    x3 = athelete_df[athelete_df['Medal']=='Silver']['Age'].dropna()
    x4 = athelete_df[athelete_df['Medal']=='Bronze']['Age'].dropna()
    
    fig = ff.create_distplot([x1,x2,x3,x4],
                             ['Overall Age', 'Gold Medalist', 'Silver Medalist', 'Bronze Medalist'],
                             show_hist=False, show_rug=False)
    fig.update_layout(width=1000, height=600)
    st.plotly_chart(fig)
    
    # Height vs Weight
    st.subheader("⚖️ Height vs Weight")
    sport_list = df['Sport'].unique().tolist()
    sport_list.sort()
    sport_list.insert(0, "Overall")
    selected_sport = st.selectbox('Select a Sport', sport_list)
    
    temp_df = helper.weight_vs_height(df, selected_sport)
    fig, ax = plt.subplots(figsize=(10,8))
    sns.scatterplot(x=temp_df['Weight'], y=temp_df['Height'],
                    hue=temp_df['Medal'], style=temp_df['Sex'], s=100, palette='bright')
    plt.title(f"Height vs Weight ({selected_sport})", fontsize=16)
    st.pyplot(fig)

    # Men vs Women participation
    st.subheader("👨‍🦱👩‍🦰 Men vs Women Participation Over the Years")
    final = helper.men_vs_women(df)
    fig = px.line(final, x='Year', y=['Male','Female'], markers=True)
    fig.update_layout(width=1000, height=600)
    st.plotly_chart(fig, use_container_width=True)
