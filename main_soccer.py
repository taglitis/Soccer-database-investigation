#import numpy as np
#import pandas as pd



import function_soccer as fc


#def db_work():
#    path = "./input/"
#    database = path + "database_soccer.sqlite"
#    conn = sqlite3.connect(database)

#    countries = pd.read_sql("""SELECT *
#                               FROM Country;""", conn)

#    print(countries)



def main():
    countries, goals_home_vs_away = fc.db_work() #obtain data sets from DB
    fc.team_attributes_compare(goals_home_vs_away)
    fc.improved_teams(goals_home_vs_away)
    fc.goals_ave_compare(goals_home_vs_away)
    fc.ave_goals_home_vs_away(countries, goals_home_vs_away)


if __name__ == "__main__":
    main()
