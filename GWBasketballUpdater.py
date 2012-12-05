import re
from pyquery import PyQuery as pq
import MySQLdb
import sys

class GWBBallUpdater:
    def __init__(self, element, class_id, desc, database, user, password):
        self.class_id = class_id
        self.desc = desc
        self.database = database
        self.user = user
        self.password = password
        self.debug = True
  
    def check_if_change(self, file_downloaded, file_before_save):
        #Bail, we have a problem
        if not isinstance(file_downloaded, str) or not isinstance(file_downloaded, str):
            return False
        #Looking at 2 files, the one we just downloaded, and the 
        #one that was previously saved. If the part we want to
        #save to the database has changed, then update the database
        #and make sure to save the new file
        if self.class_id == "id":
          elem_type = "#"
        else:
          elem_type = "."
        py_file_downloaded = pq(file_downloaded)
        py_file_before_save = pq(file_before_save)
        downloaded_check = py_file_downloaded(elem_type+self.desc)
        check_against = py_file_before_save(elem_type+self.desc)
        if downloaded_check == check_against and self.debug != True:
          return False
        else:
          self.update_bball_database(file_downloaded)
          return True

    def update_bball_database(self, info_to_parse):
        #conn = MySQLdb.connect(host="localhost", user=self.user, passwd=self.password, db=self.database)
        #cursor = conn.cursor()
        cursor = None
        #List of overall data
        #self.parse_bball_schedule_overall(info_to_parse, cursor)
        self.parse_game_schedule(info_to_parse, cursor)

    def parse_bball_schedule_overall(self, schedule_to_parse, mysql_handle):
        search_for_rows = pq(schedule_to_parse)
        schedule_rows = search_for_rows("#sched_records div")
        re.findall('(.+?)\s(\d+-\d+)', schedule_rows.text()) 

    #Nifty little thing. The list should end up looking something like
    #['date', 'opponent', 'place, 'w/l OR time of game']
    #It should also have sprinkled in the type of game being played
    #So it might have a single list item that just says ['18th Annual BB&T Classic']
    #What's even more convenient is that these tr's actually wrap around the games they
    #cover, so the list item after the games within the category of 18th annual BB&T classic
    #will be blank
    #So you can look for something like 
    #['game1']
    #['18th Annual BB&T Classic']
    #['game2']  
    #['game3']
    #['']
    #['game4']
    #game2 and game3 are in the BB&T classic, game 1 and game 4 are not
    def get_schedule_row(self, num, info):
        schedule_tr = pq(info)
        temp_list = []
        schedule_tr.find("td").each(lambda i, e: temp_list.append(pq(e).text()))
        self.list_of_scheduled_games.append(temp_list)
        
    #This fucntion takes a pyquery object, parses it further down
    #to find all tr attributes, which will be parsed further
    #down (via the each), to find all the single schedule elements
    def parse_game_schedule(self, schedule_to_parse, mysql_handle):
        self.list_of_scheduled_games = []
        search_for_schedule = pq(schedule_to_parse)
        game_schedule_rows = search_for_schedule("#schedtable").find('tr')
        game_schedule_rows.each(lambda i,e: self.get_schedule_row(i, pq(e)))
        #Remove first two entries (its the headers for the table)
        self.list_of_scheduled_games.pop(0)
        self.list_of_scheduled_games.pop(0)

        conference_regular = "Regular"
        finalized_schedule_list = []
        for single_schedule_item in self.list_of_scheduled_games:
            print len(single_schedule_item[0])
            if len(single_schedule_item) == 1 and len(single_schedule_item[0]) > 0:
                conference_regular = single_schedule_item[0]
            elif len(single_schedule_item) == 1 and len(single_schedule_item[0]) == 0:
                conference_regular = "Regular"
            else:
                single_schedule_item.append(conference_regular)
                finalized_schedule_list.append(single_schedule_item)
        
        
        #schedule_of_games = re.findall('(.+?)\r(.+?)\r(.+?)\r(.+?)\r', game_schedule_rows)
        #print schedule_of_games


