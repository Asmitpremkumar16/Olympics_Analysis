import pandas as pd
import numpy as np


def preprocess(df,noc):
    df= df.merge(noc, on= 'NOC',how= 'left')
    df= df.drop_duplicates(keep= 'first')
    df= pd.concat([df, pd.get_dummies(df['Medal']).astype(int)], axis=1)

    return df


def medal_tally(df):
    medal_tally= df.drop_duplicates(subset=['Team','NOC','Games','Year','Season','City','Sport','Event','Medal'])
    medal_tally= medal_tally.groupby(['region']).sum()[['Gold','Silver','Bronze']].sort_values('Gold',ascending= False).reset_index()
    medal_tally['Total']= (medal_tally['Gold'] + medal_tally['Silver'] + medal_tally['Bronze'])

    return medal_tally
   

def year_country_list(df):
    years= df['Year'].unique().tolist()
    years.sort()
    years.insert(0,'Overall')

    country= np.unique(df['region'].dropna().values).tolist()
    country.sort()
    country.insert(0, 'Overall')

    return years, country


def fetch_medal_tally(df, year, country):
    medal_df = df.drop_duplicates(subset=['Team', 'NOC', 'Games', 'Year', 'City', 'Sport', 'Event', 'Medal'])
    flag = 0
    if year == 'Overall' and country == 'Overall':
        temp_df = medal_df
    if year == 'Overall' and country != 'Overall':
        flag = 1
        temp_df = medal_df[medal_df['region'] == country]
    if year != 'Overall' and country == 'Overall':
        temp_df = medal_df[medal_df['Year'] == int(year)]
    if year != 'Overall' and country != 'Overall':
        temp_df = medal_df[(medal_df['Year'] == year) & (medal_df['region'] == country)]

    if flag == 1:
        x = temp_df.groupby('Year').sum()[['Gold', 'Silver', 'Bronze']].sort_values('Year').reset_index()
    else:
        x = temp_df.groupby('region').sum()[['Gold', 'Silver', 'Bronze']].sort_values('Gold',ascending=False).reset_index()

    x['total'] = x['Gold'] + x['Silver'] + x['Bronze']

    return x


def nation_overall(df):
    return df.drop_duplicates(['Year','region'])['Year'].value_counts().sort_index(ascending=True).reset_index()

def country_year_medal(df,country):
    temp_df= df.dropna(subset=['Medal'])
    temp_df= temp_df.drop_duplicates(subset= ['Team', 'NOC', 'Games', 'Year', 'City', 'Sport', 'Event', 'Medal'])
    new_df = temp_df[temp_df['region'] == country]
    final_df= new_df.groupby('Year').count()['Medal'].reset_index()
    return final_df

def country_heat(df,country):
    temp_df= df.dropna(subset=['Medal'])
    temp_df= temp_df.drop_duplicates(subset= ['Team', 'NOC', 'Games', 'Year', 'City', 'Sport', 'Event', 'Medal'])
    new_df = temp_df[temp_df['region'] == country]
    return new_df.pivot_table(values= 'Medal',index= 'Sport',columns= 'Year',aggfunc= 'count').fillna(0).astype(int)


def most_success_10(df,country):
    temp_df= df.dropna(subset= ['Medal'])
    temp_df= temp_df[temp_df['region'] == country]
    return temp_df['Name'].value_counts().reset_index().merge(df, how= 'left')[['Name','Sex','count','Sport']].drop_duplicates(['Name']).rename(columns={'count':'Medal'}).head(10)


def men_women(df):
    athlete_df= df.drop_duplicates(subset= ['Name','region'])
    men= athlete_df[athlete_df['Sex'] == 'M'].groupby('Year').count()['Name'].reset_index()
    women= athlete_df[athlete_df['Sex'] == 'F'].groupby('Year').count()['Name'].reset_index()
    final= men.merge(women, on= 'Year', how= 'left').fillna(0)
    final= final.rename(columns= {'Name_x':'Men', 'Name_y':'Women'})
    return final
def most_successful(df, sport):
    temp_df = df.dropna(subset=['Medal'])

    if sport != 'Overall':
        if isinstance(sport, list):
            temp_df = temp_df[temp_df['Sport'].isin(sport)]
        else:
            temp_df = temp_df[temp_df['Sport'] == sport]

    result = (temp_df['Name'].value_counts().reset_index().merge(df[['Name', 'Sex','Sport', 'region']], on='Name', how='left').drop_duplicates(['Name']).rename(columns={'count': 'Medal'}).head(10))

    return result



