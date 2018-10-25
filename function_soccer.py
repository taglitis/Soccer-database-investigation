import pandas as pd
import sqlite3
import matplotlib.pyplot as plt
import numpy as np


def db_work():
    """
    extracts datasets from DB

    OUTPUT:

    """
    path = "./input/"
    database = path + "database_soccer.sqlite"
    conn = sqlite3.connect(database)

# extract list of countries
    countries = pd.read_sql("""SELECT *
                               FROM Country;""", conn)
    countries.drop(['id'], axis = 1, inplace = True)

# get country with its team and goals, away country with goals
    goals_home_vs_away = pd.read_sql("""SELECT DISTINCT STRFTIME('%Y', date) AS year,
                                                        date AS full_date,
                                                        c.name AS country_name,
        	                                            home_team.team_long_name AS home_team,
                                                        match.home_team_api_id AS home_id,
        	                                            away_team.team_long_name AS away_team,
                                                        match.away_team_api_id AS away_id,
                        	                            home_team_goal,
                        	                            away_team_goal
                                        FROM match
                                        JOIN country AS c
                                          ON c.id = match.country_id
                                        JOIN League AS leag
                                          ON Leag.id = match.league_id
                                        LEFT JOIN team AS home_team
                                          ON home_team.team_api_id = match. home_team_api_id
                                        LEFT JOIN team AS away_team
                                          ON away_team.team_api_id = match.away_team_api_id
                                        ORDER BY 1  """, conn)
    return countries, goals_home_vs_away




def db_team_attributes():
    """
    from DB extract team attributes


    OUTPU:
    scatter plots
    """

    path = "./input/"
    database = path + "database_soccer.sqlite"
    conn = sqlite3.connect(database)


    team_attributes = pd.read_sql(""" SELECT STRFTIME('%Y', date) AS year,
                                                date AS full_date,
                                                team_api_id AS id,
                                                buildupplayspeed AS speed,
    											buildupplaydribbling AS gribbing,
    											buildupplaypassing AS pl_passing,
    											chancecreationpassing AS cr_passing,
    											chancecreationcrossing AS crossing,
    											chancecreationshooting AS shooting,
    											defencepressure AS pressure,
    											defenceaggression AS aggression,
    											defenceteamwidth AS width
                                        FROM Team_Attributes """, conn)
    team_attributes.dropna(inplace = True)
    team_attributes.to_csv('./datasets/team_attributes.csv')

    return team_attributes

def append_home_away_goals(goals_home_vs_away):
    """
    appends away dataset to home datasets

    INPUT:
    goals_home_vs_away datasets

    OUTPUT:
    home_away_goals - appended dataset

    """
    home_goals = goals_home_vs_away[['year', 'country_name','home_team','home_team_goal', 'home_id']]
    away_goals = goals_home_vs_away[['year', 'country_name','away_team','away_team_goal', 'away_id']]
    home_goals.rename(columns={'home_team' : 'team', 'home_team_goal' : 'total_goals', 'home_id' : 'id'}, inplace = True)
    away_goals.rename(columns={'away_team' : 'team', 'away_team_goal' : 'total_goals', 'away_id' : 'id'}, inplace = True)
    home_away_goals = home_goals.append(away_goals, ignore_index = True)
    return home_away_goals

def team_attributes_compare(goals_home_vs_away):
    """
    compares team team_attributes

    INPUT:
    goals_home_vs_away - dataset

    OUTPUT:
    scatter plots with team attributes
    """
    team_attributes = db_team_attributes()
    home_away_goals = append_home_away_goals(goals_home_vs_away)
    #group by year and id and find means of team attributes
    team_attributes_ave = team_attributes.groupby(['year', 'id'], as_index=False).mean()
    #find the total number of goals for each team
    home_away_goals_ave = home_away_goals.groupby(['year','id', 'team'], as_index=False).sum()
    #merge goals and attributes
    team_attributes_goals_ave= home_away_goals_ave.merge(team_attributes_ave, left_on='id', right_on='id', how='inner')
    #plot it
    fig, ax1 = plt.subplots()
    pd.plotting.scatter_matrix(team_attributes_goals_ave.drop(columns = 'id'))
    plt.savefig('./plots/mattix.png', dpi=600)
    fig.clf()
    #plot 3 scatter plot from matrix
    plt.subplot(3,1,1)
    plt.scatter(team_attributes_goals_ave['pl_passing'], team_attributes_goals_ave['total_goals'])
    corr = np.corrcoef(team_attributes_goals_ave['pl_passing'], team_attributes_goals_ave['total_goals'])
    plt.text(70,103, "correlation coef: " + format(corr[0,1], ".2f"))
    plt.title('Relationship between parameter Build up Play passing and number of goals')
    plt.xlabel('Build up Play passing')
    plt.ylabel('Number of goals')
    plt.subplot(3,1,2)

    plt.scatter(team_attributes_goals_ave['pressure'], team_attributes_goals_ave['total_goals'])
    corr = np.corrcoef(team_attributes_goals_ave['pressure'], team_attributes_goals_ave['total_goals'])
    plt.text(64,115, "correlation coef: " + format(corr[0,1], ".2f"))
    plt.title('Relationship between parameter Defence pressure and number of goals')
    plt.xlabel('Defence pressure')
    plt.ylabel('Number of goals')

    plt.subplot(3,1,3)
    plt.scatter(team_attributes_goals_ave['pressure'], team_attributes_goals_ave['aggression'])
    corr = np.corrcoef(team_attributes_goals_ave['pressure'], team_attributes_goals_ave['aggression'])
    plt.text(66,69, "correlation coef: " + format(corr[0,1], ".2f"))
    plt.title('Relationship between parameter Defence pressure and Defence aggression')
    plt.xlabel('Defence pressure')
    plt.ylabel('Defence aggression')
    plt.tight_layout()
    plt.show()


def goals_ave_compare(goals_home_vs_away):
    """
    compares average number of team goals for 2 years

    INPUT:
    goals_home_vs_away - dataset

    OUTPUT:
    bar graph
    """

    years = ['2008', '2016']
    bins_v = 20
    bin_names = []
    home_away_goals = append_home_away_goals(goals_home_vs_away)
    home_away_goals.to_csv('./datasets/home_away_goals_1.csv')
    i = 0
    #intervals might not match, so define min and max values for 2 different years
    for year in years:
        home_away_goals_year = home_away_goals.query('year == "{}"'.format(year))
        if i == 0:
            min = home_away_goals_year.groupby('team', as_index = False).mean().total_goals.min()
            max = home_away_goals_year.groupby('team', as_index = False).mean().total_goals.max()
        else:
            min_new = home_away_goals_year.groupby('team', as_index = False).mean().total_goals.min()
            max_new = home_away_goals_year.groupby('team', as_index = False).mean().total_goals.max()
            if min_new < min: min = min_new
            if max_new > max: max = max_new

        i += 1
    #define edges
    bin_edges = np.linspace(min-.00001, max+0.00001, bins_v)
    #the middle of each interval
    delta = (bin_edges[1] - bin_edges[0]) / 2
    #declare a lost of locations
    locations = []
    #width of a bar
    width = delta/2
    #define each location
    for i in range(bins_v-1):
        locations.append(bin_edges[i] + delta)
    #create a plot
    fig, ax = plt.subplots(figsize=(8,6))
    for year in years:
        home_away_goals_local_ave = home_away_goals.query('year == "{}"'.format(year)).groupby('team').mean()
        home_away_goals_local_ave['locations'] = pd.cut(home_away_goals_local_ave['total_goals'], bin_edges, labels = locations)
        hist_data = home_away_goals_local_ave.groupby('locations', as_index=False).count()
        hist_data['total_goals'] = hist_data['total_goals'] / hist_data['total_goals'].sum()
        mean_v = format(home_away_goals_local_ave['total_goals'].mean(), ".2f")
        label_v = year +', mean value: ' + str(mean_v)
        plt.bar(locations, height = hist_data['total_goals'], alpha=0.7, width = width, label = label_v)
        for i in range(bins_v-1):
            locations[i] = locations[i] + width
    label_v = []
    for i in range(bins_v - 1):
        locations[i] = locations[i] - 2*width
        label_v.append(format(locations[i], '.2f'))
        locations[i] = locations[i] + width / 2
    plt.title('Comparison of probability distributions of goals mean values for {} and {}'.format(years[0], years[1]))
    plt.xticks(locations, label_v)
    plt.xlabel('average number of goals')
    plt.legend()
    plt.savefig('./plots/goals_ave_compare.png')
    fig.clf()

def improved_teams(goals_home_vs_away):
    """
    defines 5 teams which improved the most since 2008

    INPUT:
    goals_home_vs_away -datasets

    OUTPUT:
    line plot with 5 the most improved teams
    """

    home_away_goals = append_home_away_goals(goals_home_vs_away)
    home_away_goals_avg = home_away_goals.groupby(['year', 'country_name', 'team'], as_index = False).mean()
    home_away_goals_avg.to_csv('./datasets/home_away_goals.csv')
#choose 5 teams which have improved the most since 2008 until 2016
    goals_ave_2008 = home_away_goals_avg.query('year == "2008"')
    goals_ave_2016 = home_away_goals_avg.query('year == "2016"')
    goals_ave_2008_1016 = goals_ave_2008.merge(goals_ave_2016, left_on='team', right_on='team', how='inner')
    goals_ave_2008_1016.rename(columns={'year_x': 'year', 'country_name_x' : 'country_name', 'total_goals_x' : 'total_goals_2008', 'total_goals_y' : 'total_goals_2016'}, inplace = True)
    goals_ave_2008_1016.drop(['year_y', 'country_name'], axis = 1, inplace=True )
    goals_ave_2008_1016['ratio'] =  goals_ave_2008_1016['total_goals_2016'] / goals_ave_2008_1016['total_goals_2008']
    goals_ave_2008_1016.sort_values(by='ratio', ascending=False, inplace=True)
    goals_ave_2008_1016.to_csv('./datasets/goals_ave_2008_2016.csv')
    year = goals_home_vs_away['year'].unique()
    five_teams_best = goals_ave_2008_1016.iloc[:5,[1, 5]] #team name and ratio
    five_teams_best.to_csv('./datasets/five_teams_best.csv')
    fig, ax = plt.subplots() #figsize=(25,15))
    leg = []
    for i in range(five_teams_best.shape[0]):
        team = home_away_goals_avg.query('team == "{}"'.format(five_teams_best.iloc[i,0]))
        team.sort_values(by='year')
        ax.plot(team.iloc[:,0].apply(pd.to_numeric), team.iloc[:,3])
        team.to_csv('./datasets/team.csv')
        leg.append(team.iloc[0,2]+", " + team.iloc[0, 1])
    plt.xlabel('year')
    plt.ylabel('average number of home and away goals ')
    plt.title('Best improved teams')
    plt.legend(leg)
    plt.savefig('./plots/improved_teams.png')
    fig.clf()


def ave_goals_home_vs_away(countries, goals_home_vs_away):
    """
    comparison of goals when teap plays at home vs aways

    INPUT:
    countries, goals_home_vs_away

    OUTPUT:
    bat charts for teams for each country
    """

    home_team_goal_avg = goals_home_vs_away[['country_name','home_team','home_team_goal']].groupby(['country_name','home_team'], as_index=False)['home_team_goal'].mean()
    away_team_goal_avg = goals_home_vs_away[['country_name','away_team','away_team_goal']].groupby(['country_name','away_team'], as_index=False)['away_team_goal'].mean()
    goals_home_away_avg = home_team_goal_avg.merge(away_team_goal_avg, left_on='home_team', right_on='away_team', how='inner')
    goals_home_away_avg.rename(columns={'country_name_x' : 'country_name', 'home_team' : 'team_name', 'home_team_goal' : 'goals_at_home', 'away_team_goal':'goals_away'}, inplace = True)
    goals_home_away_avg.drop(['away_team','country_name_y'], axis = 1, inplace=True)
    home_team_goal_avg.to_csv('./datasets/home_teams_avg.csv')
    away_team_goal_avg.to_csv('./datasets/away_teams_avg.csv')
    goals_home_away_avg.to_csv('./datasets/goals_home_aways_avg.csv')

    path = "./plots/"
    for country in countries.loc[:,'name']:

        avg_goals_country =  goals_home_away_avg[goals_home_away_avg['country_name'] == country]
        plt.subplots(figsize=(25,15))
        total = avg_goals_country['goals_at_home'].sum() + avg_goals_country['goals_away'].sum()
        avg_goals_country.loc[:,'goals_at_home'] = avg_goals_country.loc[:,'goals_at_home'] / total
        avg_goals_country.loc[:,'goals_away'] = avg_goals_country.loc[:,'goals_away'] / total
        ind = np.arange(avg_goals_country.shape[0]) # x location for teams (home and away goals)
        width = 0.35
        home_goals = plt.bar(ind, avg_goals_country['goals_at_home'], width, color = 'b', alpha=0.7, label='goals at home')
        away_goals = plt.bar(ind+width, avg_goals_country['goals_away'], width, color = 'y', alpha=0.7, label='goals away')
        locations = ind + width / 2
        plt.xticks(locations, avg_goals_country['team_name'], rotation=39, fontsize=12)
        plt.title("Comparisoin of average relative values of goals at home vs away by team in {}".format(country), fontsize=20)
        plt.xlabel('Team name')
        plt.legend(handles=[home_goals, away_goals])
        plt.savefig(path+"goals_home_away_"+country+".png")
