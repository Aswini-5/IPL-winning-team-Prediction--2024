import streamlit as st
import pickle
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

teams = ['Sunrisers Hyderabad', 'Mumbai Indians', 'Royal Challengers Bangalore', 'Kolkata Knight Riders',
         'Kings XI Punjab', 'Chennai Super Kings', 'Rajasthan Royals', 'Delhi Capitals']

cities = ['Hyderabad', 'Bangalore', 'Mumbai', 'Indore', 'Kolkata', 'Delhi', 'Chandigarh', 'Jaipur', 'Chennai',
          'Cape Town', 'Port Elizabeth', 'Durban', 'Centurion', 'East London', 'Johannesburg', 'Kimberley',
          'Bloemfontein', 'Ahmedabad', 'Cuttack', 'Nagpur', 'Dharamsala', 'Visakhapatnam', 'Pune', 'Raipur',
          'Ranchi', 'Abu Dhabi', 'Sharjah', 'Mohali', 'Bengaluru']

LogReg = pickle.load(open('LogReg.pkl', 'rb'))
Rf = pickle.load(open('Rf.pkl', 'rb'))
dt_clf = pickle.load(open('dt_clf.pkl', 'rb'))

st.title('Predict The Winning IPL Team')

# Load data
@st.cache_data
def load_data(nrows):
    data = pd.read_csv('matches.csv', nrows=nrows)
    return data

match = load_data(756)

match['team1'] = match['team1'].str.replace('Delhi Daredevils', 'Delhi Capitals')
match['team2'] = match['team2'].str.replace('Delhi Daredevils', 'Delhi Capitals')
match['winner'] = match['winner'].str.replace('Delhi Daredevils', 'Delhi Capitals')

match['team1'] = match['team1'].str.replace('Deccan Chargers', 'Sunrisers Hyderabad')
match['team2'] = match['team2'].str.replace('Deccan Chargers', 'Sunrisers Hyderabad')
match['winner'] = match['winner'].str.replace('Deccan Chargers', 'Sunrisers Hyderabad')

# Display image
st.image(r"C:\Users\kanag\Desktop\ipl prediction\d9e9cf7bf136b1580d579000dddeb6fc.jpg")

# Sidebar options
classifier_name = st.sidebar.selectbox('Select classifier', ('Logistic Regression', 'Random Forest', 'Decision Tree'))
season = st.sidebar.selectbox('Select Season', ('IPL-2008', 'IPL-2009', 'IPL-2010', 'IPL-2011', 'IPL-2012',
                                                'IPL-2013', 'IPL-2014', 'IPL-2015', 'IPL-2016', 'IPL-2017',
                                                'IPL-2018', 'IPL-2019'))
sel_team = st.sidebar.selectbox('Select Team Name', teams)

# Input form
batting_team = st.selectbox('Select the batting Team', sorted(teams))
bowling_team = st.selectbox('Select the bowling Team', sorted(teams))
selected_city = st.selectbox('Select host city', sorted(cities))
target = st.number_input('Target')
score = st.number_input('Score')
overs = st.number_input('Overs Completed')
wickets_out = st.number_input('Wicket out')

# Prediction button
if st.button('Predict Probability'):
    runs_left = target - score
    balls_left = 120 - (overs * 6)
    wickets_left = 10 - wickets_out
    crr = score / overs
    rrr = (runs_left * 6) / balls_left
    wickets = 10 - wickets_left  # Add wickets column based on wickets_left

    input_df = pd.DataFrame({'batting_team': [batting_team], 'bowling_team': [bowling_team], 'city': [selected_city],
                             'runs_left': [runs_left], 'balls_left': [balls_left], 'wickets_left': [wickets_left],
                             'wickets': [wickets], 'total_runs_x': [target], 'crr': [crr], 'rrr': [rrr]})

    if classifier_name == "Logistic Regression":
        result = LogReg.predict_proba(input_df)
    elif classifier_name == "Random Forest":
        result = Rf.predict_proba(input_df)
    else:
        result = dt_clf.predict_proba(input_df)
    loss = result[0][0]
    win = result[0][1]

    labels = [batting_team, bowling_team]
    sizes = [win, loss]
    explode = (0, 0.1)  # only "explode" the 2nd slice (i.e. 'Hogs')

    fig1, ax1 = plt.subplots(figsize=(2, 2))
    ax1.pie(sizes, explode=explode, labels=labels, autopct='%1.1f%%', shadow=True, startangle=90)
    ax1.set_title('Winnning Probability of Each Team')
    ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
    st.pyplot(fig1)

# Stats section
st.header('Some Stats')

# Performance of Teams in selected Season
if st.button('Performance of Teams in selected Season'):
    match_wins = match[match['Season'] == season]['winner'].value_counts()
    plt.figure(figsize=(10, 7))
    ax = sns.barplot(x=match_wins.index, y=match_wins.values, alpha=0.8)
    ax.set_xticklabels(ax.get_xticklabels(), rotation=40, ha="right")
    plt.title('Performance of Each Team')
    plt.ylabel('Number of Match Wins in the Season', fontsize=12)
    plt.xlabel('Teams', fontsize=12)
    plt.tight_layout()
    st.pyplot()

# Show Team Stats
if st.button('Show Team Stats'):
    df = match[(match['winner'] == sel_team)].groupby(['Season'])['id'].count()
    dff = match[(match['team1'] == sel_team) | (match['team2'] == sel_team)].groupby(['Season'])['id'].count()
    win = df.get(season, 0)
    total = dff.get(season, 0)
    loss = total - win
    data = {'win': [win], 'loss': [loss]}
    data = pd.DataFrame(data)
    st.write(data)
    st.bar_chart(data=data)
