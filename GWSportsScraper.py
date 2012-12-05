import urllib2
import os
from GWBasketballUpdater import GWBBallUpdater
from pyquery import PyQuery as pq

class GWSportsScraper:
    def __init__(self, type_of_sport, updater = None):
        self.url = 'http://www.gwsports.com'
        self.directory = 'pages'
        self.updater = updater
        
    #Function to get the contents of any page 
    def set_page_external(self, page_uri, folder = "standard", get_or_set = False, return_data = True):
        last_slash_pos = page_uri.rfind('/')
        last_slash_pos = last_slash_pos + 1
        page_name = page_uri[last_slash_pos:]
        page_html = urllib2.urlopen(self.url + page_uri).read()
        print "Read page"
        page_data = self.store_or_get_page(folder, page_name, page_html, get_or_set, return_data)
        if return_data:
            return page_data

    def get_page_external(self, page_uri, folder = "standard"):
        last_slash_pos = page_uri.rfind('/')
        last_slash_pos = last_slash_pos + 1
        page_name = page_uri[last_slash_pos:]
        page_html = urllib2.urlopen(self.url + page_uri).read()
        return page_html 

    def get_schedule_pages(self, retrieve_pages = True):
        if self.page_exists(self.directory+'/main/main-page.html') is not True:
            page_html = urllib2.urlopen(self.url).read()
            self.store_page('main', 'main-page', page_html, False)
        else:
            page_html = self.store_page("main", "main-page", "", False)
        
        find_schedule = pq(page_html)
        schedule_list = find_schedule('#nav-02')
        schedule_list.find("li").find("a").each(lambda i,e: self.get_schedule_page(e, retrieve_pages))

    def get_schedule_page(self, page_data, retrieve_page):
        if retrieve_page:
            link_to_schedule = pq(page_data).attr.href
            if not "http" in link_to_schedule:
                last_slash_pos = link_to_schedule.rfind('/')
                last_slash_pos = last_slash_pos + 1
                page_html = urllib2.urlopen(self.url + link_to_schedule).read()
                self.store_page('standard', link_to_schedule[last_slash_pos:], page_html, True) 


    def get_page(self, folder, page_name):
        file_path = self.directory + '/' + folder + '/' + page_name
        if not os.path.exists(file_path):
            #Doesn't exist, so bail
            return False
        else:
            file_to_get = open(file_path, 'r')
            return file_to_get.read()

    #Used in conjuction with get_page to only have to call the page once
    #If the page url exists as a locally stored page, don't bother grabbing
    #the page from online (cuts down on need to access the online page)
    def store_page(self, folder, page_name, page_data, return_data):
        file_path = self.directory + '/' + folder + '/' + page_name
        dir_path = self.directory+'/'+ folder
    
        if(not os.path.exists(dir_path)):
            os.makedirs(dir_path)
        #Either create the directory and file or return it
        if(not os.path.exists(file_path)):
            f = open(file_path, 'w+')
            f.write(page_data)
            f.close()
            if return_data:
                return page_data
        else:
            if self.updater != None:
                f = open(file_path, "r")
                data = f.read()
                if self.updater.check_if_change(data, page_data) != False:
                    f = open(file_path, 'w+')
                    f.write(page_data)
                    f.close()
                    if return_data:
                        return page_data
            else:
                f = open(file_oath, 'w+')
                f.write(page_data)
                f.close()
                if return_data:
                    return page_data

    def page_exists(self, page_pwd):
        if os.path.exists(page_pwd) is not True:
            return False
        else:
            return True
                        

bball_updater = GWBBallUpdater('div', 'class', 'schedborder', "gwh_bball", "cojen", "kingbobthe")
scraper = GWSportsScraper('basketball', bball_updater)
#scraper.get_schedule_pages()
#We always want to set the page so we can check if it's been updated
#For the moment, use list_of_schedule_files[9] (it's mens bball)
list_of_schedule_files = os.listdir('pages/standard')
page_data = scraper.get_page('standard', list_of_schedule_files[9])
bball_updater.check_if_change(page_data, page_data)
