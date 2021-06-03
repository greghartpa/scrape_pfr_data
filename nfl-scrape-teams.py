import numpy as np
import pandas as pd
import requests
from bs4 import BeautifulSoup
from bs4 import Comment

# Scrape player value data from PFR
url = 'https://www.pro-football-reference.com'
startyear = 2020
endyear = 2020
endyear = 2010

reccount = 0
totalcount = 0

# Read into team DVOA data to add to the team data for future analysis
dvoadf = pd.read_csv("teams-dvoa.csv")

# create dataframe of teams
column_names = ["Yr","Tm","W","L","T","PF","PA","SoS","Playoff","scraped"]
teamsdf = pd.DataFrame(columns = column_names)

# create temp dataframe to capture each team's year, name, and PFR url
tempcols = ["Yr","Tm","url"]
tempdf = pd.DataFrame(columns = tempcols)

# Step through all the years needed
year = startyear
while year >= endyear:
    print("Processing year " + str(year) + "...")

    # Scrape teams to get records and then iterate through rosters
    teamsurl = url + '/years/' + str(year)
    r = requests.get(teamsurl)
    soup = BeautifulSoup(r.content, 'html.parser')
    tables = soup.findAll('table', attrs = {'class':'sortable stats_table'})
    for teamtable in tables:
        totalcount = totalcount + reccount
        reccount = 0
        # scrape the team tables - AFC and NFC are split into different sections on PFR's website
        tdf = pd.read_html(str(teamtable))[0]
        tdf = tdf[~tdf['Tm'].str.startswith('AFC')]
        tdf = tdf[~tdf['Tm'].str.startswith('NFC')]
        # the playoff indicator is added to the team name on PFR's website - strip it into it's own column
        tdf['Playoff'] = np.where(tdf['Tm'].str.strip().str[-1] == '*', "DW",
            np.where(tdf['Tm'].str.strip().str[-1] == '+', "WC", ""))
        tdf['Tm'] = tdf['Tm'].map(lambda x: x.rstrip('*+'))
        # store the cleaned up year
        tdf['Yr'] = year
        # create a blank indicator if the team's players were scraped - this will be used in nfl-scrape-players.py
        tdf['scraped'] = 0
        # Some seasons don't have ties - check if the column is there, add it if not
        if 'T' not in tdf.columns:
            tdf['T'] = 0
        # copy the team records into the end dataframe
        selected_columns = tdf[['Yr','Tm','W','L','T','PF','PA','SoS','Playoff','scraped']]
        teamsdf = teamsdf.append(selected_columns, ignore_index=True)

        # Loop through html to grab the roster urls for later processing of player data
        table_body = teamtable.find('tbody')
        for row in table_body.find_all("tr"):
            for header in row.find_all("th", attrs = {'data-stat':'team'}):
                # Get team and it's roster url link
                team = header.text
                teamlink = header.find("a")
                teamlink = teamlink.get("href")
                rosterurl = url + teamlink[:-4] + "_roster.htm"
                team = team.rstrip('*+')
                tempdf.loc[len(tempdf.index)] = [year, team, rosterurl]

    # decrement to go back to next year to scrape
    year = year - 1

# Merge dataframes to capture roster url for later processing of player stats
teamsdf = pd.merge(teamsdf, tempdf, on=["Yr","Tm"], copy=False)
# Convert numeric columns to numeric
teamsdf["Yr"] = pd.to_numeric(teamsdf["Yr"])
teamsdf["W"] = pd.to_numeric(teamsdf["W"])
teamsdf["L"] = pd.to_numeric(teamsdf["L"])
teamsdf["T"] = pd.to_numeric(teamsdf["T"])
teamsdf["PF"] = pd.to_numeric(teamsdf["PF"])
teamsdf["PA"] = pd.to_numeric(teamsdf["PA"])
teamsdf["SoS"] = pd.to_numeric(teamsdf["SoS"])
# calculate the win percentage (ties count as a half win)
teamsdf['WinPct'] = (teamsdf['W'] + (0.5 * teamsdf['T'])) / (teamsdf['W'] + teamsdf['L'] + teamsdf['T']) * 100

# Correct the team name column to Tm as that is what I use across analysis scripts
teamsdf.rename(columns={"Tm": "FullTm"}, inplace=True)

# Add 3 letter team abbreviation and correct for team moves
data = {'FullTm':['Arizona Cardinals','Atlanta Falcons','Baltimore Ravens','Buffalo Bills','Carolina Panthers',
    'Chicago Bears','Cincinnati Bengals','Cleveland Browns','Dallas Cowboys','Denver Broncos',
    'Detroit Lions','Green Bay Packers','Houston Texans','Indianapolis Colts','Jacksonville Jaguars',
    'Kansas City Chiefs','Las Vegas Raiders','Los Angeles Chargers','Los Angeles Rams','Miami Dolphins',
    'Minnesota Vikings','New England Patriots','New Orleans Saints','New York Giants','New York Jets',
    'Oakland Raiders','Philadelphia Eagles','Pittsburgh Steelers','San Diego Chargers','San Francisco 49ers',
    'Seattle Seahawks','St. Louis Rams','Tampa Bay Buccaneers','Tennessee Titans','Washington Football Team',
    'Washington Redskins'],
    'Tm':['ARI','ATL','BAL','BUF','CAR',
    'CHI','CIN','CLE','DAL','DEN',
    'DET','GNB','HOU','IND','JAX',
    'KAN','LVR','LAC','LAR','MIA',
    'MIN','NWE','NOR','NYG','NYJ',
    'LVR','PHI','PIT','LAC','SFO',
    'SEA','LAR','TAM','TEN','WAS',
    'WAS']}
tmabrevdf = pd.DataFrame(data)
teamsdf = pd.merge(teamsdf, tmabrevdf, on="FullTm")

# Manually store the Super Bowl winners - I just manually do these given it's a small, annually updated dataset
data = {'Yr':[2005, 2006, 2007, 2008, 2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020],
    'Tm':['PIT','IND','NYG','PIT','NOR','GNB','NYG','BAL','SEA','NWE','DEN','NWE','PHI','NWE','KAN','TAM'],
    'SB':[1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]}
sbdf = pd.DataFrame(data)
teamsdf = pd.merge(teamsdf, sbdf, how="left", left_on=["Yr","Tm"], right_on=["Yr","Tm"])
teamsdf = teamsdf.replace(np.nan, '', regex=True)

#Add DVOA data
teamsdf = pd.merge(teamsdf, dvoadf, how="left", left_on=["Yr","Tm"], right_on=["Yr","Tm"])

# rearrange columns after adding the abbreviation
teamsdf = teamsdf[["Yr", "Tm", "FullTm", "W", "L", "T", "WinPct", "PF", "PA", "SoS",
    "DVOA", "DVOARank", "OffDVOA", "OffRank", "DefDVOA", "DefRank", "STDVOA", "STRank", "PriorYrDVOA",
    "Playoff", "SB", "scraped", "url"]]

teamsdf = teamsdf.sort_values(by=['Yr','Tm'], ascending=[False, True])
print(teamsdf)

# save team data to CSV and XLSX - the team data will be used to drive nfl-scrape-players.py
teamsdf.to_excel("teams-data.xlsx")
teamsdf.to_csv('teams-data.csv', index=False)
