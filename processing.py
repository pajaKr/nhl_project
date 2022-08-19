"""This python script processes the primary data files downloaded from the source website.
The .csv files that are saved are then used for further processing and interpretation
 in the data interpreter file."""

import requests
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np


def getSoup(link):
    r = requests.get(link)
    return BeautifulSoup(r.text, 'lxml')


season_codes = {'2017': '6049', '2018': '6270', '2019': '6494', '2020': '6673', '2021': '6733'}
seasons_used = ['2017', '2018', '2019', '2020', '2021']
codes = getSoup('https://nhl.cz/sezona/tymy')
team_info_list = codes.findAll('a', {'class': 'box-team__head'})
code_list = [x["href"] for x in team_info_list]
team_list = [h2.text for h2 in codes.findAll('h2')]
dict_team_codes = {team_list[i]: code_list[i] for i in range(len(code_list))}
distinct_teams = list(dict_team_codes.keys())
team_of_interest = "Boston Bruins"
code_of_interest = dict_team_codes[team_of_interest]
season_of_interest = '2021'
code_of_season = season_codes[season_of_interest]
soup = getSoup(
    f'https://nhl.cz{code_of_interest}/zapasy?matchList-filter-season={season_of_interest}&matchList-filter-competition={code_of_season}')
teams_long = [span.text for span in soup.findAll('span', {'class': 'preview__name--long'})]
teams_short = [span.text for span in soup.findAll('span', {'class': 'preview__name--short'})]
teams_dict = {}
for i in range(len(teams_long)):
    teams_dict[teams_long[i]] = teams_short[i]


def create_final_df(df):
    """this function calculates the data for last 20 games for each team which we then use for modelling"""
    TOI_points_tot = [None] * 20
    TOI_goals_scored_tot = [None] * 20
    TOI_goals_rec_tot = [None] * 20
    for x in range(len(df)):
        if x > 19:
            TOI_points_tot.append(int(df[['TOI_points']][x - 20:x].sum()))
            TOI_goals_scored_tot.append(int(df[['TOI_goals_scored']][x - 20:x].sum()))
            TOI_goals_rec_tot.append(int(df[['TOI_goals_rec']][x - 20:x].sum()))
    df['TOI_points_tot'] = TOI_points_tot
    df['TOI_goals_scored_tot'] = TOI_goals_scored_tot
    df['TOI_goals_rec_tot'] = TOI_goals_rec_tot
    return df[['game_id', 'TOI_result', 'TOI_home', 'TOI', 'other_team', 'TOI_points_tot',
               'TOI_goals_scored_tot', 'TOI_goals_rec_tot']][20:]


final_dfs = []
for team in distinct_teams:
    short_name = teams_dict[team]
    df = pd.read_csv(f'teams_pre-processed/{short_name}_pre.csv')
    final = create_final_df(df)
    final_dfs.append(final)


def other_team_info(df):
    other_team_points_tot = []
    other_team_goals_scored_tot = []
    other_team_goals_rec_tot = []
    for observation in range(len(df)):
        other_team = df.iat[observation, 4]
        other_team_index = distinct_teams.index(other_team)
        other_team_df = final_dfs[other_team_index]
        game_id = df.iat[observation, 0]
        radek = other_team_df.loc[other_team_df['game_id'] == game_id]
        if radek.empty:  # it is possible that the other team has not played 20 games yet
            other_team_points_tot.append(np.nan)
            other_team_goals_scored_tot.append(np.nan)
            other_team_goals_rec_tot.append(np.nan)
        else:
            other_team_points_tot.append(radek.iat[0, 5])
            other_team_goals_scored_tot.append(radek.iat[0, 6])
            other_team_goals_rec_tot.append(radek.iat[0, 7])
    df['other_team_points_tot'] = other_team_points_tot
    df['other_team_goals_scored_tot'] = other_team_goals_scored_tot
    df['other_team_goals_rec_tot'] = other_team_goals_rec_tot
    df = df.dropna()
    # dropping unnecessary columns
    df = df.reset_index(drop = True)
    return df


for team in final_dfs:
    model_df = other_team_info(team)
    short_name = teams_dict[model_df.loc[1, "TOI"]]
    model_df.to_csv(f'teams_final/{short_name}.csv', index=False)