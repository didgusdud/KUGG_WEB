# -*- coding: utf-8 -*-
"""
Created on Mon Aug 31 02:32:24 2020

@author: 양현영
"""
import requests
import time
import json
import pandas as pd
import numpy as np
import time
import logging
from datetime import datetime

logging.basicConfig(filename="./"+datetime.today().strftime("%Y-%m-%d")+".log", level=logging.INFO)

class MatchTimelineReceiver:
    def __init__(self, api_key, csv_name):
        self.API_KEY = api_key
        self.csv_name = csv_name
        
    def set_dbcontroller(self, db_controller):
        self.db_controller_ = db_controller
        
    def update_db(self, matchTimeline_df):
        self.db_controller_.update_matchTimeline(matchTimeline_df)
    
    def make_matchTimeline_df(self, r_get_timeline, gameId):
        r_get_timeline_json = r_get_timeline.json()
        usersTimeline_df = pd.DataFrame([r_get_timeline_json])
        usersTimeline_df["gameId"] = int(gameId)
        
        return usersTimeline_df
                        
    def request_matchTimeline(self, unique_gameId):
        loop = 0
        flag = False
        total_length = len(unique_gameId)
        
        while True:
            get_matchTimeline = "https://kr.api.riotgames.com/lol/match/v4/timelines/by-match/"+ \
                str(unique_gameId[loop]) +"?api_key="+self.API_KEY
            r_get_matchTimeline = requests.get(get_matchTimeline)
            
            if r_get_matchTimeline.status_code == 429:
                logging.warning(str(unique_gameId[loop])+" time exceed")
                time.sleep(30)
                continue
            elif r_get_matchTimeline.status_code != 200:
                logging.error("status code = "+str(r_get_matchTimeline.status_code))
                time.sleep(10)
                continue
            
            if not flag:
                flag = True
                users_matchTimeline_df_after = self.make_matchTimeline_df(r_get_matchTimeline, unique_gameId[loop])
            else:
                users_matchTimeline_df = self.make_matchTimeline_df(r_get_matchTimeline, unique_gameId[loop])
                users_matchTimeline_df_after = pd.concat([users_matchTimeline_df_after, users_matchTimeline_df], axis=0)
            
            # find all matches
            # if loop%100==99:
            #     users_matchTimeline_df_after.to_csv(self.csv_name, mode="a", header=False)
                logging.info(str(unique_gameId[loop])+" to csv"+str(datetime.today()))

            loop+=1
            
            if loop%1000==999:
                flag=False
                self.update_db(users_matchTimeline_df_after)
                logging.info(str(unique_gameId[loop])+" to db "+str(datetime.today()))
                
            if loop==total_length:
                break
            
        return users_matchTimeline_df_after

    def run(self, unique_gameId, db_controller):
        self.set_dbcontroller(db_controller)
        self.request_matchTimeline(unique_gameId)