# scrape_pfr_data

## Credits / Sources
Steve Morse - https://stmorse.github.io/journal/pfr-scrape-python.html

## Description
Scrapes team summary and player approximate value (AV) data from profootballreference.com into CSVs for analysis. The end result will be an enriched data file of players by team and year with AV data. Columns include:
* Yr - season
* Player - player name
* PlayerKey - unique PFR player key used to uniquely match players as many players will have the same name
* Age - player age that season
* Tm - normalized 3 letter abbreviation of team name
* Pos - the raw position from PFR
* PosGroup - normalized position matching the key draft position groups
* PositionGroup - a further rolled up PosGroup position grouping to allow analysis of all OL instead of separating IOL and T
* G - games played that season
* GS - games started that season
* AV - player approximate value generated that season
* AVperG - enriched (calculated) field of AV / games
* AVper16G - enriched (calculated) field of AVperG * 16 (this will need to be updated to handle 2021's 17 game season). This is used to show a potential or full season equivalent player value
* AdjAV - enriched (calculated) field to adjust what I believe is an AV flaw based on higher usage of nickel and dime defenses today (AV points are allocated 2/3 to the front seven in the PFR calculations, but this overstates AV for DL and LBs and understates AV for CB and S)
* AdjAVperG - same as AVperG but for AdjAV
* AdjAVper16G - same as AVper16G but for AdjAV
* CareerYr - identifies how many years in the league (1 is a rookie, 2 is second year, etc)
* 3YrAvgAV - average AV over 3 seasons (used in modeling projected output)
* PriorYr16GAV - prior year projected full season AV (used in modeling projected output)
* PriorYrAdj16GAV - prior year projected full season adjusted AV (used in modeling projected output)
* PriorYrG - prior year games played
* PriorYrGS - prior year games started
* Starter - indicates who were starters

## Technologies
* Python
* Pandas
* Numpy
* BeautifulSoup
* openpyxl

## Usage
### Pre-requisites:
There is some data that is manually added and not scraped automatically as the data is small and infrequently changes. Includes:
  * Super Bowl winners by year are defined in the sbdf dataframe in nfl-scrape-teams.py
  * teams-dvoa.csv is manually pulled, not scraped, from Football Outsiders (searching for "final team 2020 dvoa" will take you to the appropriate site such as https://www.footballoutsiders.com/dvoa-ratings/2021/final-2020-dvoa-ratings"). DVOA data is included for potential analysis.
  * Team abbreviations are set in the tmabrevdf dataframe in nfl-scrape-teams.py and nfl-scrape-players.py. These are current and will only need to be updated on a team move (to ensure the team's stats are combined) or expansion.
  * Position mappings are set manually in nfl-scrape-players.py. PFR is very inconsistent in how player positons are defined, players will switch positons or play hybrid roles, and season records are often blank. To handle this and allow for later analysis of normalized position names and groupings, these are manually set in the posdf and positionsdf dataframes:
    * posdf - maps the random PFR positions to normalized position names in the format "Off - POS" or "Def - POS". Each year, there are likely new positions that will show up in PFR and these need to be added to this dataframe - nfl-scrpae-players.py will output any new unknown positions, but they will need to be added here and re-run to ensure clean data.
    * positionsdf - this further consolidates posdf above into higher level groups in case needed for analysis. For example, posdf will define IOL and T separately (following draft position groupings) but positionsdf will group these both into "Off - OL" in case all offensive linemen need to be evaluated together

### Scrape team data
  * Edit "startyear" and "endyear" in nfl-scrape-teams.py to define the years of teams data to pull. Note: startyear is the most recent year (i.e., 2020) and endyear is the most distant year to pull (i.e., 2010 to pull the last decade)
  * From terminal run "python nfl-scrape-teams.py" which will output teams-data.xlsx and teams-data.csv which are needed for the next step

### Scrape player data
  * teams-data.xlsx (created above) is the driver file for nfl-scrape-players.py. When it is generated above, it is ready to go for the player scrape - the only reason this needs to be updated is if you want to re-run (need to reset the "scraped" column to 0 or just delete the file and re-run nfl-scrape-teams.py)
  * From terminal run "python nfl-scrape-players.py" which will output player-data.csv
