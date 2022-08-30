# NHL predictions project
---
This is a project for the class Data Processing in Python - JEM207. It was created by Pavlína Křenková and Vojtěch Vaverka.

The code scrapes data from the website https://nhl.cz/. After the data is scraped, the user of the code selects two teams from the dropdown menu. Those teams are then stored as variables *team_1* and *team_2*. Note that *team_1* should be the home team as the models based on past duels give a slight edge to the team under the variable *team_1*.

## Structure of our project

### Scraping data

First of all, we scrape the website https://nhl.cz/. This is done by the code that is located in *scraping.py* we scrape data for the last 5 seasons of NHL so from the season 2017/2018 to the season 2021/2022. Once the data is scraped it is stored in the folder *teams_pre-processed* under *XXX_pre.csv* where XXX is the short name for the given team. Those short names are created by *teams_info.py* and then stored in *teams_info.csv*

###  Processing data
*processing.py* is responsible for processing the data we have gathered. It creates columns for each team which we need for our models and graphs. Columns
* TOI_points_tot - Total number of points gained in last 20 matches by TOI (*team_1*)
* TOI_goals_scored_tot - Total number of goals scored in last 20 matches by TOI (*team_1*)
* TOI_goals_rec_tot - Total number of goals received in last 20 matches by TOI (*team_1*)
* other_team_points_tot - Total number of points gained in last 20 matches by *team_2*
* other_team_goals_scored_tot - Total number of goals scored in last 20 matches by *team_2*
* other_team_goals_rec_tot - Total number of goals received in last 20 matches by *team_2*

are created here. Once those columns are created and added the data is saved as .csv inside the folder *teams_final* under *XXX.csv* where XXX stands for the short name of a given team. Data from this folder is then used.

#####  all_matches.csv
all_matches.csv is a file that contains all matches there we have scraped. This dataset is then used to calculate the home advantage. It was also constructed with the code in *scraping.py*.

##### teams_info
Folder called teams info contains *teams_info.py* that gets team name, code (code is /klub/2004, for example, and this is based on how are teams marked on the website we are scraping), team_short is a short name for each team, we use team_short for file naming. This info is then stored in *teams_info.csv*

##### nhl_project.ipynb
*nhl_project.ipynb* is our main file. It contains our models and graphs.

#### Some other important variables and columns
* *match_ordr* this is created in nhl_project.ipynb and it is needed for models based on duels as it tells us the order in which the matches happened
* *team_1* this is a variable set by the user as he selects the home team for our models and graphs, *Team_1* is often marked as TOI
* *team_2* this is a variable set by the user as he selects the away team for our models and graphs

### Models

We have 3 models in total to predict which team will win

#### Model based on wins in duels

Our first model is the most simple one as it takes into account just the matches where the two teams have faced each other. This model works on counting the number of wins for each team and then saying which team will win based on which team has more wins. In the code, this works by summing the column *TOI_result* which has the value of one if TOI (*team_1*) won or zero if they lost. And then dividing this by the number of matches between teams.

Here is the home advantage we have discovered reflected slightly in the fact that when the value is 0.5, meaning that both teams have won and lost the same number of matches in duels the win is predicted for the home team.

The accuracy of this model is 54.05% which is a bit worst than the accuracy of the Logistic regression model. But the accuracy varies widely as for some duels the accuracy is 100% (22 duels) and for some 0% (6 duels). If we remove Seattle Kraken a team that has just recently joined NHL (they played NHL only in the season 2021/2022) so there is not as much data. Those numbers drop to 0 duels for 0% accuracy and 6 duels for 100% accuracy. So this model should not be used with Seattle Kraken as the small amount of data available makes it unreliable and highly variable.


#### Logistic regression model

This is a more complex model which is based on the 7 following variables:
* TOI_home - either one if TOI is home or 0 if TOI is away
* TOI_points_tot - Sum of points gained by TOI in the last 20 matches
* TOI_goals_scored_tot - Sum of goals scored by TOI in the last 20 matches
* TOI_goals_rec_tot - Sum of goals received by TOI in the last 20 matches
* other_team_points_tot - Sum of points gained by *team_2* in the last 20 matches
* other_team_goals_scored_tot - Sum of goals scored by *team_2* in last 20 matches
* other_team_goals_rec_tot - Sum of goals received by *team_2* in last 20 matches

Here TOI is an abbreviation for Team Of Interest this is the team in variable *team_1*, and the other team is the team under variable *team_2* The model then produces either value of one or zero. One means the TOI (*team_1*) will win the match and a value of 0 means that *team_2* will win.
We have calculated the accuracy of this model and it is 55.7% so it is better than random guessing by 5.7% which may not seem as much but in our eyes, it is a success.


#### Neural Network

We build a 7-6-2-1 Neural network. This is the most complex model, which also yields the best results (mean accuracy above 57%). It uses the same variables as the Logistic regression as input parameters.

## Contribution

The contribution of this project is the following. It analyzes home advantage and teams' performance in a way that the standard nhl-focused websites, such as https://nhl.cz/, do not offer. It also predicts game outcomes by three different techniques, which were (to our knowledge) not implemented in this way before. It shows that a simple method such as estimating the game's outcome based on previous duels is very unstable and can have very low accuracy. On the contrary, using recognized econometric and machine learning techniques results in consistent, robust and stable prediction accuracy that can be significantly higher that just a random guess. The predictions can be used for entertainment, drawing interesting insights or casual betting; however, the authors do not take any responsibility if a user decides to do so.
