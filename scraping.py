'''this python file serves as a downloader and a tool for saving data then used for interpretation
'''

# importing packages
import requests
from bs4 import BeautifulSoup
from time import sleep
import pandas as pd
import numpy as np


def getSoup(link):
    sleep(0.1)
    r = requests.get(link)
    return BeautifulSoup(r.text, 'lxml')


# what seasons do we use
# codes must be specified manually since there is no system in their naming
season_codes = {'2017': '6049', '2018': '6270', '2019': '6494', '2020': '6673', '2021': '6733'}
seasons_used = ['2017', '2018', '2019', '2020', '2021']

# we also have to store teams and their codes, since there is also no system for that
codes = getSoup('https://nhl.cz/sezona/tymy')
team_info_list = codes.findAll('a', {'class': 'box-team__head'})
code_list = [x["href"] for x in team_info_list]
team_list = [h2.text for h2 in codes.findAll('h2')]
# the dictionary contains code used in links of all the teams
dict_team_codes = {team_list[i]: code_list[i] for i in range(len(code_list))}
distinct_teams = list(dict_team_codes.keys())

# we also need to store the short version of team names as we use them for file naming
# those are stored only in team specific soups - we get it from auxiliary team
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


# the baseline class
class One_season:
    """this class serves for creating a dataframe of games of a single season"""

    def __init__(self, season):
        self.season = season

    def get_link(self):
        code_of_season = season_codes[self.season]
        return f'https://nhl.cz/sezona/zapasy?matchList-filter-season={self.season}&matchList-filter-competition={code_of_season}'

    def get_soup(self):
        r = requests.get(self.get_link())
        if r.status_code == 200:
            r.encoding = 'UTF-8'
            return BeautifulSoup(r.text, 'lxml')
        else:
            raise Exception(f'Cannot access the url. Returning status_code {r.status_code}')

    def get_goals(self, soup):
        return [int(td.text) for td in soup.findAll('td', {'class': 'preview__score'})]

    def get_teams(self, soup):
        return [span.text for span in soup.findAll('span', {'class': 'preview__name--long'})]

    def get_OT(self, soup):
        all_games = soup.findAll('tr')
        OT = []
        for game in all_games:
            ot = game.find('span', {'class': 'dot dot__blue'})
            if ot is None:
                OT.append(0)
            else:
                OT.append(1)
        return OT

    def get_game_IDs(self, soup):
        game_ids_list = soup.find_all("a", href=lambda value: value and value.startswith("/zapas/"))
        game_ids = [x["href"] for x in game_ids_list][::2]
        return game_ids

    def create_df(self):
        soup = self.get_soup()
        goals = self.get_goals(soup)
        teams = self.get_teams(soup)
        OT = self.get_OT(soup)
        game_ids = self.get_game_IDs(soup)

        # games cancelled due to covid were left blank and would cause errors
        if len(goals) / 2 == len(teams) / 2 == len(OT) == len(game_ids):
            pass
        else:
            teams = teams[:len(goals)]
            OT = OT[:int(len(goals) / 2)]
            game_ids = game_ids[:int(len(goals) / 2)]

        aux_dictionary = {'game_id': game_ids, 'team_home': teams[::2], 'team_away': teams[1::2],
                          'goals_home': goals[::2], 'goals_away': goals[1::2], 'OT': OT}
        df = pd.DataFrame(aux_dictionary)
        return df

    def create_whole_df(self):
        df = self.create_df()
        df.loc[(df["goals_home"] > df["goals_away"]) & (df["OT"] == 0), 'points_home'] = 3
        df.loc[(df["goals_home"] > df["goals_away"]) & (df["OT"] == 1), 'points_home'] = 2
        df.loc[(df["goals_home"] < df["goals_away"]) & (df["OT"] == 1), 'points_home'] = 1
        df.loc[(df["goals_home"] < df["goals_away"]) & (df["OT"] == 0), 'points_home'] = 0

        df.loc[(df["goals_home"] > df["goals_away"]) & (df["OT"] == 0), 'points_away'] = 0
        df.loc[(df["goals_home"] > df["goals_away"]) & (df["OT"] == 1), 'points_away'] = 1
        df.loc[(df["goals_home"] < df["goals_away"]) & (df["OT"] == 1), 'points_away'] = 2
        df.loc[(df["goals_home"] < df["goals_away"]) & (df["OT"] == 0), 'points_away'] = 3

        df.loc[(df["goals_home"] > df["goals_away"]), 'home_wins'] = 1
        df.loc[(df["goals_home"] < df["goals_away"]), 'home_wins'] = 0

        df["season"] = int(season)

        return df


class One_team_season(One_season):
    """This class saves dataframes for individual teams. It takes the One_season class
    as a parent, and the team attribute is added as it was not needed before.
    Also two functions are modified."""

    def __init__(self, team, season):
        self.team = team
        self.season = season

    def get_link(self):
        """this function creates a link based on the specific team and season"""
        code_of_season = season_codes[self.season]
        code_of_interest = dict_team_codes[self.team]
        return f'https://nhl.cz{code_of_interest}/zapasy?matchList-filter-season={self.season}&matchList-filter-competition={code_of_season}'

    def create_whole_df(self):
        """This function creates the dataframe. Now using more variables then in the class One_season"""
        df = self.create_df()
        df.loc[(df["goals_home"] > df["goals_away"]) & (df["OT"] == 0), 'points_home'] = 3
        df.loc[(df["goals_home"] > df["goals_away"]) & (df["OT"] == 1), 'points_home'] = 2
        df.loc[(df["goals_home"] < df["goals_away"]) & (df["OT"] == 1), 'points_home'] = 1
        df.loc[(df["goals_home"] < df["goals_away"]) & (df["OT"] == 0), 'points_home'] = 0

        df.loc[(df["goals_home"] > df["goals_away"]) & (df["OT"] == 0), 'points_away'] = 0
        df.loc[(df["goals_home"] > df["goals_away"]) & (df["OT"] == 1), 'points_away'] = 1
        df.loc[(df["goals_home"] < df["goals_away"]) & (df["OT"] == 1), 'points_away'] = 2
        df.loc[(df["goals_home"] < df["goals_away"]) & (df["OT"] == 0), 'points_away'] = 3

        df.loc[df["team_home"] == self.team, 'TOI_home'] = 1
        df.loc[df["team_home"] != self.team, 'TOI_home'] = 0

        df.loc[(df["TOI_home"] == 1), 'TOI_points'] = df["points_home"]
        df.loc[(df["TOI_home"] == 0), 'TOI_points'] = df["points_away"]

        df.loc[(df["TOI_home"] == 1), 'TOI_goals_scored'] = df["goals_home"]
        df.loc[(df["TOI_home"] == 0), 'TOI_goals_scored'] = df["goals_away"]
        df.loc[(df["TOI_home"] == 1), 'TOI_goals_rec'] = df["goals_away"]
        df.loc[(df["TOI_home"] == 0), 'TOI_goals_rec'] = df["goals_home"]

        df.loc[(df["TOI_home"] == 1) & (df["points_home"] > df["points_away"]), 'TOI_result'] = 1  # 1 is a win
        df.loc[(df["TOI_home"] == 1) & (df["points_home"] < df["points_away"]), 'TOI_result'] = 0
        df.loc[(df["TOI_home"] == 0) & (df["points_home"] > df["points_away"]), 'TOI_result'] = 0
        df.loc[(df["TOI_home"] == 0) & (df["points_home"] < df["points_away"]), 'TOI_result'] = 1

        df.loc[(df["TOI_home"] == 1), 'other_team'] = df["team_away"]
        df.loc[(df["TOI_home"] == 0), 'other_team'] = df["team_home"]

        df.loc[(df["TOI_home"] == 1), 'TOI'] = df["team_home"]
        df.loc[(df["TOI_home"] == 0), 'TOI'] = df["team_away"]

        df["season"] = int(season)

        return df


# creating a dataframe with all games playd over all the considered seasons
individual_seasons = []

for season in seasons_used:
    individual_seasons.append(One_season(season).create_whole_df())

all_seasons = pd.concat(individual_seasons, ignore_index=True)

all_seasons.to_csv('all_matches.csv', index=False)

# creating a dataframe for each team individually
individual_teams = []

for team in distinct_teams:
    one_team = []
    for season in seasons_used:
        try:
            one_team.append(One_team_season(team, season).create_whole_df())
        except:  # Seattle Kraken did not play seasons 2017,18,19,20 - we cannot create those dataframes
            pass
    one_team = pd.concat(one_team, ignore_index=True)
    short_name = teams_dict[team]
    one_team.to_csv(f'teams_pre-processed/{short_name}_pre.csv', index=False)
