import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.figure_factory as ff

import preprocessor
import preprocessor_s
import preprocessor_w


# ===============================
# LOAD DATA
# ===============================

@st.cache_data
def load_athletes_data():
    # Direct download link for your athletes data
    url = "https://drive.google.com/uc?id=1eMJa7EQ3HOfjE5-I8SGLVeMa9U0l0Skq"
    return pd.read_csv(url)

@st.cache_data
def load_noc_data():
    # Direct download link for your NOC data
    url = "https://drive.google.com/uc?id=1QH8c8aAFGKAKrzKfQuqiRTQro9rkvRbk"
    return pd.read_csv(url)


df= load_athletes_data()
noc= load_noc_data()




# Preprocess all once and store
data_dict = {
    'Overall': {'df': preprocessor.preprocess(df, noc), 'proc': preprocessor},
    'Summer': {'df': preprocessor_s.preprocess_s(df, noc), 'proc': preprocessor_s},
    'Winter': {'df': preprocessor_w.preprocess_w(df, noc), 'proc': preprocessor_w}
}

# ===============================
# STREAMLIT UI SETUP
# ===============================
st.sidebar.title('Olympics Analysis')

season = st.sidebar.radio('Select your Season', ('Overall', 'Summer', 'Winter'))
option = st.sidebar.radio(
    'Select an Option',
    ('Medal Tally', 'Overall Analysis', 'Country-wise Analysis', 'Athlete-wise Analysis')
)

df_current = data_dict[season]['df']
proc = data_dict[season]['proc']


# ===============================
# HELPER FUNCTIONS
# ===============================
def show_medal_tally(df, proc, title):
    years, countries = proc.year_country_list(df)
    selected_year = st.sidebar.selectbox('Select Year', years)
    selected_country = st.sidebar.selectbox('Select Country', countries)

    medal_tally = proc.fetch_medal_tally(df, year=selected_year, country=selected_country)

    if selected_year == 'Overall' and selected_country == 'Overall':
        st.header(f'{title} - Overall Medal Analysis')
    elif selected_year == 'Overall':
        st.header(f'{title} - Medal Analysis for {selected_country}')
    elif selected_country == 'Overall':
        st.header(f'{title} - Medal Analysis in {selected_year}')
    else:
        st.header(f'{title} - {selected_country} in {selected_year}')

    st.dataframe(medal_tally)


def show_overall_stats(df, proc, title):
    stats = {
        'Editions': len(df['Year'].unique()),
        'Cities': len(df['City'].unique()),
        'Sports': len(df['Sport'].unique()),
        'Events': len(df['Event'].unique()),
        'Athletes': len(df['Name'].unique()),
        'Nations': len(df['region'].unique())
    }

    st.title(f'Top {title} Statistics')
    col1, col2, col3 = st.columns(3)
    col4, col5, col6 = st.columns(3)
    cols = [col1, col2, col3, col4, col5, col6]

    for i, (k, v) in enumerate(stats.items()):
        with cols[i]:
            st.metric(k, v)

    # Participating nations over time
    nation_df = proc.nation_overall(df)
    st.header(f'Number of Participating Nations in {title}')
    fig = px.line(nation_df, x='Year', y='count')
    st.plotly_chart(fig)

    # Events heatmap
    st.header(f'Number of Events Over the Years - {title}')
    fig, ax = plt.subplots(figsize=(18, 14))
    x = df.drop_duplicates(['Year', 'Sport', 'Event'])
    sns.heatmap(
        x.pivot_table(index='Sport', columns='Year', values='Event', aggfunc='count')
        .fillna(0)
        .astype(int),
        annot=True,
        ax=ax
    )
    st.pyplot(fig)


def show_country_analysis(df, proc, country):
    medal_df = proc.country_year_medal(df, country)
    st.header(f'{country} Medal Analysis Over the Years')
    st.plotly_chart(px.scatter(medal_df, x='Year', y='Medal'))

    # Heatmap
    if hasattr(proc, 'country_heat'):
        heat_df = proc.country_heat(df, country)
        if heat_df.shape != (0, 0):
            st.header(f'{country} Performance in Events')
            fig, ax = plt.subplots(figsize=(18, 16))
            sns.heatmap(heat_df, annot=True, ax=ax)
            st.pyplot(fig)
        else:
            st.info("No heatmap data available for this country.")

    # Top athletes
    if hasattr(proc, 'most_success_10'):
        top_athletes = proc.most_success_10(df, country)
        st.header(f'Top 10 Athletes from {country}')
        st.table(top_athletes)


def show_athlete_analysis(df, proc):
    st.header('Athlete-Wise Analysis')

    sport_list = df['Sport'].dropna().unique().tolist()
    sport_list.sort()
    sport_list.insert(0, 'Overall')
    selected_sport = st.sidebar.selectbox('Select a Sport', sport_list)

    # Age distribution
    athlete_df = df.drop_duplicates(subset=['Name', 'region'])
    x = athlete_df['Age'].dropna()
    x1 = athlete_df[athlete_df['Medal'] == 'Gold']['Age'].dropna()
    x2 = athlete_df[athlete_df['Medal'] == 'Silver']['Age'].dropna()
    x3 = athlete_df[athlete_df['Medal'] == 'Bronze']['Age'].dropna()

    fig = ff.create_distplot(
        [x, x1, x2, x3],
        ['Overall', 'Gold Medalists', 'Silver Medalists', 'Bronze Medalists'],
        show_hist=False,
        show_rug=False
    )
    st.header('Probability of Winning a Medal at a Particular Age')
    st.plotly_chart(fig)

    # Men vs Women participation
    final = proc.men_women(df)
    st.header('Men vs Women Participation Over the Years')
    fig = px.line(final, x='Year', y=['Men', 'Women'])
    st.plotly_chart(fig)

    # Top athletes
    top_athletes = proc.most_successful(df, selected_sport)
    st.header(f'Top Performers in {selected_sport}')
    st.table(top_athletes)


# ===============================
# MAIN PAGE LOGIC
# ===============================
if option == 'Medal Tally':
    st.sidebar.header('Medal Tally')
    show_medal_tally(df_current, proc, f'{season} Olympics')

elif option == 'Overall Analysis':
    show_overall_stats(df_current, proc, season)

elif option == 'Country-wise Analysis':
    country_list = sorted(df_current['region'].dropna().unique().tolist())
    selected_country = st.sidebar.selectbox('Select Country', country_list)
    show_country_analysis(df_current, proc, selected_country)

elif option == 'Athlete-wise Analysis':
    show_athlete_analysis(df_current, proc)
