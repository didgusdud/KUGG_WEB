# -*- coding: utf-8 -*-
"""
Created on Thu Sep  3 21:49:15 2020

@author: 6794c
"""
import usersLeagueReceiver
import usersInfoReceiver
import usersMatchlistReceiver
import matchInfoReceiver
import matchTimelineReceiver
import pandas as pd

# input your api key when you need

class DataReceiver:
    def __init__(self):
        self.API_KEY = None
        self.usersLeague_csv_name = "usersLeague.csv"
        self.usersInfo_csv_name = "usersInfo.csv"
        self.usersMatchlist_csv_name = "usersMatchlist.csv"
        self.matchInfo_csv_name = "matchInfo.csv"
        self.matchTimeline_csv_name = "matchTimeline.csv"
        
        self.usersLeague_receiver = usersLeagueReceiver.UsersLeagueReceiver(
            self.API_KEY, self.usersLeague_csv_name)
        self.usersInfo_receiver = usersInfoReceiver.UsersInfoReceiver(
            self.API_KEY, self.usersInfo_csv_name)
        self.usersMatchlist_receiver = usersMatchlistReceiver.UsersMatchlistReceiver(
            self.API_KEY, self.usersMatchlist_csv_name)
        self.matchInfo_receiver = matchInfoReceiver.MatchInfoReceiver(
            self.API_KEY, self.matchInfo_csv_name)
        self.matchTimeline_receiver = matchTimelineReceiver.MatchTimelineReceiver(
            self.API_KEY, self.matchTimeline_csv_name)
        
    def run(self):
        usersLeague_df = self.usersLeague_receiver.run()
        print("usersLeague complete")        
        usersInfo_df = self.usersInfo_receiver.run(usersLeague_df)
        print("usersInfo complete")
        usersMatchlist_df = self.usersMatchlist_receiver.run(usersInfo_df)
        print("usersMatchlist complete")
        unique_gameId = self.unique_matchList(usersMatchlist_df)
        self.matchInfo_receiver.run(unique_gameId)
        print("matchInfo complete")
        self.matchTimeline_receiver.run(unique_gameId)
        print("matchTimeline complete")
        
        # usersMatchlist_df = pd.read_csv("usersMatchlist.csv")
        # columns_df = pd.read_csv("columnsInfo_web.csv")
        # columns_list = columns_df[~columns_df["usersMatchlist"].isna()]["usersMatchlist"]
        # usersMatchlist_df.columns = columns_list
        # usersMatchlist_df = usersMatchlist_df.drop("idx_col", axis=1)
        # unique_gameId = self.unique_matchList(usersMatchlist_df)

    def unique_matchList(self, usersMatchlist_df):
        return usersMatchlist_df["gameId"].unique()
        
datareceiver = DataReceiver()
datareceiver.run()