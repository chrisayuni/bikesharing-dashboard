import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from matplotlib.ticker import FuncFormatter

sns.set(style='dark')

def create_daily_rentals_df(df):
    daily_rentals_df = df.resample(rule='D', on='dteday').agg({
        "cnt": "sum"  
    })
  
    daily_rentals_df = daily_rentals_df.reset_index()
    daily_rentals_df.rename(columns={
        "cnt": "total_rentals"
    }, inplace=True)
    
    return daily_rentals_df

def create_sum_rentals_df(df):
    sum_rentals_df = df.groupby("dteday")['cnt'].sum().sort_values(ascending=False).reset_index()
    sum_rentals_df.rename(columns={'cnt': 'total_rentals'}, inplace=True)
    return sum_rentals_df

def create_by_hour_df(df):
    byhour_df = df.groupby(by="hr").cnt.sum().reset_index()
    byhour_df.rename(columns={
        "cnt": "total_rentals"
    }, inplace=True)
    return byhour_df

def create_by_season_df(df):
    byseason_df = df.groupby(by="season").cnt.sum().reset_index()
    byseason_df.rename(columns={
        "cnt": "total_rentals"
    }, inplace=True)
    return byseason_df

def create_by_time_group_df(df):
    by_time_group_df = df.groupby('time_group').cnt.sum().reset_index()
    by_time_group_df.rename(columns={"cnt": "total_rentals"}, inplace=True)
    return by_time_group_df

def create_by_membership_df(df):
    total_casual = df['casual'].sum()
    total_registered = df['registered'].sum()
    return {
        'Non-Member': total_casual,
        'Member': total_registered
    }

def create_weekday_member_df(df):
    weekday_member_df = df.pivot_table(
        index='weekday',
        values=['casual', 'registered'],
        aggfunc='sum'
    )
    return weekday_member_df

day_df = pd.read_csv("all_day.csv")
hour_df = pd.read_csv("all_hour.csv")

datetime_columns = ["dteday"]
day_df.sort_values(by="dteday", inplace=True)
day_df.reset_index(drop=True, inplace=True)

for column in datetime_columns:
    day_df[column] = pd.to_datetime(day_df[column])

min_date = day_df["dteday"].min()
max_date = day_df["dteday"].max()

with st.sidebar:
    st.image("https://github.com/chrisayuni/dataset/raw/main/bikesharing.png")
    
    start_date, end_date = st.date_input(
        label='Time Range',
        min_value=min_date,
        max_value=max_date,
        value=(min_date, max_date) 
    )

main_df = day_df[(day_df["dteday"] >= str(start_date)) & 
                (day_df["dteday"] <= str(end_date))]

daily_rentals_df = create_daily_rentals_df(main_df)
sum_rentals_df = create_sum_rentals_df(main_df)
by_hour_df = create_by_hour_df(hour_df)
by_season_df = create_by_season_df(main_df)
by_time_group_df = create_by_time_group_df(hour_df)
membership_df = create_by_membership_df(day_df)
weekday_member_df = create_weekday_member_df(day_df)

#VISUALISASI
st.header('Bike-Sharing Dashboard 🚲')

#SUBJUDUL1
st.subheader('Daily Rentals')
total_rentals = main_df['cnt'].sum() 
st.metric("Total Rentals", value=total_rentals)
fig, ax = plt.subplots(figsize=(16, 8))
ax.plot(
    main_df["dteday"],  
    main_df["cnt"],     
    marker='o', 
    linewidth=2,
    color="#E17F93" 
)
ax.tick_params(axis='y', labelsize=20)
ax.tick_params(axis='x', labelsize=15)
st.pyplot(fig)

#SUBJUDUL1
st.subheader("Best & Worst Performing Days")
fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(40, 15))
colors = ['#E17F93', '#F4C2C2', '#F4C2C2', '#F4C2C2', '#F4C2C2']

sns.barplot(x="cnt", y="dteday", data=day_df.sort_values(by="cnt", ascending=False).head(5), palette=colors, ax=ax[0])
ax[0].set_ylabel(None)
ax[0].set_xlabel(None)
ax[0].set_title("Days with Highest Rentals", loc="center", fontsize=45)
ax[0].tick_params(axis='y', labelsize=35)
ax[0].tick_params(axis='x', labelsize=40)  

sns.barplot(x="cnt", y="dteday", data=day_df.sort_values(by="cnt", ascending=True).head(5), palette=colors, ax=ax[1])
ax[1].set_ylabel(None)
ax[1].set_xlabel(None)
ax[1].invert_xaxis()
ax[1].yaxis.set_label_position("right")
ax[1].yaxis.tick_right()
ax[1].set_title("Days with Lowest Rentals", loc="center", fontsize=45)
ax[1].tick_params(axis='y', labelsize=35)
ax[1].tick_params(axis='x', labelsize=40)  

st.pyplot(fig)


#SUBJUDUL3
st.subheader('Hourly Rentals')

total_rentals_per_hour = hour_df.groupby('hr')['cnt'].sum().reset_index()
max_rentals_hour = total_rentals_per_hour['cnt'].max()
colors = ['#E17F93' if cnt == max_rentals_hour else '#F4C2C2' for cnt in total_rentals_per_hour['cnt']]

fig, ax = plt.subplots(figsize=(12, 6))
sns.barplot(x='hr', y='cnt', data=total_rentals_per_hour, palette=colors, ax=ax)
ax.set_xlabel("Hour of the Day", fontsize=15)
ax.set_ylabel("Total Rentals", fontsize=15)
ax.tick_params(axis='x', labelsize=15)
ax.tick_params(axis='y', labelsize=15)
st.pyplot(fig)

#SUBJUDUL4
st.subheader("Customer Demographics by Season and Time Category")
byseason_df = day_df.groupby(by="season")["cnt"].sum().reset_index()
season_names = {1: 'Spring', 2: 'Summer', 3: 'Fall', 4: 'Winter'}
byseason_df['season'] = byseason_df['season'].map(season_names)
byseason_df.rename(columns={"cnt": "total_rentals"}, inplace=True)

col1, col2 = st.columns(2)
with col1:
    fig, ax = plt.subplots(figsize=(40, 20))
    colors = ['#E17F93', '#F4C2C2', '#F4C2C2', '#F4C2C2']

    sns.barplot(
        x="season", 
        y="total_rentals", 
        data=byseason_df.sort_values(by="total_rentals", ascending=False),
        palette=colors,
        ax=ax
    )
    ax.set_title("Total Rentals by Season", loc="center", fontsize=85)
    ax.set_ylabel("Total Rentals", fontsize=75)
    ax.set_xlabel(None)  
    ax.tick_params(axis='y', labelsize=70)
    ax.tick_params(axis='x', labelsize=80)  
    ax.yaxis.set_major_formatter(FuncFormatter(lambda x, _: f'{int(x / 1000)}K'))
    st.pyplot(fig)

with col2:
    fig, ax = plt.subplots(figsize=(40, 20))
    colors = ['#F4C2C2', '#F4C2C2', '#F4C2C2', '#E17F93']

    sns.barplot(
        x="time_group",  
        y="total_rentals", 
        data=by_time_group_df.sort_values(by="total_rentals"),
        palette=colors,
        ax=ax
    )
    ax.set_title("Total Rentals by Time Category", loc="center", fontsize=85)
    ax.set_ylabel("Total Rentals", fontsize=75)
    ax.set_xlabel(None)  
    ax.tick_params(axis='y', labelsize=70)
    ax.tick_params(axis='x', labelsize=80)  
    ax.yaxis.set_major_formatter(FuncFormatter(lambda x, _: f'{int(x / 1000)}K'))
    st.pyplot(fig)

#SUBJUDUL5
st.subheader("Proportion of Member and Non-Member Rentals")

total_casual = day_df['casual'].sum()
total_registered = day_df['registered'].sum()

labels = ['Non-Member', 'Member']
sizes = [total_casual, total_registered]
colors = ['#F4C2C2', '#E17F93']  
explode = (0.1, 0) 
fig1, ax1 = plt.subplots(figsize=(3, 3))
ax1.pie(sizes, explode=explode, labels=labels, colors=colors,
        autopct='%1.1f%%', shadow=True, startangle=180, 
        textprops={'fontsize': 5}) 
ax1.axis('equal') 

for text in ax1.texts:
    text.set_fontsize(5) 

st.pyplot(fig1)
st.subheader('Comparison of Non-Member and Member Rentals by Weekday')
fig, ax = plt.subplots(figsize=(10, 6))
weekday_member_df.plot(kind='bar', ax=ax, color=['#F4C2C2', '#E17F93'])
ax.set_xlabel(None)
ax.set_ylabel('Total Rentals', fontsize=12)
ax.set_xticklabels(['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'], rotation=45)
ax.legend(labels=['Non-Member', 'Member'])
st.pyplot(fig)