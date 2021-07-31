# -*- coding: utf-8 -*-
"""
Created on Thu Sep  3 21:49:15 2020

@author: 6794c
"""
import pandas as pd
import time

import usersLeagueReceiver
import usersInfoReceiver
import usersMatchlistReceiver
import matchInfoReceiver
import matchTimelineReceiver
import matchInfo_and_matchTimelineReceiver
import db_controller

# input your api key when you need
class DataReceiver:
    def __init__(self):
        self.API_KEY = None
        self.usersLeague_csv_name = "usersLeague.csv"
        self.usersInfo_csv_name = "usersInfo.csv"
        self.usersMatchlist_csv_name = "usersMatchlist.csv"
        self.matchInfo_csv_name = "matchInfo.csv"
        self.matchTimeline_csv_name = "matchTimeline.csv"
        self.matchInfo_and_matchTimeline_csv_name = "matchInfo_and_matchTimeline.csv"
        
        
        print("loading receiver")
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
        
        self.matchInfo_and_matchTimeline_receiver = matchInfo_and_matchTimelineReceiver.MatchInfo_and_MatchTimelineReceiver(
            self.API_KEY, self.matchInfo_and_matchTimeline_csv_name)
        
        print("check DB connection")
        self.database_controller = db_controller.DBController()
        
        
    def run(self):
        for i in range(1):
            # """test complete"""
            # # usersleague db only maintain recent challenger, grandmaster, master league info
            # usersLeague_df = self.usersLeague_receiver.run()
            # self.database_controller.update_usersLeague(usersLeague_df)
            # print("usersleague complete")
            
            # # first, compare usersleague_df and usersinfo db data for request operation. make summonerId_array which not inside ussersinfoDB
            # # second,  i only request data which not inside usersinfoDB.
            # # usersInfo_df is data which not insde original usersinfoDB
            # summonerId_array = self.database_controller.from_usersLeague_for_usersInfo_summonerId(usersLeague_df)
            # print("residual summonerid array: ", len(summonerId_array))
            # usersInfo_df = self.usersInfo_receiver.run(summonerId_array)
            
            # # it is possible to make usersInfo_df is empty
            # # because usersInfo_df is new data, its revisionDate set 0
            # if len(usersInfo_df)!=0:
            #     self.database_controller.insert_usersInfo(usersInfo_df)
            # print("usersinfo complete")
            
            # # first load usersinfoDB(summonerId, revisionDate)
            # # secnond request usersmatchlist using revisionDate and summonerId. data only received by revisiondate
            # # second update usersmatchlist by usersmatchlist_df
            # usersMatchlist_df = self.usersMatchlist_receiver.run(self.database_controller.load_usersInfo_fromDB(), self.database_controller)
            # usersMatchlist_df.to_csv("check_usersmatchlist.csv", mode='a')
            # self.database_controller.update_usersMatchlist(usersMatchlist_df)
            # print("usersmatchlist complete")
            
            usersMatchlist_df = pd.read_csv("check_usersmatchlist.csv")
            usersMatchlist_df.drop("Unnamed: 0", axis=1, inplace=True)
            print("tmp usersmatchlist load")
            
            self.database_controller.update_DBrevisionDate(usersMatchlist_df)
            print("update dbrevision date complete")
            
            # because of duplicated gameId in usersmatchlist, i must extract unique gameI
            unique_gameId = self.unique_matchList(usersMatchlist_df)
            print("unique gamid length : ", unique_gameId)

            # unique gameid in basis, request matchinfo data
            # matchInfo_df = self.matchInfo_receiver.run(unique_gameId)
            # self.db_controller.update_matchInfo(matchInfo_df)
            ##self.matchInfo_receiver.run(unique_gameId, self.database_controller)
            ##print("matchinfo_df complete")

            ##self.matchTimeline_receiver.run(unique_gameId, self.database_controller)
            # matchTimeline_df = self.matchTimeline_receiver.run(unique_gameId)
            # self.db_controller.update_matchTimeline(matchTimeline_df)
            ##print("matchtimeline complete")
            unique_gameId = unique_gameId.tolist()
            index = unique_gameId.index(4123058900)
            print(index)
            unique_gameId=unique_gameId[index:]
            self.matchInfo_and_matchTimeline_receiver.run(unique_gameId, self.database_controller)
            print("matchinfo_df&matchtimeline complete")

            time.sleep(5)
        self.database_controller.controller_close()

            
            
            # matchInfo_df = self.matchInfo_receiver.run(unique_gameId)
            # self.db_controller.update_matchInfo(matchInfo_df)
            
            # matchTimeline_df = self.matchTimeline_receiver.run(unique_gameId)
            # self.db_controller.update_matchTimeline(matchTimeline_df)

        # default code
        # usersLeague_df = self.usersLeague_receiver.run()
        # print("usersLeague complete")   
        # usersInfo_df = self.usersInfo_receiver.run(usersLeague_df)
        # print("usersInfo complete")
        # usersMatchlist_df = self.usersMatchlist_receiver.run(usersInfo_df)
        # print("usersMatchlist complete")
        # unique_gameId = self.unique_matchList(usersMatchlist_df)
        # self.matchInfo_receiver.run(unique_gameId)
        # print("matchInfo complete")
        # self.matchTimeline_receiver.run(unique_gameId)
        # print("matchTimeline complete")

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