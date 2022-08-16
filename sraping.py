#importing packages
import requests
from bs4 import BeautifulSoup
from time import sleep
import pandas as pd
import numpy as np

#what seasons do we use
#codes must be specified manually since there is no system in their naming
season_codes = {'2017': '6049', '2018': '6270', '2019': '6494', '2020': '6673','2021': '6733'}
seasons_used = ['2017', '2018', '2019', '2020','2021']

#the baseline class
class One_season:
    '''this class serves for creating a dataframe of games of a single season'''
    def __init__(self, season):
        self.season = season

    def get_link(self):
        code_of_season = season_codes[self.season]
        return f'https://nhl.cz/sezona/zapasy?matchList-filter-season={self.season}&matchList-filter-competition={code_of_season}'

    def get_soup(self):
        r = requests.get(self.get_link())
        if r.status_code == 200:
            r.encoding = 'UTF-8'
            return BeautifulSoup(r.text)
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

        #games cancelled due to covid were left blank and would cause errors
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

    def __init__(self, team, season):
        self.team = team
        self.season = season

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

#creating a dataframe with all games playd over all the considered seasons
individual_seasons = []

for season in seasons_used:
    individual_seasons.append(One_season(season).create_whole_df())

all_seasons = pd.concat(individual_seasons, ignore_index=True)

all_seasons.to_csv('all_seasons.csv')


