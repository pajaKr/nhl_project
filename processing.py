"""This python script processes the primary data files downloaded from the source website.
The .csv files that are saved are then used for further processing and interpretation
 in the data interpreter file."""

import pandas as pd
import numpy as np

season_codes = {'2017': '6049', '2018': '6270', '2019': '6494', '2020': '6673', '2021': '6733'}
seasons_used = ['2017', '2018', '2019', '2020', '2021']

teams_info = pd.read_csv('teams_info/teams_info.csv')

# we have to store teams and their codes, since there is also no system for that
# the dictionary contains code used in links of all the teams
dict_team_codes = pd.Series(teams_info.code.values, index=teams_info.team).to_dict()
distinct_teams = list(dict_team_codes.keys())

# we also need to store the short version of team names as we use them for file naming
teams_dict = pd.Series(teams_info.team_short.values, index=teams_info.team).to_dict()


def create_final_df(df):
    """this function calculates the data (goals, points) for last 20 games for each team which we then use for modelling"""
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


final_dfs = []  # list to store all the df together
for team in distinct_teams:
    short_name = teams_dict[team]
    df = pd.read_csv(f'teams_pre-processed/{short_name}_pre.csv')
    final = create_final_df(df)
    final_dfs.append(final)


def other_team_info(df):
    """For each game searches (based on game ID) the data (points, goals) about the other team and adds them to the
    dataframe."""
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
    df = df.reset_index(drop=True)
    return df


# We store all the dataframes individually, so we can later load them based on what teams we are analyzing.
for team in final_dfs:
    model_df = other_team_info(team)
    short_name = teams_dict[model_df.loc[1, "TOI"]]
    model_df.to_csv(f'teams_final/{short_name}.csv', index=False)
