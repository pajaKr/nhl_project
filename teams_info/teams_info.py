"""This script stores all necessary info """

import requests
from bs4 import BeautifulSoup
from time import sleep
import pandas as pd
import numpy as np

def getSoup(link):
    sleep(0.1)
    r = requests.get(link)
    return BeautifulSoup(r.text,'lxml')


season_codes = {'2017': '6049', '2018': '6270', '2019': '6494', '2020': '6673','2021': '6733'}

codes = getSoup('https://nhl.cz/sezona/tymy')
team_info_list = codes.findAll('a', {'class':'box-team__head'})
code_list = [x["href"] for x in team_info_list]
team_list = [h2.text for h2 in codes.findAll('h2')][:len(code_list)]
code_list_sorted = [x for _, x in sorted(zip(team_list, code_list))]
team_list_sorted = sorted(team_list)
dict_team_codes = {team_list[i]: code_list[i] for i in range(len(code_list))}

team_of_interest = "Boston Bruins"
code_of_interest = dict_team_codes[team_of_interest]
season_of_interest = '2021'
code_of_season = season_codes[season_of_interest]
soup = getSoup(f'https://nhl.cz{code_of_interest}/zapasy?matchList-filter-season={season_of_interest}&matchList-filter-competition={code_of_season}')
teams_long = [span.text for span in soup.findAll('span', {'class':'preview__name--long'})]
teams_short = [span.text for span in soup.findAll('span', {'class':'preview__name--short'})]
teams_dict = {}
for i in range(len(teams_long)):
    teams_dict[teams_long[i]] = teams_short[i]
teams_long_list = list(teams_dict.keys())
teams_short_list = list(teams_dict.values())
teams_short_list_sorted = [x for _, x in sorted(zip(teams_long_list, teams_short_list))]

info = {"team": team_list_sorted, "code": code_list_sorted, "team_short": teams_short_list_sorted}

info_df = pd.DataFrame(info)

info_df.to_csv(f'teams_info/teams_info.csv', index=False)
