import numpy as np
import plotly.express as px

def fetch_medal_tally(df, year, country):
    medal_df = df.drop_duplicates(subset = ['Team', 'NOC', 'Games', 'Year','City', 'Event', 'Medal'])
    flag = 0
    if year == 'Overall' and country == 'Overall':
         temp_df = medal_df
    if year == 'Overall' and country != 'Overall':
         flag = 1
         temp_df = medal_df[medal_df['region'] == country]
    if year != 'Overall' and country == 'Overall':
         temp_df = medal_df[medal_df['Year'] == int(year)]
    if year != 'Overall' and country != 'Overall':
         temp_df = medal_df[(medal_df['Year'] == year) &( medal_df['region'] == country)]

    if flag == 1:
        x = temp_df.groupby('Year').sum()[['Gold', 'Silver', 'Bronze']].sort_values('Year', ascending = True).reset_index()
    else:
         x = temp_df.groupby('region').sum()[['Gold', 'Silver', 'Bronze']].sort_values('Gold', ascending = False).reset_index()
    x['Total'] = x['Gold'] + x['Silver'] + x['Bronze']

    x['Gold'] = x['Gold'].astype('int')
    x['Silver'] = x['Silver'].astype('int')
    x['Bronze'] = x['Bronze'].astype('int')
    x['Total'] = x['Total'].astype('int')

    return x


def medal_tally(df):
    medal_tally = df.drop_duplicates(subset=['Team','NOC','Games','Year','Games','Year','City','Sport','Event','Medal'])
    medal_tally = medal_tally.groupby('region').sum()[['Gold','Silver','Bronze']].sort_values('Gold', ascending = False).reset_index()

    medal_tally['total'] = medal_tally['Gold'] + medal_tally['Silver'] + medal_tally['Bronze']

    medal_tally['Gold'] = medal_tally['Gold'].astype('int')
    medal_tally['Silver'] = medal_tally['Silver'].astype('int')
    medal_tally['Bronze'] = medal_tally['Bronze'].astype('int')
    medal_tally['total'] = medal_tally['total'].astype('int')

    return medal_tally


def country_year_list(df):

    years = df['Year'].unique().tolist()
    years.sort()
    years.insert(0, 'Overall')

    country = np.unique(df['region'].dropna().values).tolist()
    country.sort()
    country.insert(0, 'Overall')

    return years, country


def data_over_time(df, col):
     df_clean = df.drop_duplicates(['Year', col])
     year_counts = df_clean['Year'].value_counts().reset_index()
     year_counts.columns = ['Year', 'Count']
     nations_over_time = year_counts.sort_values('Year')
     nations_over_time.rename(columns = {'Year': 'Edition', 'Count': col}, inplace = True)
     return nations_over_time


def most_successful(df, sport):
    # Drop rows with missing medals
    temp_df = df.dropna(subset=['Medal'])

    # Filter by sport if needed
    if sport != 'Overall':
        temp_df = temp_df[temp_df['Sport'] == sport]

    # Count medals per athlete
    medal_counts = temp_df['Name'].value_counts().reset_index()
    medal_counts.columns = ['Name', 'Medal_Count']

    # Get top 15
    top_15 = medal_counts.head(15)

    # Merge with original df to get extra info
    enriched = top_15.merge(df[['Name', 'Sport', 'region']], on='Name', how='left')

    # Drop duplicates to avoid multiple rows per athlete
    enriched = enriched.drop_duplicates(subset='Name')

    return enriched[['Name', 'Medal_Count', 'Sport', 'region']]


def yearwise_medal_tally(df, country):
     temp_df = df.dropna(subset=['Medal'])
     temp_df.drop_duplicates(subset = ['Team', 'NOC', 'Year', 'City', 'Sport', 'Event', 'Medal'], inplace = True)

     new_df = temp_df[temp_df['region'] == country]
     final_df = new_df.groupby('Year').count()['Medal'].reset_index()

     return final_df


def country_event_heatmap(df, country):
     temp_df = df.dropna(subset=['Medal'])
     temp_df.drop_duplicates(subset = ['Team', 'NOC', 'Year', 'City', 'Sport', 'Event', 'Medal'], inplace = True)

     new_df = temp_df[temp_df['region'] == country]
     pt = new_df.pivot_table(index='Sport', columns = 'Year', values='Medal', aggfunc='count').fillna(0).astype('int')

     return pt

def most_successful_atheletes_country(df, country):
    # Drop rows with missing medals
    temp_df = df.dropna(subset=['Medal'])

    # Filter by sport if needed
    
    temp_df = temp_df[temp_df['region'] == country]

    # Count medals per athlete
    medal_counts = temp_df['Name'].value_counts().reset_index()
    medal_counts.columns = ['Name', 'Medal_Count']

    # Get top 15
    top_15 = medal_counts.head(10)

    # Merge with original df to get extra info
    enriched = top_15.merge(df[['Name', 'Sport']], on='Name', how='left')

    # Drop duplicates to avoid multiple rows per athlete
    enriched = enriched.drop_duplicates(subset='Name')

    return enriched[['Name', 'Medal_Count', 'Sport']]


def weight_vs_height(df, sport):
     athelete_df = df.drop_duplicates(subset=['Name', 'region'])
     athelete_df['Medal'].fillna('No Medal', inplace=True)
     if sport != 'Overall':
          temp_df = athelete_df[athelete_df['Sport'] == sport]
          return temp_df
     else:
          return athelete_df
     

def men_vs_women(df):
     athelete_df = df.drop_duplicates(subset=['Name', 'region'])
     men = athelete_df[athelete_df['Sex'] == 'M'].groupby('Year').count()['Name'].reset_index()
     women = athelete_df[athelete_df['Sex'] == 'F'].groupby('Year').count()['Name'].reset_index()
     final = men.merge(women, on='Year', how='left')
     final.rename(columns={'Name_x': 'Male', 'Name_y':'Female'}, inplace=True)
     final.fillna(0, inplace=True)
     return final