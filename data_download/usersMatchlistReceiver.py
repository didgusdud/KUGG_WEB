# -*- coding: utf-8 -*-
"""
Created on Mon Aug 17 21:22:40 2020

@author: jhs
"""
import requests
import time
import json
import pandas as pd
import numpy as np
import time
import logging
from datetime import datetime

logging.basicConfig(filename="./usersMatchList "+datetime.today().strftime("%Y-%m-%d")+".log", level=logging.INFO)

class UsersMatchlistReceiver:
    def __init__(self, api_key, csv_name):
        self.API_KEY = api_key
        self.csv_name = csv_name
        self.seasons = "13"
        
    def set_dbcontroller(self, db_controller):
        self.db_controller_ = db_controller
        
    def update_db(self, accountId):
        self.db_controller_.update_matchInfo(accountId)
        
    def make_usersMatchlist_df(self, r_get_matchList, users_accountId):
        r_get_matchList_json = r_get_matchList.json()
        
        users_matchList_df = pd.DataFrame(r_get_matchList_json["matches"])
        users_matchList_df['accountId'] = users_accountId
        
        return users_matchList_df
    
    def request_usersMatchlist(self, usersInfo_df):
        # beginTime=0
        print("usersinfo_df length: ", len(usersInfo_df))
        count_idx=0
        flag=False
        # tmp_idx=0
        
        # usersInfo_df.values = accountId, revisionDate
        for accountId, revisionDate in usersInfo_df.values:
            beginIndex = 0
            # flag = False
            
            while True:
                # print(accountId, revisionDate)
                get_matchList = "https://kr.api.riotgames.com/lol/match/v4/matchlists/by-account/"+accountId \
                    +"?season="+self.seasons+"&beginTime="+str(int(revisionDate))+"&beginIndex="+str(beginIndex)+"&api_key="+self.API_KEY
                r_get_matchList = requests.get(get_matchList)
                
                # request time out
                if r_get_matchList.status_code == 429:
                    # print("time exceed")
                    logging.warning(accountId+" time exceed, idx: "+str(count_idx))
                    time.sleep(30)
                    continue
                
                # if data not found
                elif r_get_matchList.status_code==404:
                    logging.info("data not found= "+accountId)
                    
                    revisionDate = self.db_controller_.select_matchlist_accountId(accountId)
                    continue
                
                # request status code not 200(normal code)
                elif r_get_matchList.status_code != 200:
                    # print("status code = ", r_get_matchList.status_code)
                    logging.error("status code = "+str(r_get_matchList.status_code))
                    time.sleep(10)
                    continue
                
                # if no matches
                if r_get_matchList.json()['matches'] == []:
                    # print("no matches in "+accountId+" idx= "+str(beginIndex))
                    break
                    
                if not flag:
                    flag = True
                    users_matchList_df_after = self.make_usersMatchlist_df(r_get_matchList, accountId)
                else:
                    users_matchList_df = self.make_usersMatchlist_df(r_get_matchList, accountId)
                    users_matchList_df_after = pd.concat([users_matchList_df_after, users_matchList_df], axis=0)
                
                beginIndex+=100
                
                # tmp_idx+=1
                
            count_idx+=1
            # print(len(users_matchList_df_after))
            
            # if tmp_idx>50:
            #     break
            # find all matches
            # users_matchList_df_after.to_csv(self.csv_name, mode="a", header=False)
            # logging.info(accountId+" to csv, beginIdxx= "+str(beginIndex)+" "+str(datetime.today()))
            
        return users_matchList_df_after
    
        
    def run(self, usersInfo_df, db_controller):
        self.set_dbcontroller(db_controller)
        return self.request_usersMatchlist(usersInfo_df)