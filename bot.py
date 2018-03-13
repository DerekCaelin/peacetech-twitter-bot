from __future__ import print_function
from __future__ import with_statement
import contextlib
import tweepy
import re
import string
import nltk
nltk.download('punkt')
import sys
import requests
from bs4 import BeautifulSoup
import curses
from curses.ascii import isdigit

import sys
import certifi
import urllib
import urllib3
try:
    from urllib.parse import urlencode
except ImportError:
    from urllib import urlencode
try:
    from urllib.request import urlopen
except ImportError:
    from urllib2 import urlopen
import httplib2
import os
import gspread
from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage
from oauth2client.service_account import ServiceAccountCredentials
import time
from time import gmtime, strftime
import datetime
from datetime import datetime, date, timedelta
from apscheduler.schedulers.blocking import BlockingScheduler
from profanity import profanity 

import lxml

# Imports the Google Cloud client library
#from google.cloud import language
#from google.cloud.language import enums
#from google.cloud.language import types

# Instantiates a client
#glclient = language.LanguageServiceClient()

import json
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import math
import random
import numpy as np

#from aylienapiclient import textapi


try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

tokenizer = nltk.data.load('nltk:tokenizers/punkt/english.pickle')
from nltk.corpus import cmudict
d = cmudict.dict()

import urllib3.contrib.pyopenssl
urllib3.contrib.pyopenssl.inject_into_urllib3()

syllables = 0
countloop = 0

 #Google
headers = gspread.httpsession.HTTPSession(headers={'Connection': 'Keep-Alive'})
gscope = ['https://spreadsheets.google.com/feeds']
gsecret = ServiceAccountCredentials.from_json_keyfile_name('peacetechbot_secret.json', gscope)
gclient = gspread.Client(auth=gsecret, http_session=headers)
gclient.login()
    
#gapplication_name = 'Google Sheets API Python Quickstart'
sheet = gclient.open("PeaceTech People Grants Networks and News Data") #name of spreadsheet
nonengwords_gslist = sheet.worksheet('nonengwords') #name of worksheet
savedlinks_gslist = sheet.worksheet('savedlinks')
peacegrants_gslist = sheet.worksheet('peacegrants')
savedtweets_gslist = sheet.worksheet('savedtweets')
handles_gslist = sheet.worksheet('peacetechpeople')
authorizedtomention_gslist = sheet.worksheet('authorizedtomention')
elements_gs = sheet.worksheet('elements')
connections_gs = sheet.worksheet('connections')
misc_gs = sheet.worksheet('misc')
load_e_gs = sheet.worksheet('load_e')
load_c_gs = sheet.worksheet('load_c')
#peaceengineering_gs = sheet.workshot('peaceengineering')

#first twitter creds
from credentials import CONSUMER_KEY as CONSUMER_KEY
from credentials import CONSUMER_SECRET as CONSUMER_SECRET
from credentials import ACCESS_KEY as ACCESS_KEY
from credentials import ACCESS_SECRET as ACCESS_SECRET
auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_KEY, ACCESS_SECRET)
api = tweepy.API(auth)

scheduler = BlockingScheduler()
import logging
logging.basicConfig()

def GetCreds():

    
     #renew authorization
    global gclient
    gclient = gspread.Client(auth=gsecret, http_session=headers) #renew authorization
    gclient.login()
    global sheet
    sheet = gclient.open("PeaceTech People Grants Networks and News Data") #name of spreadsheet
    
    global nonengwords_gslist
    nonengwords_gslist = sheet.worksheet('nonengwords') #name of worksheet
    global savedlinks_gslist
    savedlinks_gslist = sheet.worksheet('savedlinks')
    global savedtweets_gslist
    savedtweets_gslist = sheet.worksheet('savedtweets')
    global handles_gslist
    handles_gslist = sheet.worksheet('peacetechpeople')
    global authorizedtomention_gslist
    authorizedtomention_gslist = sheet.worksheet('authorizedtomention')
    global elements_gs
    elements_gs = sheet.worksheet('elements')
    global connections_gs
    connections_gs = sheet.worksheet('connections')
    
    #Twitter
    from credentials import CONSUMER_KEY as CONSUMER_KEY
    from credentials import CONSUMER_SECRET as CONSUMER_SECRET
    from credentials import ACCESS_KEY as ACCESS_KEY
    from credentials import ACCESS_SECRET as ACCESS_SECRET
    auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
    auth.set_access_token(ACCESS_KEY, ACCESS_SECRET)
    global api
    api = tweepy.API(auth)
    
    http = urllib3.PoolManager(
    cert_reqs='CERT_REQUIRED',
    ca_certs=certifi.where())

def SearchForHaikuTweets(queryword): #seach for tweets
    print("searching for haiku tweets for "+queryword)
    for tweet in tweepy.Cursor(api.search,
                               q=queryword,
                               count=10,
                               result_type="recent",
                               tweet_mode='extended',
                               include_entities=True,
                               lang="en").items(10):
        global countloop
        countloop += 1                    
        #tweet.translate(None, '')
        #print(tweet)
        
        #get the user who made the tweet, add it to database
        user = api.get_user(tweet.author.screen_name)
        tweettext = tweet.full_text
        print (tweettext)
        if queryword == "peacetech":
            addpeopletodatabase(user,"tweeted about peacetech",tweet)
        
        #mentions
        if re.search(r'@', tweettext):
            tweettext = ''
            
        # Retweets
        if re.search(r'\bRT\b', tweettext):
           tweettext = ''
        
           
        #profanity
        if profanity.contains_profanity(tweettext):
            tweettext = ''
        
        #follow someone if they have tweeted about peacetech without retweeting or mentioning (in other words, posting themselves)
        #if tweettext != '' and api.exists_friendship != True :
        #    api.create_friendship(user)
        
        else:
            # Dropping special characters
            tweettext =  re.sub(re.compile('[^'+string.printable+']'), '', tweettext)
            
            # Dropping urls, hashtags and addressing
            tweettext = re.sub(r'\bhttps?://.*\b', '', tweettext)
            
            # strip amp
            tweettext = re.sub(r'\b &amp;\b', '', tweettext)
            
            #convert line breaks into spaces
            tweettext = tweettext.replace('\n', '')
            
            # Dropping hashtags and addressing
            tweettext = re.sub(r'#|@[^ ]?|\*', '', tweettext)
           
            # Dropping htmlentities
            tweettext = re.sub(r'&.+?;', '', tweettext)
            # Final Strip
            tweettext = tweettext.rstrip().strip()
           
           # tweettext = 'I am first with five then seven in the middle Five again to end'
        #print (tweettext)
        if tweettext != '':
            if is_haiku(tweettext):
                print("haiku detected!")
                print (tweet.user.screen_name)
                print("")
                print (lines)
                print ('')
                #if I haven't posted this before...
                if checksavedtweets(tweet.user.screen_name, lines, tweet.id, queryword) == False:
                    #post the haiku
                    postHaiku(tweet.user, lines, queryword)
            
#detect if post is a haiku
def is_haiku(text):

    import re
    text_orig = text
    text = text.lower()
    
    #split sentence into words
    words = nltk.wordpunct_tokenize(re.sub('[^a-zA-Z_ ]', '',text))
    syl_count = 0
    word_count = 0
    haiku_line_count = 0
    global lines
    lines = ""
    
    for word in words:
        #count syllables
        try:
            syl_count += nsyl(word)
        except:
            return False
        global syllables
        syllables = syl_count
        
        #insert a linebreak at 5 and 12 syllables
        if syl_count == 5 or syl_count == 12:
            lines += word + ' ~ \n'
        else:
            lines += word+" "

    if syl_count == 17 and lines.count('~') == 2:
        return True
    else:
        return False
        
def nsyl(word):
    try: 
        #use the nltk english library to look up syllables
        return [len(list(y for y in x if y[-1].isdigit())) for x in d[word.lower()]][0]
    except:
        #if the word doesn't exist in the nltk library, look up the custom list
        if word in nonengwords_gslist.col_values(1):
            row = nonengwords_gslist.col_values(1).index(word)+1
            col = 2
            return int(nonengwords_gslist.cell(row,col).value)
        else:
            stringThing= "I don't know a word: "+word
            
            #if the word isn't in the list, 
            if stringThing not in savedtweets_gslist.col_values(2):
            
                #ask (someone) to define the syllable count
                #return askWordLength(word, nonengwords_gslist.row_count)
                
                api.send_direct_message('derekpost',text=stringThing)
                savedtweets_gslist.append("PeaceTechBot",stringThing, strftime("%Y-%m-%d %H:%M:%S", gmtime()),"word syllable request","")

#function to extract metadata from tweets about peacetech
def FindLinksToTweet(queryword):
    print("finding tweets for "+queryword)
    for tweet in tweepy.Cursor(api.search,
                               q=queryword,
                               count=10,
                               result_type="recent",
                               tweet_mode='extended',
                               include_entities=True,
                               lang="en").items(20):
        urls = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', tweet.full_text)
        result = []
       # print(savedlinks_gslist.col_values(2))
        for url in urls:
            print(url)
            
            SaveTweet(tweet)
            
            #extract data
            ExtractLinkData(url, "Twitter",queryword)
            
def SaveTweet(tweet):
    user = api.get_user(tweet.author.screen_name)
    cuser_sn = "@"+user.screen_name
    tweetid = str(tweet.id)
    tweettext = tweet.full_text
    print("attempting to save and favorite tweet "+str(tweet.id)+" by "+cuser_sn)
    #Check Saved Tweets
    if tweetid in savedtweets_gslist.col_values(5) or cuser_sn == "@PeaceTechBot":
        print("Detected mention "+str(tweetid)+" is already in database or poster is @peacetechbot.")
        return True
    else:
        insert = [cuser_sn, tweettext, strftime("%Y-%m-%d %H:%M:%S", gmtime()), "peacetech tweet", tweetid]
        savedtweets_gslist.append_row(insert)
        FavoriteTweet(tweet)
        print("saved and favorited tweet!")
        return False
            
def FavoriteTweet(tweet):
 
    #like tweet
    api.create_favorite(tweet.id)
            
def ExtractLinkData(twitterurl, type, queryword):
    try:
        session = requests.Session()  # so connections are recycled
        resp = session.head(twitterurl, allow_redirects=True)
        print("resp.url = "+resp.url)
        #filter out links to other twitter posts or facebook posts, or websites that don't play ball with bots
        if 'twitter.com' not in resp.url and 'destyy.com' not in resp.url and 't.co' not in resp.url:
                   
            #insert headers to pretend not to be a bot
            headers = {'User-Agent':'Mozilla/5.0'}    
            page = requests.get(twitterurl, headers=headers)
            print("page")
            soup = BeautifulSoup(page.text, "html.parser")
            #print(soup)        
        
            if type == "Twitter":
                try:
                    title = soup.find("meta",  property="og:title")["content"]
                    print("title is: "+title)
                    #url = soup.find("meta",  property="og:url")["content"]
                    url = resp.url
                    print(url)
                    from urlparse import urlparse
                    parsed_uri = urlparse(url)
                    domain = '{uri.scheme}://{uri.netloc}/'.format(uri=parsed_uri)
                
                    print("is url NOT in database? "+ str(url not in savedlinks_gslist.col_values(2)))
                    #if the Url has already been saved
                    if url not in savedlinks_gslist.col_values(2):
                                    
                        #add it to the database
                        insert = [title, url, domain, strftime("%Y-%m-%d %H:%M:%S", gmtime()),"twitter","",queryword]
                        savedlinks_gslist.append_row(insert)
                        print("added link to list!")
                                    
                        #make a url tiny, because the twitter API doesn't automatically shorten
                        tiny_url = make_tiny(url)
                                    
                        status_update = str(title)+", "+str(tiny_url)+", #peacetech"
                        api.update_status(status_update)
                            
                   
                except:
                    try:
                        title = soup.find("meta",  property="og:title")["content"]
                        print("title is: "+title)
                        #url = soup.find("meta",  property="og:url")["content"]
                        url = resp.url
                        print(url)
                        from urlparse import urlparse
                        #parsed_uri = urlparse(url)
                        #domain = '{uri.scheme}://{uri.netloc}/'.format(uri=parsed_uri)
                    
                        print("is url NOT in database? "+ str(url not in savedlinks_gslist.col_values(2)))
                        #if the Url has already been saved
                        if url not in savedlinks_gslist.col_values(2):
                                        
                            #add it to the database
                            insert = [title, url, "", strftime("%Y-%m-%d %H:%M:%S", gmtime()),"twitter","",queryword]
                            savedlinks_gslist.append_row(insert)
                            print("added link to list!")
                                        
                            #make a url tiny, because the twitter API doesn't automatically shorten
                            tiny_url = make_tiny(url)
                                        
                            status_update = str(title)+", "+str(tiny_url)+", #peacetech"
                            api.update_status(status_update)
                        
                    except:
                        try:
                            title = soup.find("title").contents[0]
                            print("title is: "+title)
                            #url = soup.find("meta",  property="og:url")["content"]
                            url = twitterurl
                            print("twitter url = "+url)
                            #from urlparse import urlparse
                            #parsed_uri = urlparse(url)
                            #domain = '{uri.scheme}://{uri.netloc}/'.format(uri=parsed_uri)
                        
                            print("is url NOT in database? "+ str(url not in savedlinks_gslist.col_values(2)))
                            #if the Url has already been saved
                            if url not in savedlinks_gslist.col_values(2):
                                            
                                #add it to the database
                                insert = [title, url, "", strftime("%Y-%m-%d %H:%M:%S", gmtime()),"twitter","",queryword]
                                savedlinks_gslist.append_row(insert)
                                print("added link to list!")
                                            
                                #make a url tiny, because the twitter API doesn't automatically shorten
                                #tiny_url = make_tiny(url)
                                            
                                status_update = str(title)+", "+str(url)+", #peacetech"
                                api.update_status(status_update)
                        except:
                            
                            print("something went wrong getting data from tweet link")
            #share the link, but don't save it to the database
            if type == "Wiki":
                try:
                    #print(soup)
                    pagediv = soup.find_all("div", class_="catlinks")[0]
                    pageclass = soup.find('div', attrs={'class': 'mw-normal-catlinks'})
                    pagetype = str(pageclass.findAll('a')[1].contents[0])
                    print(pagetype)
                    
                    #Clean up the titles
                    title = str(soup.title)
                    title = re.sub('<title>', '', title)
                    title = re.sub("\ - PeaceTech Wiki</title>$", '', title)
                    print(title)
                    
                    url = str(soup.find(id="footer-places-mobileview"))
                    url = re.sub('<li id="footer-places-mobileview"><a class="noprint stopMobileRedirectToggle" href="', '', url)
                    url = re.sub('&amp;mobileaction=toggle_view_mobile">Mobile view</a></li>', '', url)
                    print(url)
                    
                    images = soup.findAll('img')
                    fileurl = str(images[0]["src"])
                    filename = str(images[0]["alt"])
                    print(filename)
                    if "http" in fileurl:
                        request = requests.get(fileurl, stream=True)
                        if request.status_code == 200:
                            with open(filename, 'wb') as image:
                                for chunk in request:
                                    image.write(chunk)
                                    #make a url tiny, because the twitter API doesn't automatically shorten
                                    tiny_url = make_tiny(url)
                                    
                                    status_update = "this should be filled in"
                                    
                                    if pagetype == "Tool":
                                        addtotweet = " "
                                        toolthing = soup.find_all("tr")[2]
                                        tooltd = toolthing.find("td")
                                        toolas = tooltd.findAll("a")
                                        #print(toolas)
                                        for toollink in toolas:
                                            tempthing = "#"+str(toollink.contents[0])+" "
                                            tempthing = re.sub(r'\ \b', '', tempthing).strip().strip(")")
                                            tempthing = tempthing.strip().strip("(")
                                            tempthing = tempthing.strip("Tool Class")
                                            addtotweet += tempthing+" "
                                        status_update = str(title), "A tool from the #PeaceTech Wiki! "+", "+tiny_url+","+addtotweet+"#peacetech"
                                    
                                    if pagetype == "Tool Class":
                                        addtotweet = " "
                                        status_update = "From the #PeaceTech Wiki: "+str(title)+", "+tiny_url+","+addtotweet+"#peacetech"
                                    
                                    if pagetype == "Project":
                                        addtotweet = " "
                                        status_update = "A project from the #PeaceTech Wiki: "+str(title)+", "+tiny_url+","+addtotweet+"#peacetech"
                                     
                                    if pagetype == "Peacebuilding Theme":
                                        addtotweet = " "
                                        status_update = "From the #PeaceTech Wiki: "+str(title)+", "+tiny_url+","+addtotweet+"#peacetech"
                                    
                                    if pagetype == "Objective":
                                        addtotweet = " "
                                        status_update = "#From the #PeaceTech Wiki: "+str(title)+", "+tiny_url+","+addtotweet+"#peacetech"
                                    
                            print(status_update)
                            api.update_with_media(filename, status = status_update)
                            os.remove(filename)
                        
                        else:
                            print("Unable to download image, trying again")
                            WikiPost()
                except:
                    WikiPost()
            
            if type == "grants":
                try:
                    #print(soup)
                    items = soup.find_all("item")
                    for item in items:
                        title = item.find("title").contents[0]
                        
                        description = item.find("content:encoded").contents[0]
                        #print(description)
                        searchterms = ["peace","peacebuilding","peacetech","CVE","violence","conflict-affected","violent extremism","radicalization",
                                    "hate speech", "hate crime", "dangerous speech", "social entrepreneurship", "bridgebuilding","coexistence"]
                        #notwantterms = ["domestic violence", "family violence", "dating violence"]
                        countries = ["Afghanistan","Albania","Algeria","Andorra","Angola","Anguilla","Antigua &amp; Barbuda","Argentina","Armenia","Aruba","Australia","Austria","Azerbaijan","Bahamas","Bahrain","Bangladesh","Barbados","Belarus","Belgium","Belize","Benin","Bermuda","Bhutan","Bolivia","Bosnia &amp; Herzegovina","Botswana","Brazil","British Virgin Islands","Brunei","Bulgaria","Burkina Faso","Burundi","Cambodia","Cameroon","Cape Verde","Cayman Islands","Chad","Chile","China","Colombia","Congo","Cook Islands","Costa Rica","Cote D Ivoire","Croatia","Cruise Ship","Cuba","Cyprus","Czech Republic","Denmark","Djibouti","Dominica","Dominican Republic","Ecuador","Egypt","El Salvador","Equatorial Guinea","Estonia","Ethiopia","Falkland Islands","Faroe Islands","Fiji","Finland","France","French Polynesia","French West Indies","Gabon","Gambia","Georgia","Germany","Ghana","Gibraltar","Greece","Greenland","Grenada","Guam","Guatemala","Guernsey","Guinea","Guinea Bissau","Guyana","Haiti","Honduras","Hong Kong","Hungary","Iceland","India","Indonesia","Iran","Iraq","Ireland","Isle of Man","Israel","Italy","Jamaica","Japan","Jersey","Jordan","Kazakhstan","Kenya","Kuwait","Kyrgyz Republic","Laos","Latvia","Lebanon","Lesotho","Liberia","Libya","Liechtenstein","Lithuania","Luxembourg","Macau","Macedonia","Madagascar","Malawi","Malaysia","Maldives","Mali","Malta","Mauritania","Mauritius","Mexico","Moldova","Monaco","Mongolia","Montenegro","Montserrat","Morocco","Mozambique","Namibia","Nepal","Netherlands","Netherlands Antilles","New Caledonia","New Zealand","Nicaragua","Niger","Nigeria","Norway","Oman","Pakistan","Palestine","Panama","Papua New Guinea","Paraguay","Peru","Philippines","Poland","Portugal","Puerto Rico","Qatar","Reunion","Romania","Russia","Rwanda","Saint Pierre &amp; Miquelon","Samoa","San Marino","Satellite","Saudi Arabia","Senegal","Serbia","Seychelles","Sierra Leone","Singapore","Slovakia","Slovenia","South Africa","South Korea","Spain","Sri Lanka","St Kitts &amp; Nevis","St Lucia","St Vincent","St. Lucia","Sudan","Suriname","Swaziland","Sweden","Switzerland","Syria","Taiwan","Tajikistan","Tanzania","Thailand","Timor L'Este","Togo","Tonga","Trinidad &amp; Tobago","Tunisia","Turkey","Turkmenistan","Turks &amp; Caicos","Uganda","Ukraine","United Arab Emirates","United Kingdom","Uruguay","Uzbekistan","Venezuela","Vietnam","Virgin Islands (US)","Yemen","Zambia","Zimbabwe"]
                        keywords = ""
                        keywordcount = 0
                        countryhash = ""
                        newgrant = False
                        for searchterm in searchterms:
                            if searchterm in description and keywordcount < 3:
                                keywordcount += 1
                                newgrant = True
                                searchterm = re.sub(r'\ \b', '', searchterm)
                                keywords += " #"+searchterm
                        if newgrant == True:
                            for country in countries:
                                if country in description:
                                    country = re.sub(r'\ \b', '',  country)
                                    countryhash += " #"+country
                            url = item.find("guid").contents[0]
                            if url not in savedlinks_gslist.col_values(2):
                                insert = ["Grant Opportunity: "+title,url,"",strftime("%Y-%m-%d %H:%M:%S", gmtime()),"grants.gov"]
                                
                                
                                tiny_url = make_tiny(url)
                                
                                status_update = "Peace Grant found: '"+title+"', "+tiny_url+" #grants"+keywords+countryhash
                                if len(status_update) > 140:
                                    trimchar = len(title) - (len(status_update)-138)
                                    title = (title[:trimchar] + '..')
                                    status_update = "Peace Grant found: '"+title+"', "+tiny_url+" #grants"+keywords+countryhash
                                
                                    #print(len(status_update))
                                if len(status_update) <= 140:    
                                    print(status_update)
                                    api.update_status(status_update) 
                                    savedlinks_gslist.append_row(insert)
                except:
                    print("something went wrong hunting grants")
                    
            else:
                print("ExtractUrl with a type")
                
       
    except:
        print("encountered error getting data from a url")

#get a human to define the word length
def askWordLength(newWord, row):
    
    try:
        #make a prompt
        newsylcount = int(input("I don't recognize '"+newWord+"'. How many syllables does it have?"))
        insert = [newWord,newsylcount]
        nonengwords_gslist.resize(row,2)
        nonengwords_gslist.append_row(insert)
        print("added words to list!")
    except:
         return False
    return newsylcount
            
#do a user search using the phrase peacetech            
def findpeacetechpeople():
    #for i in range (1,2):
    for user in tweepy.Cursor(api.search_users,
                               q="peacetech",
                               per_page=20,
                               #page=1
                               ).items(20):
   
        i = 0
        
        try:
            for tweet in api.user_timeline(user.id).items():
               # only look at the most recent peacetech tweet
                if 'peacetech' in tweet.full_text and i != 1:
                    i+=1
                    addpeopletodatabase(user,"peacetech user search",tweet.full_text)
        except:
            #extract a bunch of data about the user and their most recent peacetech tweet
            if user.screen_name not in handles_gslist.col_values(1):
                insert = [user.screen_name, user.name, user.description, user.location,"http://twitter.com/"+user.screen_name, "peacetech user search", strftime("%Y-%m-%d %H:%M:%S", gmtime()), "No recent peacetech tweet." ,"",user.followers_count]
                handles_gslist.append_row(insert)
                print("added people to list!")       
            
#post user and tweet data to the database
def addpeopletodatabase(user,source,tweet):

    if user.screen_name not in handles_gslist.col_values(1):
        insert = [user.screen_name, user.name, user.description, user.location,"http://twitter.com/"+user.screen_name, source, strftime("%Y-%m-%d %H:%M:%S", gmtime()), tweet.full_text,tweet.created_at,user.followers_count]
        handles_gslist.append_row(insert)
        print("added people to list!")
    #don't post any tweet that is older than the most recent peacetech tweet, but if you do, update variables  
    timething = handles_gslist.cell(handles_gslist.col_values(1).index(user.screen_name)+1,9).value
    if timething == "":
        timething = "2000-01-01 01:00:00"
    #print(timething)
    if tweet.created_at > datetime.strptime(timething, '%Y-%m-%d %H:%M:%S'):
        row = handles_gslist.col_values(1).index(user.screen_name)+1
        col = 8
        handles_gslist.update_cell(row, col, tweet.full_text)
        
        row = handles_gslist.col_values(1).index(user.screen_name)+1
        col = 9
        handles_gslist.update_cell(row, col, tweet.created_at)
        
        row = handles_gslist.col_values(1).index(user.screen_name)+1
        col = 10
        handles_gslist.update_cell(row, col, user.followers_count)
        
        print(user.screen_name+" updated in database")
        
def checkMentions():
    #look for mentions of the peacetech bot
    for tweet in tweepy.Cursor(api.search,
                               q="@peacetechbot",
                               tweet_mode='extended',
                               count=20,
                               #result_type="recent",
                               include_entities=True,
                               lang="en").items():
        
        tweettext = tweet.full_text
        tweetid = tweet.id
        
        #Haikus
        #if they've explicitly said that they do haiku 
        if re.search(r'i do haiku', tweettext.lower()):
            #and if we haven't already logged them as interested
            if checkauthorizedme(tweet.user.screen_name) == False:
                #and if this isn't a retweet of someone else
                if not re.search(r'RT', tweettext):
                    #log this person as OK to @mention in the future
                    authorizedtomention(tweet.user, tweettext, tweet.created_at)
                    
        #country check
        #if the tweet is about country check
        if re.search(r'@peacetechbot request conflict brief for', tweettext.lower()):
            print("someone made a country data request")
            if checksavedtweets(tweet.user.screen_name, tweettext, tweetid ,"countrycheck") == False:
                 #check if I've seen this tweek before
                #print("detected country data request: "+tweettext)
                text = tweettext.split(" ")
                global words
                words = []
                happy = False
                for i in text:
                    #print(i)
                    words.append(i.lower())
                    if i.lower() == "for":
                        #print (words)
                        happy = True
                        #print (happy)
                if happy == True:
                    countrytosearch = words[words.index('for')+1]
                    print("searching "+countrytosearch)
                    GetCountryData(countrytosearch, tweet.user.screen_name, tweetid)
                if happy == False:
                    print("couldn't figure out queryword for country search")

def checkFollowers():
    i = 0
    
def make_tiny(url):
    request_url = ('http://tinyurl.com/api-create.php?' + 
    urlencode({'url':url}))
    with contextlib.closing(urlopen(request_url)) as response:
        return response.read().decode('utf-8')    

def checksavedtweets(user, tweet, tweetid, queryword):
    
    if str(tweetid) in savedtweets_gslist.col_values(5):
        print("Detected mention "+str(tweetid)+" is already in database.")
        return True
    else:
        insert = [user, tweet, strftime("%Y-%m-%d %H:%M:%S", gmtime()), queryword, tweetid]
        savedtweets_gslist.append_row(insert)
        print("saved tweet!")
        return False

def postHaiku(user,tweet, queryword):
    print("running post haiku")
    additional = ""
    if strftime("%Y-%m-%d", gmtime()) == "2017-09-21" :
        additional = "#peaceday"
    if checkauthorizedme(user) == True:
        haikumaster = "@"+user.screen_name
        print("i'm authorized, appending that symbol")
    else:
        haikumaster = ""+user.name
    print("ready to assemble status")
    status_update = "Discovered #haiku by "+haikumaster+"!\n'"+tweet+"'\n#peacetech" +" "+additional
    print("status is: "+status_update)
    api.update_status(status_update)
    print("posted new haiku to twitter!")
    
def authorizedtomention(user,message,timething):
    insert = [user.screen_name, message, str(timething)]
    authorizedtomention_gslist.append_row(insert)
    print(user.screen_name+" authorized me to mention him/her!")

def checkauthorizedme(user):
    if user not in authorizedtomention_gslist.col_values(1):
        return False
    else:
        return True
        
def checkDMs():
    for message in api.direct_messages(count=10, page=1):
        text = message.text.split(" ")
        global words
        words = []
        for i in text:
            words.append(i.lower())
    
        #if the message is coming from me
        if message.sender.screen_name == "derekpost":
            #and the first word is train
            if words[0] == 'train':
                #and the second word is not in the database
                try:
                    if words[1] not in nonengwords_gslist.col_values(1):
                        #append 2nd word and value into database
                        insert = [words[1],words[2]]
                        nonengwords_gslist.append_row(insert)
                        api.send_direct_message(screen_name='derekpost',text="I've added "+words[1] +" to my database.")
                        print ("added to recognized word list: "+str(insert))
                except: 
                    i=0

def NetworkMap():
    print("mapping the peacetech network")
    queryword = "peacetech"
    #reset sheets
    connections_gs.clear()
    connections_gs.update_cell(1,1,"From")
    connections_gs.update_cell(1,2,"To")
    connections_gs.update_cell(1,3,"Tweet")
    connections_gs.update_cell(1,4,"Date")
    connections_gs.update_cell(1,5,"TweetID")
    connections_gs.update_cell(1,6,"")
    elements_gs.clear()
    elements_gs.update_cell(1,1,"Label")
    elements_gs.update_cell(1,2,"Name")
    elements_gs.update_cell(1,3,"Description")
    elements_gs.update_cell(1,4,"Location")
    elements_gs.update_cell(1,5,"Image")
    elements_gs.update_cell(1,6,"Most Recent #peacetech Tweet")
    elements_gs.update_cell(1,7,"# Tweets")
    
    usercounter = 2
    conncounter = 2

    for tweet in tweepy.Cursor(api.search,
                               q=queryword,
                               count=100,
                               result_type="recent",
                               tweet_mode='extended',
                               include_entities=True,
                               lang="en").items(100):
        
        #read text language

        #tweettext = api.get_status(tweet.id, tweet_mode='extended')._json['full_text']
        tweettext = tweet.full_text
        #scrub &amp
        tweettext = re.sub(r'\b &amp;\b', '', tweettext)
        tweetdate = tweet.created_at
        tweetid = tweet.id
        print(tweettext)

       
        #get element details   
        user_sn = "@"+tweet.author.screen_name
        user_n = tweet.author.name
        user_l = tweet.author.location
        user_d = tweet.author.description
        user_p = tweet.author.profile_image_url
            
        #insert user into elements list
        if user_sn not in elements_gs.col_values(1):
            #insert = [user_sn, user_n, user_d, user_l,user_p]
            #elements_gs.append_row(insert)
            elements_gs.update_cell(usercounter,1,user_sn)
            elements_gs.update_cell(usercounter,2,user_n)
            elements_gs.update_cell(usercounter,3,user_d)
            elements_gs.update_cell(usercounter,4,user_l)
            elements_gs.update_cell(usercounter,5,user_p)
            elements_gs.update_cell(usercounter,6,tweettext)
            elements_gs.update_cell(usercounter,7,1)
            usercounter += 1
        
        if user_sn in elements_gs.col_values(1):
            #val = elements_gs.
            print("")

        #if text includes a mention...
        if re.search(r'@', tweettext):
            
            #get element details   
            user_sn = "@"+tweet.author.screen_name
            user_n = tweet.author.name
            user_l = tweet.author.location
            user_d = tweet.author.description
            user_p = tweet.author.profile_image_url
            
            #insert user into elements list
            if user_sn not in elements_gs.col_values(1):
                insert = [user_sn, user_n, user_d, user_l,user_p]
                elements_gs.append_row(insert)
            
            #get connection details
            connections = re.findall(r'(?<=^|(?<=[^a-zA-Z0-9-\.]))@([A-Za-z]+[A-Za-z0-9]+)',tweettext,re.I)
            if re.search(r'RT ', tweettext) or re.search(r'Retweeted ',tweettext):
                cuser = connections[0]
                try: 
                        #extract information
                        
                        cfull_user = api.get_user(cuser.encode('utf-8','ignore'))
                        cuser_sn = "@"+cfull_user.screen_name
                        cuser_n = cfull_user.name
                        cuser_l = cfull_user.location
                        cuser_d = cfull_user.description
                        cuser_p = cfull_user.profile_image_url
                 
                        #add THESE people to elements
                        if cuser_sn not in elements_gs.col_values(1):
                            #insert = [cuser_sn, cuser_n, cuser_d, cuser_l,cuser_p]
                            #elements_gs.append_row(insert)
                            elements_gs.update_cell(usercounter,1,cuser_sn)
                            elements_gs.update_cell(usercounter,2,cuser_n)
                            elements_gs.update_cell(usercounter,3,cuser_d)
                            elements_gs.update_cell(usercounter,4,cuser_l)
                            elements_gs.update_cell(usercounter,5,cuser_p)
                            
                            usercounter += 1
                        
                        #record the connection
                        connections_gs.update_cell(conncounter,1,user_sn)
                        connections_gs.update_cell(conncounter,2,cuser_sn)
                        connections_gs.update_cell(conncounter,3,tweettext)
                        connections_gs.update_cell(conncounter,4,tweetdate)
                        connections_gs.update_cell(conncounter,5,tweetid)
                        conncounter += 1
                               
                            
                except:
                        print("something went wrong with the network retweet mapping")
                
            else:
                for cuser in connections:
                   
                    try: 
                        #extract information
                        
                        cfull_user = api.get_user(cuser.encode('utf-8','ignore'))
                        cuser_sn = "@"+cfull_user.screen_name
                        cuser_n = cfull_user.name
                        cuser_l = cfull_user.location
                        cuser_d = cfull_user.description
                        cuser_p = cfull_user.profile_image_url
                 
                        #add THESE people to elements
                        if cuser_sn not in elements_gs.col_values(1):
                            #insert = [cuser_sn, cuser_n, cuser_d, cuser_l,cuser_p]
                            #elements_gs.append_row(insert)
                            elements_gs.update_cell(usercounter,1,cuser_sn)
                            elements_gs.update_cell(usercounter,2,cuser_n)
                            elements_gs.update_cell(usercounter,3,cuser_d)
                            elements_gs.update_cell(usercounter,4,cuser_l)
                            elements_gs.update_cell(usercounter,5,cuser_p)
                            
                            usercounter += 1
                        
                        #record the connection
                        connections_gs.update_cell(conncounter,1,user_sn)
                        connections_gs.update_cell(conncounter,2,cuser_sn)
                        connections_gs.update_cell(conncounter,3,tweettext)
                        connections_gs.update_cell(conncounter,4,tweetdate)
                        connections_gs.update_cell(conncounter,5,tweetid)
                        conncounter += 1
                               
                            
                    except:
                        i=0
    try:
        status_update = "Today's network map of #peacetech on Twitter is out! goo.gl/ppuAi2"
        api.update_status(status_update)  
    except:
        print("error making a tinyurl of the network map")

def CheckGDELT(queryword):
    #access GDLT API with keyword
    gdurl = urlopen('http://api.gdeltproject.org/api/v2/doc/doc?query='+queryword+'&sortby=date&format=json').read()
    gdeltjson = json.loads(gdurl)
    try:
        for article in gdeltjson['articles']:
            #if I haven't seen the article before
            if article['url'] not in savedlinks_gslist.col_values(2):
                try:
                    gdomain = article['domain']
                    gurl = article['url']
                    gtitle = article['title']
                    gseentime = strftime("%Y-%m-%d %H:%M:%S", gmtime())
                    gtag = 'gdelt'
                    gsource = article['sourcecountry']
                    
                    #update Gsheets
                    insert = [gtitle, gurl, gdomain, gseentime, gtag, gsource,queryword]
                    savedlinks_gslist.append_row(insert)
                    
                    #make the url tiny
                    tiny_url = make_tiny(gurl)
                    
                    #share on twitter
                    print(gtitle)
                    print(tiny_url)
                    status_update = str(gtitle)+", "+str(tiny_url)+", #peacetech"
                    api.update_status(status_update)
                except:
                    print("couldn't share/append for some reason")
    except:
        print("keyerror articles?")
                
def WikiPost():
    print("getting wiki page")
    url = "http://peacetech.wiki/index.php?title=Special:Random"
    ExtractLinkData(url, "Wiki","none")
 
def CheckPCDNjobs():
    request = requests.get('https://pcdnetwork.org/?feed=job_feed&job_types=post-doc%2Cfull-time-job%2Cconsultancy%2Cpart-time-job%2Ctemporary%2Cinternship%2Cfellowship&search_location&job_categories&search_keywords')
    soup = BeautifulSoup(request.text,"html5lib")
    try:
        items = soup.find_all('item')
    except:
        items = soup.find_all('entry')
    
    for item in items:
        title = item.find('title').text
        url = item.link.next_sibling.strip()
        print (title + ' - ' + url)
        
        print("is url NOT in database? "+ str(url not in savedlinks_gslist.col_values(2)))
        #if the Url has already been saved
        if url not in savedlinks_gslist.col_values(2):
                                
            #add it to the database
            insert = [title, url, "pcdnetwork.org", strftime("%Y-%m-%d %H:%M:%S", gmtime()),"pcdn"]
            savedlinks_gslist.append_row(insert)
            print("added link to list!")
            
            try:            
                #make a url tiny, because the twitter API doesn't automatically shorten
                tiny_url = make_tiny(url)
                filename = 'pcdnlogo.jpg'            
                status_update = "Peace Job Alert: "+title+", "+str(tiny_url)+", #peacebuilding #jobs"
                api.update_with_media(filename, status=status_update)
            except:
                "could tweet a job for some reason"
  
def GrantsSearch(queryword):
    print("checking grants: "+queryword)
    
     #search for these keywords
    searchterms = ["peace","peacebuilding","peacetech","CVE","violence","conflict-affected","violent extremism","radicalization",
                    "hate speech", "hate crime", "dangerous speech", "social entrepreneurship", "bridgebuilding","coexistence","conflict","transparency and accountability"]
    highlightSearch = ["technology, data, media, innovation, innovation, ICT, 'early warning', 'early response'"]
    countries = ["Afghanistan","Albania","Algeria","Andorra","Angola","Anguilla","Antigua &amp; Barbuda","Argentina","Armenia","Aruba","Australia","Austria","Azerbaijan","Bahamas","Bahrain","Bangladesh","Barbados","Belarus","Belgium","Belize","Benin","Bermuda","Bhutan","Bolivia","Bosnia &amp; Herzegovina","Botswana","Brazil","British Virgin Islands","Brunei","Bulgaria","Burkina Faso","Burundi","Cambodia","Cameroon","Cape Verde","Cayman Islands","Chad","Chile","China","Colombia","Congo","Cook Islands","Costa Rica","Cote D Ivoire","Croatia","Cruise Ship","Cuba","Cyprus","Czech Republic","Denmark","Djibouti","Dominica","Dominican Republic","Ecuador","Egypt","El Salvador","Equatorial Guinea","Estonia","Ethiopia","Falkland Islands","Faroe Islands","Fiji","Finland","France","French Polynesia","French West Indies","Gabon","Gambia","Georgia","Germany","Ghana","Gibraltar","Greece","Greenland","Grenada","Guam","Guatemala","Guernsey","Guinea","Guinea Bissau","Guyana","Haiti","Honduras","Hong Kong","Hungary","Iceland","India","Indonesia","Iran","Iraq","Ireland","Isle of Man","Israel","Italy","Jamaica","Japan","Jersey","Jordan","Kazakhstan","Kenya","Kuwait","Kyrgyz Republic","Laos","Latvia","Lebanon","Lesotho","Liberia","Libya","Liechtenstein","Lithuania","Luxembourg","Macau","Macedonia","Madagascar","Malawi","Malaysia","Maldives","Mali","Malta","Mauritania","Mauritius","Mexico","Moldova","Monaco","Mongolia","Montenegro","Montserrat","Morocco","Mozambique","Namibia","Nepal","Netherlands","Netherlands Antilles","New Caledonia","New Zealand","Nicaragua","Niger","Nigeria","Norway","Oman","Pakistan","Palestine","Panama","Papua New Guinea","Paraguay","Peru","Philippines","Poland","Portugal","Puerto Rico","Qatar","Reunion","Romania","Russia","Rwanda","Saint Pierre &amp; Miquelon","Samoa","San Marino","Satellite","Saudi Arabia","Senegal","Serbia","Seychelles","Sierra Leone","Singapore","Slovakia","Slovenia","South Africa","South Korea","Spain","Sri Lanka","St Kitts &amp; Nevis","St Lucia","St Vincent","St. Lucia","Sudan","Suriname","Swaziland","Sweden","Switzerland","Syria","Taiwan","Tajikistan","Tanzania","Thailand","Timor L'Este","Togo","Tonga","Trinidad &amp; Tobago","Tunisia","Turkey","Turkmenistan","Turks &amp; Caicos","Uganda","Ukraine","United Arab Emirates","United Kingdom","Uruguay","Uzbekistan","Venezuela","Vietnam","Virgin Islands (US)","Yemen","Zambia","Zimbabwe"]
 
    #url lookup
    if queryword == "grants.gov":
        url = "https://www.grants.gov/rss/GG_NewOppByCategory.xml"
    if queryword == "fundsforngos.org":
        url = "https://www2.fundsforngos.org/category/peace-and-conflict-resolution/feed/"
    if queryword == "osf":
        url = "https://www.opensocietyfoundations.org/grants/rss"
    if queryword == "dfid":
        url = "https://www.gov.uk/government/publications.atom"
    if queryword == "difid":
        url = "https://www.gov.uk/international-development-funding.atom"
    if queryword == "undp":
        url = "http://procurement-notices.undp.org/rss_feeds/rss.xml"
    if queryword == "rwjf-o":
        url = "https://www.rwjf.org/rss/feed?cfp&title=RWJF%20-%20Open%20Calls%20For%20Proposals&desc=RWJF%20announces%20the%20following%20calls%20for%20proposals."

    #Load RSS page data
    headers = {'User-Agent':'Mozilla/5.0'}    
    page = requests.get(url)
    soup = BeautifulSoup(page.text, "html.parser")
    
    
    
    querywords = ["grants.gov","fundsforngos.org","osf","undp","rwjf-o"]
    #get rss/atom entries
    if queryword in querywords:
        items = soup.find_all('item') #most rss feeds use this format
    if queryword == "dfid" or queryword == "difid":
        items = soup.find_all('entry') #difd
        
    for item in items:
        
        if queryword == "osf":
            title = item.find("title").contents[0]
            granturl = item.link.next_sibling
            description = item.find("description").contents[0]
            description = description.replace(u"\u2018", "'").replace(u"\u2019", "'").replace(u"\u2013", " ")
            headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
            session = requests.Session()  # so connections are recycled
            resp = session.head(granturl, allow_redirects=True)
            page = requests.get(granturl, headers=headers)
            soup = BeautifulSoup(page.text, "html.parser")
            fulldescription = str(soup.find("div", attrs={'class': 'region-inner region-content-inner'})).lower()
        
        if queryword == "grants.gov":
            title = item.find("title").contents[0]
            granturl = item.find("guid").contents[0]
            description = item.find("content:encoded").contents[0]
            #description = description.replace(u"\u2018", "'").replace(u"\u2019", "'").replace(u"\u2013", " ")
            fulldescription = description
        
        if queryword == "fundsforngos.org":
            title = item.find("title").contents[0]
            granturl = item.find("link")
            description = item.find("description").contents[0]
            #description = description.replace(u"\u2018", "'").replace(u"\u2019", "'").replace(u"\u2013", " ")
            fulldescription = description
        
        if queryword == "dfid":
            title = item.find("title").contents[0]
            granturl = item.find("link")
            granturl = dict(granturl.attrs).get('href', '')
            granturl = str(granturl).replace('\n    ','').strip('\n').replace('\n','').strip()
            description = item.find("summary").contents[0]
            headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
            session = requests.Session()  # so connections are recycled
            resp = session.head(granturl, allow_redirects=True)
            page = requests.get(granturl, headers=headers)
            soup = BeautifulSoup(page.text, "html.parser")
            fulldescription = str(soup.find("body")).lower()
        
        if queryword == "difid":
            title = item.find("title").contents[0]
            granturl = item.find("link")
            granturl = dict(granturl.attrs).get('href', '')
            granturl = str(granturl).replace('\n    ','').strip('\n').replace('\n','').strip()
            description = item.find("summary").contents[0]
            headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
            session = requests.Session()  # so connections are recycled
            resp = session.head(granturl, allow_redirects=True)
            page = requests.get(granturl, headers=headers)
            soup = BeautifulSoup(page.text, "html.parser")
            fulldescription = str(soup.find("body")).lower()
            
        if queryword == "undp":
            title = item.find("title").contents[0]
            granturl = item.link.next_sibling
            granturl = str(granturl).replace('\n    ','').strip('\n').replace('\n','').strip()
            if '\n' in granturl:
                print("found n in granturl")
            description =item.find("dc:subject").contents[0]
            fulldescription = description.lower()

        if queryword == "rwjf-o":
            title = item.find("title").contents[0]
            granturl = item.link.next_sibling
            granturl = str(granturl).replace('\n    ','').strip('\n').replace('\n','').strip()
            print(granturl)
            #granturl = dict(granturl.attrs).get('href', '')
            description = item.find("description").contents[0]
            headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
            session = requests.Session()  # so connections are recycled
            resp = session.head(granturl, allow_redirects=True)
            page = requests.get(granturl, headers=headers)
            soup = BeautifulSoup(page.text, "html.parser")
            fulldescription = str(soup.find("body")).lower()
            
        
        keywords = ""
        keywordcount = 0
        countryhash = ""
        newgrant = False
        highlightGrant = False
        
        for searchterm in searchterms:
            if searchterm in fulldescription and keywordcount < 3:
                print(searchterm)
                keywordcount += 1
                newgrant = True
                searchterm = re.sub(r'\ \b', '', searchterm)
                keywords += " #"+searchterm
                
        for searchterm in highlightSearch:
            if searchterm in fulldescription:
                highlightGrant = True
            
        if newgrant == True:
            for country in countries:
                if country in fulldescription:
                    country = re.sub(r'\ \b', '',  country)
                    countryhash += " #"+country
                    
            comparelist = []
            for compareurl in peacegrants_gslist.col_values(2):
                comparelist.append(str(compareurl.strip('\n')))
                    
            if granturl not in comparelist:

                #truncate stuff from longwinded, messy websites
                if queryword == "grants.gov":
                    description = ""
                
                if highlightGrant == False:
                    print("grant:"+title+ ", has some keywords, adding")
                    insert = [title, granturl, description, strftime("%Y-%m-%d %H:%M:%S", gmtime()), countryhash.replace("#",""), keywords.replace("#",""), queryword,""]
                if highlightGrant != False:
                    print("grant "+title+ ", has highlight keywords! flagging..")
                    insert = [title, granturl, description, strftime("%Y-%m-%d %H:%M:%S", gmtime()), countryhash.replace("#",""), keywords.replace("#",""),queryword,"True"]

                tiny_url = make_tiny(granturl)
                try:
                    status_update = "Peace Grant found: '"+title+"', "+tiny_url+" #grants"+keywords+countryhash
               
                    if len(status_update) > 140:
                        trimchar = len(title) - (len(status_update)-138)
                        title = (title[:trimchar] + '..')
                        status_update = "Peace Grant found: '"+title+"', "+tiny_url+" #grants"+keywords+countryhash
                    
                        #print(len(status_update))
                    if len(status_update) <= 140:    
                        print(status_update)
                        api.update_status(status_update)
                except:
                    print ("couldn't post tweet for some reason")
                
                try:    
                    peacegrants_gslist.append_row(insert)
                except:
                    print("couldn't insert grant into gsheets. probably unicode error but who knows")
                    
def VisualizeACLED(queryword, replytweet):
    print("Checking ACLED")
    try:
        #get ACLED data
        url = "https://api.acleddata.com/acled/read.csv"
        response = requests.get(url)
        data = pd.read_csv(url)
        countrycol = data.loc[:,"country"]
        dates = data.loc[:,"event_date"]
        
        #select country
        countries = list(set(countrycol))
        if queryword == "random":
            country = random.choice(countries)
        else:
            country = queryword.title()
        
        #get data from country
        countrydatafull = data[data['country']==country]
        total_events = len(countrydatafull)
        
        #contingencies
        if replytweet == False and total_events == 0:
            VisualizeACLED(queryword, replytweet)
        if replytweet == True and total_events == 0:
            print ("no acled data for "+queryword)
        else:
            #get dates
            cdates = sorted(list(set(countrydatafull.loc[:,"event_date"])))
            dates_list = [datetime.strptime(date, '%Y-%m-%d').date() for date in cdates]
            first_date = dates_list[0]
            last_date = dates_list[len(dates_list)-1]
            final_dates = []
            
            #if acledupdated recently
            timesinceupdate = datetime.strptime(datetime.now().strftime("%Y-%m-%d"), '%Y-%m-%d').date() - last_date
            print(timesinceupdate.days)
            
            if (timesinceupdate.days <= 3 and replytweet == False) or replytweet == True: 
                
                delta = last_date-first_date
                for i in range(delta.days + 1):
                    final_dates.append(first_date + timedelta(days=i))
                
                eventcount = []
                
                #get events per date
                for date in cdates:
                    thing = list(countrydatafull.loc[:,"event_date"]).count(date)
                    eventcount.append(thing)
                
                #get event types
                ceventtypes = sorted(list(set(countrydatafull.loc[:,"event_type"])))
                print(ceventtypes)
                
                datelists = []
                graphcount = 0
                colors = ["#223451","#4b6896","#394559","#10397c","#04193d","#839cc6","#393c42","#000000"]
                
                #pre format chart
                fig, ax = plt.subplots()
                plt.title("Recent ACLED Events: "+country)
            
                
                #getdata
                for ceventtype in ceventtypes:
                        
                    #get date of eventtype
                    selcountrydatafull = countrydatafull[countrydatafull['event_type']==ceventtype]
                    datetocheckstr  = list(selcountrydatafull.loc[:,"event_date"])
                    datetocheckdt = [datetime.strptime(date, '%Y-%m-%d').date() for date in datetocheckstr]
                    
                    #get events per date
                    ceventcounts = []
                    for date in final_dates:
                        thing = datetocheckdt .count(date)
                        ceventcounts.append(thing)
                        
                    #make a list of dates
                    datelists.append(ceventcounts)
            
                
                #Visualize   
                sumdatelist = []
                graphs = []
                for date in datelists[0]:
                    sumdatelist.append(0) 
                for datelist in datelists:
                    graph = plt.bar(final_dates, datelist,color = colors[graphcount], bottom = sumdatelist )
                    graphs.append(graph)
                    sumdatelist = np.add(datelist, sumdatelist)
                    graphcount += 1
                
                #post viz formatting
                ax.format_xdata = mdates.DateFormatter('%Y-%m-%d')
                ax.set_ylim(ymin=0)
                ax.set_xlabel('Date')
                ax.set_ylabel('Events')
                plt.gcf().subplots_adjust(bottom=0.15)
                plt.xticks(rotation=15)
                plt.legend((graphs),(ceventtypes), fancybox=True, framealpha=0.5)
                #ax.legend(loc='best', fancybox=True, framealpha=0.5)
                plt.savefig("chart.png")
                
                #create status and share    
                if(first_date != last_date):
                    status = "Between " + str(first_date) + " and " + str(last_date) + ", there were " + str(total_events) + " protests or violent events in " + country + ". #ACLED #conflict #peacetech"
                if(first_date == last_date):
                    if total_events == 1:
                        status = "On " + str(first_date) + ", there was a protest or violent event in " + country + ". #ACLED #conflict #peacetech"
                    if total_events > 1:
                        status = "On " + str(first_date) + ", there were " + str(total_events) + " protests or violent events in " + country + ". #ACLED #conflict #peacetech"
                print(status)
                if replytweet == True:
                    tweetid = GetMyMostRecentTweet()
                    print(status)
                    api.update_with_media("chart.png",status = status, in_reply_to_status_id = tweetid)
                    os.remove("chart.png")
                else:
                    print(status)
                    api.update_with_media("chart.png",status = status)
                    os.remove("chart.png")
    except:
        print("error doing acled")

def GDELTconflict(queryword, articleGoal):
    queryword = str(queryword)
    print("getting GDELT data for "+queryword)
    print(queryword)
    gdurl = urlopen("https://api.gdeltproject.org/api/v2/doc/doc?query="+queryword+"%20sourcelang:english%20tone%3C-10%20theme:WB_2432_FRAGILITY_CONFLICT_AND_VIOLENCE%22%20&mode=artlist&maxrecords=100&timespan=1week&sort=datedesc&format=json").read()
    gdeltjson = json.loads(gdurl)
    usedAP = False
    titlesSoFar = []
    articleCount = 0
    #print(gdeltjson)
    try:
        for article in gdeltjson['articles']:
                try:
                    if articleCount == articleGoal:
                        break
                    gdomain = article['domain']
                    gurl = article['url']
                    headers = {'User-Agent':'Mozilla/5.0'}   
                    try:
                        page = requests.get(gurl, headers=headers)
                    except:
                        print("skipped.ArithmeticError  ")
                    soup = BeautifulSoup(page.text, "html.parser")
                    gtitle = article['title']
                    gseentime = strftime("%Y-%m-%d %H:%M:%S", gmtime())
                    gtag = 'gdelt conflict'
                    gsource = article['sourcecountry']
                    
                    #update Gsheets
                    insert = [gtitle, gurl, gdomain, gseentime, gtag, gsource,queryword]
                    
                    #make the url tiny
                    tiny_url = make_tiny(gurl)
                    status_update=""
                    
                    #share on twitter
                    try:
                        if str(soup).count(queryword) > 2 and gtitle not in titlesSoFar:
                            if "AP" in str(soup) or "Associated Press" in str(soup) and usedAP == False:
                                usedAP = True
                                articleCount += 1
                                titlesSoFar.append(gtitle)
                                try:
                                    status_update = gtitle+", "+str(tiny_url)+" #"+queryword
                                except:
                                    print ("couldn't make status")
                            if usedAP == True and ("AP" not in str(soup) and "Associated Press" not in str(soup)): 
                                articleCount += 1
                                titlesSoFar.append
                                try:
                                    status_update = gtitle+", "+str(tiny_url)+" #"+queryword
                                except:
                                    print ("couldn't make status")
                            try:
                                print (status_update)
                                tweetid = GetMyMostRecentTweet()
                                api.update_status(status_update, in_reply_to_status_id = tweetid)
                            except:
                                print("couldn't post status to twitter.")
                    except:
                        print("couldn't post an article")
                
                except:
                    print("couldn't share/append for some reason")
    except:
        print("keyerror articles?")

def GetCountryData(queryword, user, tweetid):
    print("getting country data on "+queryword+" as requested")
    status_update = "@"+str(user)+" "+str(user)+" requested a conflict update on "+queryword.title()+"! Follow this thread for conflict data & news update."
    api.update_status(status_update,in_reply_to_status_id = tweetid)
    
    #give acled data
    VisualizeACLED(queryword, True)
    
    #get GDELT Followup
    tweetid = GetMyMostRecentTweet()
    status_update = "Also checking conflict relevant #GDELT articles for "+queryword.title()
    api.update_status(status_update,in_reply_to_status_id = tweetid)
    GDELTconflict(queryword,3)

def GetMyMostRecentTweet():
    stuff = api.user_timeline(count=1)
    tweetid = stuff[0].id
    #print(tweetid)
    return tweetid

    
print("starting now.")


def thegreatloop():
    print("the loop begins")
    GetCreds()
    checkDMs()
    checkMentions()
    #SearchForHaikuTweets("peacetech")
    #SearchForHaikuTweets("peacemedia")
    #SearchForHaikuTweets("peaceapp")
    CheckGDELT("peacetech")
    CheckGDELT("peaceapp")
    CheckGDELT("peacemedia")
    CheckGDELT("peacegeeks")
    CheckGDELT("peacehack")
    FindLinksToTweet("peaceapp")
    FindLinksToTweet("peacetech")
    FindLinksToTweet("peacetechlab")
    FindLinksToTweet("peacemedia")
    FindLinksToTweet("peacegeeks")
    FindLinksToTweet("peacehack")
    
    findpeacetechpeople()
    CheckPCDNjobs()
    GrantsSearch("grants.gov")
    GrantsSearch("fundsforngos.org")
    GrantsSearch("osf")
    GrantsSearch("dfid")
    GrantsSearch("difid")
    GrantsSearch("undp")
    GrantsSearch("rwjf-o")




def periodic():
    WikiPost()
    VisualizeACLED("random", False)

def daily():
    NetworkMap()
    
def NormalOperations():
    thegreatloop()
    NetworkMap() 
    scheduler.add_job(thegreatloop, 'interval', minutes=5)
    scheduler.add_job(periodic,'interval', minutes=240)
    scheduler.add_job(daily,'interval',minutes=1440)
    scheduler.start()

NormalOperations()
#GrantsSearch("undp")
#VisualizeACLED("random", False)