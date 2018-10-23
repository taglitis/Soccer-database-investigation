import pandas as pd
import sqlite3
import matplotlib.pyplot as plt
import numpy as np


def db_work(goals_home_vs_away):
    path = "./input/"
    database = path + "database_soccer.sqlite"
    conn = sqlite3.connect(database)

# extract list of countries
    countries = pd.read_sql("""SELECT *
                               FROM Country;""", conn)
    countries.drop(['id'], axis = 1, inplace = True)
    print('List of countries', countries, "\n")

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
#    print(goals_home_vs_away)
    return countries, goals_home_vs_away




def db_team_attributes():
    path = "./input/"
    database = path + "database_soccer.sqlite"
    conn = sqlite3.connect(database)


    team_attributes = pd.read_sql(""" SELECT STRFTIME('%Y', date) AS year,
                                                date AS full_date,
                                                team_api_id AS id,
                                                buildupplayspeed AS play_speed,
    											buildupplaydribbling AS play_gribbing,
    											buildupplaypassing AS play_passing,
    											chancecreationpassing AS chance_passing,
    											chancecreationcrossing AS chance_crossing,
    											chancecreationshooting AS chance_shooting,
    											defencepressure AS defence_pressure,
    											defenceaggression AS defence_affression,
    											defenceteamwidth AS defence_width
                                        FROM Team_Attributes """, conn)
    team_attributes.dropna(inplace = True)
    team_attributes.to_csv('./datasets/team_attributes.csv')

    return team_attributes

def append_home_away_goals(goals_home_vs_away):
    home_goals = goals_home_vs_away[['year', 'country_name','home_team','home_team_goal', 'home_id']]
    away_goals = goals_home_vs_away[['year', 'country_name','away_team','away_team_goal', 'away_id']]
    home_goals.rename(columns={'home_team' : 'team', 'home_team_goal' : 'total_goals', 'home_id' : 'id'}, inplace = True)
    away_goals.rename(columns={'away_team' : 'team', 'away_team_goal' : 'total_goals', 'away_id' : 'id'}, inplace = True)
#Before appending check shape
    print("shape for home_away_goals: \n", home_goals.shape, " and away_goals: \n", away_goals.shape)
    home_away_goals = home_goals.append(away_goals, ignore_index = True)
    return home_away_goals

def goals_ave_compare(goals_home_vs_away):
    years = ['2008', '2016']
    bins_v = 20
    bin_names = []
    home_away_goals = append_home_away_goals(goals_home_vs_away)
    home_away_goals.to_csv('./datasets/home_away_goals_1.csv')
    #print('home_away_goals: ', home_away_goals)
    i = 0
    for year in years:
        print('year: ', year)
        home_away_goals_year = home_away_goals.query('year == "{}"'.format(year))
        if i == 0:
            min = home_away_goals_year.groupby('team', as_index = False).mean().total_goals.min()
            max = home_away_goals_year.groupby('team', as_index = False).mean().total_goals.max()
            print('min: ', min, 'max: ', max)
        else:
            min_new = home_away_goals_year.groupby('team', as_index = False).mean().total_goals.min()
            max_new = home_away_goals_year.groupby('team', as_index = False).mean().total_goals.max()
            if min_new < min: min = min_new
            if max_new > max: max = max_new
            print('min_new: ', min_new, 'max_new: ', max_new)

        i += 1
    print('min: ', min, 'max: ', max)
    bin_edges = np.linspace(min-.00001, max+0.00001, bins_v)
    delta = (bin_edges[1] - bin_edges[0]) / 2
    locations = []
    ind = []
    width = delta/2
    for i in range(bins_v-1):
        locations.append(bin_edges[i] + delta)
        #ind.append(bin_edges[i] + delta )
    print('bin_edges', bin_edges, '\n  bin_edges len', len(bin_edges), '\n \n locations ', locations, '\n locations len', len(locations),  '\n delta: ', delta)
    print('\n \n ind \n', ind)
    fig, ax = plt.subplots(figsize=(8,6))
    for year in years:
        home_away_goals_local_ave = home_away_goals.query('year == "{}"'.format(year)).groupby('team').mean()
#    home_away_goals_2008_ave = home_away_goals_2008.groupby('team').mean()
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
        print('i= ', i, 'locations[i]', locations[i])
        locations[i] = locations[i] - 2*width
        label_v.append(format(locations[i], '.2f'))
        locations[i] = locations[i] + width / 2
    print("locations: ", locations, "label_v", label_v)
    plt.title('Comparison of probability distributions of goals mean values for {} and {}'.format(years[0], years[1]))
    plt.xticks(locations, label_v)
    plt.xlabel('average number of goals')
    plt.legend()
    plt.savefig('./plots/goals_ave_compare.png')

def improved_teams(goals_home_vs_away, countries):
    home_away_goals = append_home_away_goals(goals_home_vs_away)
    print("shape for home_away_goals after appending:", home_away_goals.shape)
    home_away_goals_avg = home_away_goals.groupby(['year', 'country_name', 'team'], as_index = False).mean()
    home_away_goals_avg.to_csv('./datasets/home_away_goals.csv')
#choose 5 teams which have improved the most since 2008 until 2016
    goals_ave_2008 = home_away_goals_avg.query('year == "2008"')
    goals_ave_2016 = home_away_goals_avg.query('year == "2016"')
    print('goals_ave_2008: ', goals_ave_2008.shape, 'goals_ave_2016: ', goals_ave_2016.shape)
    goals_ave_2008_1016 = goals_ave_2008.merge(goals_ave_2016, left_on='team', right_on='team', how='inner')
    goals_ave_2008_1016.rename(columns={'year_x': 'year', 'country_name_x' : 'country_name', 'total_goals_x' : 'total_goals_2008', 'total_goals_y' : 'total_goals_2016'}, inplace = True)
    print('goals_ave_2008_2016 shape : ', goals_ave_2008_1016.shape)
    print('goals_ave_2008_2016 columns : ', goals_ave_2008_1016.columns)
    goals_ave_2008_1016.drop(['year_y', 'country_name'], axis = 1, inplace=True )
    print('goals_ave_2008_2016 columns : ', goals_ave_2008_1016.columns)
    goals_ave_2008_1016['ratio'] =  goals_ave_2008_1016['total_goals_2016'] / goals_ave_2008_1016['total_goals_2008']
    goals_ave_2008_1016.sort_values(by='ratio', ascending=False, inplace=True)
    print('goals_ave_2008_2016 columns : ', goals_ave_2008_1016.columns)
    goals_ave_2008_1016.to_csv('./datasets/goals_ave_2008_2016.csv')
    year = goals_home_vs_away['year'].unique()
    five_teams_best = goals_ave_2008_1016.iloc[:5,[1, 5]] #team name and ratio
    print('five_teams_best ration: ', five_teams_best.columns)
    print('year: ', year)
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



def ave_goals_home_vs_away(goals_home_vs_away, countries):
#solving encoding problem: UnicodeEncodeError: 'charmap' codec can't encode character '\xf6' in position 56: character maps to <undefined>
    home_team_goal_avg = goals_home_vs_away[['year', 'country_name','home_team','home_team_goal']].groupby(['year', 'country_name','home_team'], as_index=False)['home_team_goal'].mean()
    away_team_goal_avg = goals_home_vs_away[['year','country_name','away_team','away_team_goal']].groupby(['year','country_name','away_team'], as_index=False)['away_team_goal'].mean()
    goals_home_away_avg = home_team_goal_avg.merge(away_team_goal_avg, left_on='home_team', right_on='away_team', how='inner')
    goals_home_away_avg.rename(columns={'country_name_x' : 'country_name', 'home_team' : 'team_name', 'home_team_goal' : 'goals_at_home', 'away_team_goal':'goals_away'}, inplace = True)
    goals_home_away_avg.drop(['away_team','country_name_y'], axis = 1, inplace=True)
    home_team_goal_avg.to_csv('./datasets/home_teams_avg.csv')
    away_team_goal_avg.to_csv('./datasets/away_teams_avg.csv')
    goals_home_away_avg.to_csv('./datasets/goals_home_aways_avg.csv')
    print(home_team_goal_avg.head())
    print('******* \n', goals_home_vs_away.head())

    path = "./plots/"
    for country in countries.loc[:,'name']:
        print(country)

        avg_goals_country =  goals_home_away_avg[goals_home_away_avg['country_name'] == country]
        plt.subplots(figsize=(25,15))
        total = avg_goals_country['goals_at_home'].sum() + avg_goals_country['goals_away'].sum()
        avg_goals_country.loc[:,'goals_at_home'] = avg_goals_country.loc[:,'goals_at_home'] / total
        avg_goals_country.loc[:,'goals_away'] = avg_goals_country.loc[:,'goals_away'] / total
#        print(avg_goals_country)
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
