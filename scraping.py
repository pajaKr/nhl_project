"""this python file serves as a tool for downloading and saving data then used for interpretation
"""

# importing packages
import requests
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np

# what seasons do we use
# codes must be specified manually since there is no system in their naming...
# and they are also not mentioned anywhere in the "soups"
season_codes = {'2017': '6049', '2018': '6270', '2019': '6494', '2020': '6673', '2021': '6733'}
seasons_used = ['2017', '2018', '2019', '2020', '2021']

# we load the team codes, sice we need them for creating the links
teams_info = pd.read_csv('teams_info/teams_info.csv')

# we also have to store teams and their codes, since there is also no system for that
# the dictionary contains code used in links of all the teams
dict_team_codes = pd.Series(teams_info.code.values, index=teams_info.team).to_dict()
distinct_teams = list(dict_team_codes.keys())

# we also need to store the short version of team names as we use them for file naming
teams_dict = pd.Series(teams_info.team_short.values, index=teams_info.team).to_dict()


# the baseline class
class One_season:
    """this class serves for creating a dataframe of games of a single season"""

    def __init__(self, season):
        self.season = season

    def get_link(self):
        """Returns a link for scraping based on season of interest."""
        code_of_season = season_codes[self.season]
        return f'https://nhl.cz/sezona/zapasy?matchList-filter-season={self.season}&matchList-filter-competition={code_of_season}'

    def get_soup(self):
        """Returns a BeautifulSoup object from the created link."""
        r = requests.get(self.get_link())
        if r.status_code == 200:
            r.encoding = 'UTF-8'
            return BeautifulSoup(r.text, 'lxml')
        else:
            raise Exception(f'Cannot access the url. Returning status_code {r.status_code}')

    def get_goals(self, soup):
        """Returns list of goals of all matches from season of interest."""
        return [int(td.text) for td in soup.findAll('td', {'class': 'preview__score'})]

    def get_teams(self, soup):
        """Returns list of teams from each game played that season"""
        return [span.text for span in soup.findAll('span', {'class': 'preview__name--long'})]

    def get_OT(self, soup):
        """Returns a list of whether game ended in overtime for each game that season."""
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
        """Returns a list of game IDs that are specific to each game played that season."""
        game_ids_list = soup.find_all("a", href=lambda value: value and value.startswith("/zapas/"))
        game_ids = [x["href"] for x in game_ids_list][::2]
        return game_ids

    def create_df(self):
        """"Returns a dataframe from the information stored so far."""
        soup = self.get_soup()
        goals = self.get_goals(soup)
        teams = self.get_teams(soup)
        OT = self.get_OT(soup)
        game_ids = self.get_game_IDs(soup)

        # games cancelled due to covid were left blank on the website and would cause errors
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
        """Adds additional variables - points gained by homa and away team, and whether the home team won."""
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

        df["season"] = int(self.season)

        return df


class One_team_season(One_season):
    """This class saves dataframes for individual teams. It takes the One_season class
    as a parent, and the team attribute is added as it was not needed before.
    Also two functions are modified."""

    def __init__(self, team, season):
        super().__init__(season)
        self.team = team

    def get_link(self):
        """this function creates a link based on the specific team and season"""
        code_of_season = season_codes[self.season]
        code_of_interest = dict_team_codes[self.team]
        return f'https://nhl.cz{code_of_interest}/zapasy?matchList-filter-season={self.season}&matchList-filter-competition={code_of_season}'

    def create_whole_df(self):
        """This function creates the dataframe. Now using more variables then in the class One_season. Especially
        regarding the team of interest"""
        df = self.create_df()

        # how many points did home and away team obtain
        df.loc[(df["goals_home"] > df["goals_away"]) & (df["OT"] == 0), 'points_home'] = 3
        df.loc[(df["goals_home"] > df["goals_away"]) & (df["OT"] == 1), 'points_home'] = 2
        df.loc[(df["goals_home"] < df["goals_away"]) & (df["OT"] == 1), 'points_home'] = 1
        df.loc[(df["goals_home"] < df["goals_away"]) & (df["OT"] == 0), 'points_home'] = 0

        df.loc[(df["goals_home"] > df["goals_away"]) & (df["OT"] == 0), 'points_away'] = 0
        df.loc[(df["goals_home"] > df["goals_away"]) & (df["OT"] == 1), 'points_away'] = 1
        df.loc[(df["goals_home"] < df["goals_away"]) & (df["OT"] == 1), 'points_away'] = 2
        df.loc[(df["goals_home"] < df["goals_away"]) & (df["OT"] == 0), 'points_away'] = 3

        # whether the Team of Interest played home
        df.loc[df["team_home"] == self.team, 'TOI_home'] = 1
        df.loc[df["team_home"] != self.team, 'TOI_home'] = 0

        # How many points did Team of Interest gain
        df.loc[(df["TOI_home"] == 1), 'TOI_points'] = df["points_home"]
        df.loc[(df["TOI_home"] == 0), 'TOI_points'] = df["points_away"]

        # How many goals did Team of Interest score and received
        df.loc[(df["TOI_home"] == 1), 'TOI_goals_scored'] = df["goals_home"]
        df.loc[(df["TOI_home"] == 0), 'TOI_goals_scored'] = df["goals_away"]
        df.loc[(df["TOI_home"] == 1), 'TOI_goals_rec'] = df["goals_away"]
        df.loc[(df["TOI_home"] == 0), 'TOI_goals_rec'] = df["goals_home"]

        # Whether Team of Interest won (1) or lost (0)
        df.loc[(df["TOI_home"] == 1) & (df["points_home"] > df["points_away"]), 'TOI_result'] = 1  # 1 is a win
        df.loc[(df["TOI_home"] == 1) & (df["points_home"] < df["points_away"]), 'TOI_result'] = 0
        df.loc[(df["TOI_home"] == 0) & (df["points_home"] > df["points_away"]), 'TOI_result'] = 0
        df.loc[(df["TOI_home"] == 0) & (df["points_home"] < df["points_away"]), 'TOI_result'] = 1

        # The name of the other team than Team of Interest
        df.loc[(df["TOI_home"] == 1), 'other_team'] = df["team_away"]
        df.loc[(df["TOI_home"] == 0), 'other_team'] = df["team_home"]

        # The name of Team of Interest
        df.loc[(df["TOI_home"] == 1), 'TOI'] = df["team_home"]
        df.loc[(df["TOI_home"] == 0), 'TOI'] = df["team_away"]

        df["season"] = int(self.season)

        return df


# creating a dataframe with all games played over all the considered seasons
individual_seasons = []

for season in seasons_used:
    # We append each season through this for loop
    individual_seasons.append(One_season(season).create_whole_df())

all_seasons = pd.concat(individual_seasons, ignore_index=True)

all_seasons.to_csv('all_matches.csv', index=False)

# creating a dataframe for each team individually
individual_teams = []

for team_df in distinct_teams:
    one_team = []
    for season_df in seasons_used:
        # Seattle Kraken did not play seasons 2017,18,19,20 - we cannot create those dataframes and it would cause
        # an error
        if (team_df == 'Seattle Kraken') and (season_df in ['2017', '2018', '2019', '2020']):
            pass
        else:
            one_team.append(One_team_season(team_df, season_df).create_whole_df())
    one_team = pd.concat(one_team, ignore_index=True)
    short_name = teams_dict[team_df]
    one_team.to_csv(f'teams_pre-processed/{short_name}_pre.csv', index=False)
