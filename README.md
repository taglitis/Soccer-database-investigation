# Soccer-database-investigation


## Introduction

Soccer plays an important role in our society. It does not only entertain people, but keeps soccer players in good health condition as well as attracts huge amount of money during FIFA and other games. Such games gather millions of people on stadiums and in front of TVs. Many fans bet on their favorite teams.  Some of them win and a lot of them loose their money. In order to predict and to increase a possibility that the game score will be in their favor we will investigate the European Soccer Database provided by Hugo Mathien (https://www.kaggle.com/hugomathien/soccer)

The following questions will be explored during the analysis: 
*	Do teams perform better when they play at home or away?
*	Determine teams which performance significantly improved. 
*	Does overall performance among all teams in 2008 and 2016 had been improved? 
*	Are there any correlations between total number of goals and team attributes? Can we find correlation between team attributes? 

## Exploratory analysis

**`Data extraction`**
Data is stored in SQLite database. Using DB browser for SQlite the data was initially investigated and queries were developed.  Then, the queries were passed to Python functions db_work() and db_team_attributes() in such way that the Python script interacts with the Python script directly obtaining the necessary dataset for further analysis. 

**`Data wrangling`**
Initial data investigation was performed in DB browser. From the first glance, it was obvious that tables with team attributes had many NaN values, which had to be removed. Therefore, it helped to understand type of data, columns name, its relationship between tables and other important information about available dataset.

**`Data cleaning`** 
Data cleaning was performed in db_work() and db_team_attributes() after the datasets were obtained. 
Number of rows with NaN values were calculated and then these rows were dropped. A similar check duplicated rows were performed and then, duplicated rows were dropped also. Results were stored in .csv files for further analysis.  

**Note:** Team names contain non-English characters and it brings the following error when a print function is called: “UnicodeEncodeError: 'charmap' codec can't encode character '\xf6' in position 56: character maps to <undefined>.”. After several attempts to change the codec to utf-8 and some other codecs a solution was found to save data into .csv files and then open it using cat in the terminal or in a spreadsheet such as Excel.  
