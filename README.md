### NHL predictions project
---
This is a project for the subject Data Processing in Python - JEM207. That was created by Pavlína Křenková and Vojtěch Vaverka.

The code scrapes data from the website https://nhl.cz/. After the data is scraped, the user of the code selects two teams from the dropdown menu. Those teams are then stored as variables *team_1* and *team_2*. Note that *team_1* should be the home team as the models based on past duels give a slight edge to the team under the variable *team_1*.

#### Structure of our project

##### Scraping data

First of all, we scrape the website https://nhl.cz/. This is done by the code that is located in *scraping.py* we scrape data for the last 5 seasons of NHL so from the season 2017/2018 to the season 2021/2022. Once the data is scraped it is stored in folder *teams_pre-processed* under *XXX_pre.csv* where XXX is the short name for the given team. Those are created by *teams_info.py* and then stored in *teams_info.csv*

#####  Processing data
*processing.py* is responsible for processing the data we have gathered. It creates columns for each team which we need for our models and graphs. Columns
* TOI_points_tot - Total number of points gained in last 20 matches by TOI (*team_1*)
* TOI_goals_scored_tot - Total number of goals scored in last 20 matches by TOI (*team_1*)
* TOI_goals_rec_tot - Total number of goals recived in last 20 matches by TOI (*team_1*)
* other_team_points_tot - Total number of points gained in last 20 matches by *team_2*
* other_team_goals_scored_tot - Total number of goals scored in last 20 matches by *team_2*
* other_team_goals_rec_tot - Total number of goals recived in last 20 matches by *team_2*

are created here once those columns are created and added the data is saved as csv inside the folder *teams_final* under *XXX.csv* where XXX stands for the short name of a given team. Data from this folder is then used.

#####  all_matches.csv
all_matches.csv is a file that contains all matches there we have scraped. NOT SURE FROM WHERE IT COMES PLS DOPLŇ

##### teams_info
Folder teams info contains *teams_info.py* that gets team name, code (code is /klub/2004 for example and this is based on how are teams marked on the website we are scraping), team_short is a short name for each team. This is then stored in *teams_info.csv*

##### nhl_project.ipynb
*nhl_project.ipynb* is our main file. It contains our models and graphs.

#### Models

We have 3 models in total to predict which team will win

##### Logistic regression model

This is our most complex model it is based on 7 variables which are 
* TOI_home - either one if TOI is home or 0 if TOI is away
* TOI_points_tot - Sum of points gained by TOI in the last 20 matches
* TOI_goals_scored_tot - Sum of goals scored by TOI in the last 20 matches
* TOI_goals_rec_tot - Sum of goals received by TOI in the last 20 matches
* other_team_points_tot - Sum of points gained by *team_2* in the last 20 matches
* other_team_goals_scored_tot - Sum of goals scored by *team_2* in last 20 matches
* other_team_goals_rec_tot - Sum of goals received by *team_2* in last 20 matches

Here TOI is an abbreviation for Team Of Interest this is the team in variable *team_1*, and the other team is the team under variable *team_2* The model then produces either value of one or zero. One means the TOI (*team_1*) will win the match and a value of 0 means that *team_2* will win.
We have calculated the accuracy of this model and it is 57.1% so it is better than random guessing by 7.1% which may not seem as much but in our eyes, it is a success.

##### Model based on wins in duels

Our second model is simpler than Logistic regression as it takes into account just the matches where the two teams have faced each other. This model works on counting the number of wins for each team and then saying which team will win based on which team has more wins. In the code, this works by summing the column *TOI_result* which has the value of one if TOI (*team_1*) won or zero if they lost. And then dividing this by the number of matches between teams.
Here is the home advantage we have discovered reflected slightly in the fact that when the value is 0.5, meaning that both teams have won and lost the same number of matches in duels the win is predicted for *team_1* which should be the home team.
The accuracy of this model is 53.26% which is a bit worst than the accuracy of the Logistic regression model. But the accuracy varies widely as for some duels the accuracy is 100% (42 duels) and for some 0% (24 duels). If we remove Seattle Kraken a team that has just recently joined NHL (they played NHL only in the season 2021/2022) so there is not as much data. Those numbers drop to 5 duels for 0% accuracy and 14 duels for 100% accuracy. So this model should not be used with Seattle Kraken as the small amount of data available makes it unreliable and highly variable.

##### Model based on points gained in duels

Our third model is simpler than Logistic regression as it takes into account just the matches where the two teams have faced each other. This model works by counting the number of points gained by each team and then saying which team will win based on which team has more wins. The difference between the second and third models is that not all wins result in 3 points if the win is achieved in overtime the teams get 2 points for the win and 1 for the loss. In the code, this works by summing the column *TOI_points* which stores the number of points gained by *team_1* in each match, and dividing it by the number of matches times three, as three is the number of points available for each match.
Here is the home advantage reflected slightly in the fact that when the value is 0.5, meaning that both teams have received the same amount of points in their duels. The win is assigned to *team_1* 

#### Some important variables and columns
* *match_ordr* this is created in nhl_project.ipynb and it is needed for models based on duels as it tells us the order in which the matches happened
* *team_1* this is a variable set by the user as he selects the home team for our models and graphs, *Team_1* is often marked as TOI
* *team_2* this is a variable set by the user as he selects the away team for our models and graphs
