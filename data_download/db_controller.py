# -*- coding: utf-8 -*-
"""
Created on Tue Sep  8 14:38:24 2020

@author: 6794c
"""
import pymysql
import copy
import numpy as np
import pandas as pd

class DBController:
    def __init__(self):
        self.conn, self.cur = self.db_connect()       
        
    def db_connect(self):
        conn = pymysql.connect(host="localhost", user='root', password='', db='')
        cur = conn.cursor()
        
        return conn, cur
    
    # usersLeagueDB type = all string
    def update_usersLeague(self, usersLeague_df):
        # tier, leagueId, queue, name, summonerId, summonerName, leaguePoints,
        #       rank, wins, losses, veteran, inactive, freshBlood, hotStreak
        insert_usersLeague_sql = "INSERT into usersleague \
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        update_usersLeague_sql = "UPDATE usersleague \
            SET tier=%s, leagueId=%s, queue=%s, lname=%s, summonerName=%s, leaguePoints=%s, srank=%s, wins=%s, losses=%s, veteran=%s, sinactive=%s, freshBlood=%s, hotStreak=%s \
                WHERE summonerId=%s;"
        delete_usersLeague_sql = "DELETE FROM usersleague\
            WHERE summonerId=%s"
            
        self.cur.execute("SELECT * FROM usersleague")
        rows = self.cur.fetchall()
        request_usersLeauge_summonerId = usersLeague_df["summonerId"].values
        residual_summonerId = copy.deepcopy(request_usersLeauge_summonerId)
        
        for row in rows:
            # DB's summonerId in request summonerId
            if row[4] in request_usersLeauge_summonerId:
                # DB'S leaguepoints not same request leaguePoints
                residual_summonerId = np.delete(residual_summonerId, np.argwhere(residual_summonerId==row[4]))
                # print("0", row[6], int(usersLeague_df[usersLeague_df["summonerId"]==row[4]]["leaguePoints"].values[0]))
                if int(row[6]) != int(usersLeague_df[usersLeague_df["summonerId"]==row[4]]["leaguePoints"].values[0]):
                    
                    update_row = usersLeague_df[usersLeague_df["summonerId"]==row[4]].values[0].tolist()
                    update_row.append(row[4])
                    del update_row[4]

                    self.cur.execute(update_usersLeague_sql, update_row)
            else:
                # print(row[5], row[6])
                self.cur.execute(delete_usersLeague_sql, (row[4],))
        
        self.conn.commit()

        print("usersleague residual summerlength: ", len(residual_summonerId))

        # insert data which not inside DB
        for summonerId in residual_summonerId:
            self.cur.execute(insert_usersLeague_sql,
                             tuple(usersLeague_df[usersLeague_df["summonerId"]==summonerId].values[0]))
            
        self.conn.commit()
        # self.conn.close()
        
        return 0
        
        # extract summonerId from usersLeague for request usersInfo
    def from_usersLeague_for_usersInfo_summonerId(self, usersLeague_df):
        # delete_usersInfo_sql = "DELETE FROM usersInfo WHERE summonerId=%s"
        select_usersInfo_sql = "SELECT * FROM usersInfo"
        self.cur.execute(select_usersInfo_sql)
        
        request_usersLeague_summonerId = usersLeague_df["summonerId"].values
        residual_summonerId = copy.deepcopy(request_usersLeague_summonerId)
             
        for row in self.cur.fetchall():
            residual_summonerId = np.delete(residual_summonerId, np.argwhere(residual_summonerId==row[0]))
            # remove delete option
            # if row[0] not in request_usersLeague_summonerId:
            # # is in DB, but not in latest usersLeague --> need delete
            #     self.cur.execute(delete_usersInfo_sql, row[0])
            
        self.conn.commit()
        
        return residual_summonerId
        
        
    """
    In usersInfo part, did not implement update sql because of too much requestt
    """
    # revision date가 계속 초기화되는 문제 발생 
    def insert_usersInfo(self, usersInfo_df):
        # id, accountId, puuid, name, profileIconId, revesionDate, summonerLevel
        insert_usersInfo_sql = "INSERT INTO usersinfo (summonerId, accountId, puuId, sname, profileIconId, \
            revisionDate, summonerLevel) VALUES (%s, %s, %s, %s, %s, 0, %s)"

        for row in usersInfo_df.values:
            insert_row = row.tolist()
            del insert_row[-2]
            self.cur.execute(insert_usersInfo_sql, insert_row)
            
        self.conn.commit()
        
    def load_usersInfo_fromDB(self):
        select_usersInfo_sql = "select accountId, revisionDate from usersinfo natural join usersleague \
            where tier='CHALLENGER' or tier='MASTER' or tier='GRANDMASTER'"
        
        usersInfo_df = pd.read_sql_query(select_usersInfo_sql, self.conn)
        
        return usersInfo_df
        
    # only given new matchlist.
    # insert new matchlist data to matchlistDB and update and update usersInfo revisionDate column
    def update_usersMatchlist(self, usersMatchlist_df):
        # index, platformId, gameId, champion, queue, season, (begin)timestamp, role, lane, accountId
        insert_usersMatchlist_sql = "INSERT INTO usersmatchlist (platformId, gameId, champion, queue, season, \
            timestamp, role, lane, accountId) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
        # update_usersInfo_sql = "UPDATE usersinfo SET revisionDate=%s WHERE accountId=%s"
        
        # before_account = "initial_account"  # row[-1]
        # recent_timestamp = 100 # row[5]
        for row in usersMatchlist_df.values:
            self.cur.execute(insert_usersMatchlist_sql, row.tolist())
            # if row[-1] != before_account:
            #     before_account = row[-1]
            #     recent_timestamp = row[5]
                
            #     update usersInfo revisionDate 
            #     self.cur.execute(update_usersInfo_sql, [str(recent_timestamp), before_account])
            
        self.conn.commit()
        
    """matchInfo, matchTimeline method only excute insert function"""
    def update_matchInfo(self, matchInfo_df):
        insert_matchInfo_sql = "INSERT INTO matchinfo VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        
        for row in matchInfo_df.values:
            list_row = row
            list_row[10] = str(list_row[10])
            list_row[11] = str(list_row[11])
            list_row[12] = str(list_row[12])
            try:
                self.cur.execute(insert_matchInfo_sql, tuple(list_row))
            except self.conn.IntegrityError:
                continue
            self.conn.commit()
            
    def update_matchTimeline(self, matchTimeline_df):
        insert_matchTimeline_sql = "INSERT INTO matchtimeline VALUES (%s, %s, %s)"
        
        for row in matchTimeline_df.values:
            list_row = row
            list_row[0] = str(list_row[0])
            try:
                self.cur.execute(insert_matchTimeline_sql, tuple(list_row))
            except self.conn.IntegrityError:
                continue
            self.conn.commit()
            
    def update_DBrevisionDate(self, usersMatchlist_df):
        update_usersInfo_sql = "UPDATE usersinfo SET revisionDate=%s WHERE accountId=%s"
        
        before_account = "initial_account" # row[-1]
        recent_timestamp = 0 # row[5]
        for row in usersMatchlist_df.values:
            if row[-1] != before_account:
                before_account = row[-1]
                recent_timestamp = row[5]
                
                # update usersInfo revisionDate 
                self.cur.execute(update_usersInfo_sql, [str(recent_timestamp), before_account])
    
    def select_matchlist_accountId(self, accountId):
        select_matchlist_sql = "SELECT * FROM usersinfo WHERE accountId=%s"
        select_maxtimestamp_sql = "SELECT max(timestamp) FROM usersmatchlist WHERE accountId=%s"
        update_revisionDate_sql = "UPDATE usersinfo SET revisionDate=%s WHERE accountId=%s"
        
        query_length = self.cur.execute(select_matchlist_sql, accountId)
        if query_length==0:
            update_revisionDate = 0
        else:
            self.cur.execute(select_maxtimestamp_sql, accountId)
            update_revisionDate = self.cur.fetchone()[0]
            if update_revisionDate==None:
                update_revisionDate = 0
        
        self.cur.execute(update_revisionDate_sql, (update_revisionDate, accountId))
        self.conn.commit()
        
        return update_revisionDate
    
    def controller_close(self):
        self.conn.close()