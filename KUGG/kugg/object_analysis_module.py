# -*- coding: utf-8 -*-
"""
Created on Wed Aug 26 20:47:28 2020

@author: 6794c
"""
import pickle
import numpy as np

# OUTER_TURRET='-', 'BOT_LANE-', 'BOT_LANE-MID_LANE',
#         'BOT_LANE-MID_LANE-TOP_LANE', 'BOT_LANE-TOP_LANE', 'MID_LANE-',
#         'MID_LANE-TOP_LANE', 'TOP_LANE-'
# INNER_TURRET='-', 'BOT_LANE-', 'BOT_LANE-MID_LANE',
#         'BOT_LANE-MID_LANE-TOP_LANE', 'BOT_LANE-TOP_LANE', 'MID_LANE-',
#         'MID_LANE-TOP_LANE', 'TOP_LANE-'
# BASE_TURRET='-', 'BOT_LANE-', 'BOT_LANE-MID_LANE',
#         'BOT_LANE-MID_LANE-TOP_LANE', 'BOT_LANE-TOP_LANE', 'MID_LANE-',
#         'MID_LANE-TOP_LANE', 'TOP_LANE-'
# UNDEFINED(INHIB)_TURRET='-', 'BOT_LANE-', 'BOT_LANE-MID_LANE',
#         'BOT_LANE-MID_LANE-TOP_LANE', 'BOT_LANE-TOP_LANE', 'MID_LANE-',
#         'MID_LANE-TOP_LANE', 'TOP_LANE-'
# NEXUS_TURRET = '-', '-MID_LANE-', '-MID_LANE-MID_LANE-'



class ObjectAnalysis:
    def __init__(self, first_object_model=None, object_kills_model=None, object_killsAnd_first_model=None):
        # ObjectAnalysis.py in kugg-web/menu/
        self.model_dic_path = "kugg/static/analysis_models/"
        self.first_object_model=None
        self.object_kills_model=None
        self.object_killsAnd_first_model=None
        
        
        self.object_analysismodel=None
        self.data_encoder=None
        self.update_model("first_object_model")
        self.update_model("object_kills_model")
        self.update_model("object_killsAnd_first_model")
        #self.update_model("tmp_modelupdate")
        self.update_model("object_modelupdate")
        #self.update_mdoel('data_encoder')
    
    # parameter = pickle file
    def update_model(self, object_model):
        if object_model == "first_object_model":
            model_path = self.model_dic_path+"dt_model1.pkl"
            with open(model_path, 'rb') as file:
                self.first_object_model = pickle.load(file)
                return 1
            
        elif object_model == "object_kills_model":
            model_path = self.model_dic_path+"dt_model2.pkl"
            with open(model_path, 'rb') as file:
                self.object_kills_model = pickle.load(file)
                return 2
                
        elif object_model == "object_killsAnd_first_model":
            model_path = self.model_dic_path+"dt_model3.pkl"
            with open(model_path, 'rb') as file:
                self.object_killsAnd_first_model = pickle.load(file)
                return 3

        elif object_model == "object_modelupdate":
            model_path = self.model_dic_path+'second_object_dtmodel.pickle'
            with open(model_path, 'rb') as file:
                self.object_analysismodel = pickle.load(file)
                return 4
            
        elif object_model == 'data_encoder':
            model_path = self.model_dic_path+'categorical_data_encoder.pickle'
            with open(model_path, 'rb') as file:
                self.data_encoder = pickle.load(file)
                return 5
            
        else:
            print("wrong input")
            return -1
        
    # def tmp_model_predict(self, teamId, baronKills, riftHeraldKills, OUTER_TURRET,
    #                       INNER_TURRET, BASE_TURRET, UNDEFINED_TURRET, NEXUS_TURRET,
    #                       AIR_DRAGON, WATER_DRAGON, EARTH_DRAGON, FIRE_DRAGON, ELDER_DRAGON):
        
    #     predict_array = self.tmp_modelupdate.predict_proba(
    #         np.array([teamId, baronKills, riftHeraldKills, OUTER_TURRET, INNER_TURRET,
    #                   BASE_TURRET, UNDEFINED_TURRET, NEXUS_TURRET,
    #                   AIR_DRAGON, WATER_DRAGON, EARTH_DRAGON, FIRE_DRAGON, ELDER_DRAGON]).reshape(1, -1))
        
    #     return predict_array[0][1]

    def oneteam_model_predict(self, teamId, baronKills, riftHeraldKills, OUTER_TURRET,
                          INNER_TURRET, BASE_TURRET, UNDEFINED_TURRET, NEXUS_TURRET,
                          AIR_DRAGON, WATER_DRAGON, EARTH_DRAGON, FIRE_DRAGON, ELDER_DRAGON):
        
        predict_array = self.object_analysismodel.predict_proba(
            np.array([teamId, baronKills, riftHeraldKills, OUTER_TURRET, INNER_TURRET,
                      BASE_TURRET, UNDEFINED_TURRET, NEXUS_TURRET,
                      AIR_DRAGON, WATER_DRAGON, EARTH_DRAGON, FIRE_DRAGON, ELDER_DRAGON]).reshape(1, -1))
        
        return predict_array[0][1]
    
    def twoteam_model_predict(self, BteamId, BbaronKills, BriftHeraldKills, BOUTER_TURRET,
                              BINNER_TURRET, BBASE_TURRET, BUNDEFINED_TURRET, BNEXUS_TURRET,
                              BAIR_DRAGON, BWATER_DRAGON, BEARTH_DRAGON, BFIRE_DRAGON, BELDER_DRAGON,
                              RteamId, RbaronKills, RriftHeraldKills, ROUTER_TURRET,
                              RINNER_TURRET, RBASE_TURRET, RUNDEFINED_TURRET, RNEXUS_TURRET,
                              RAIR_DRAGON, RWATER_DRAGON, REARTH_DRAGON, RFIRE_DRAGON, RELDER_DRAGON):
        
        Bpredict_array = self.object_analysismodel.predict_proba(
            np.array([BteamId, BbaronKills, BriftHeraldKills, BOUTER_TURRET, BINNER_TURRET,
                      BBASE_TURRET, BUNDEFINED_TURRET, BNEXUS_TURRET, BAIR_DRAGON,
                      BWATER_DRAGON, BEARTH_DRAGON, BFIRE_DRAGON, BELDER_DRAGON]).reshape(1,-1))
        Rpredict_array = self.object_analysismodel.predict_proba(
            np.array([RteamId, RbaronKills, RriftHeraldKills, ROUTER_TURRET, RINNER_TURRET,
                      RBASE_TURRET, RUNDEFINED_TURRET, RNEXUS_TURRET, RAIR_DRAGON,
                      RWATER_DRAGON, REARTH_DRAGON, RFIRE_DRAGON, RELDER_DRAGON]).reshape(1, -1))
        
        total_prob = Bpredict_array[0][1]+Rpredict_array[0][1]
        
        # return blue team win probability, red team win probability
        return Bpredict_array[0][1]/total_prob, Rpredict_array[0][1]/total_prob
    
    def first_object_predict(self, fdragon, fharry, fblood, ftower,
                             fbaron, finhib):
        predict_array = self.first_object_model.predict_proba(
            np.array([fblood, finhib, ftower, fharry, fdragon, fbaron]).reshape(1, -1))
        
        # ex. 0.641095145921092....
        return predict_array[0][1]
    
    def object_kills_predict(self, dragonkills, baronkills, inhibkills,
                             harrykills, towerkills):
        predict_array = self.object_kills_model.predict_proba(
            np.array([harrykills, inhibkills, towerkills, baronkills,
                     dragonkills]).reshape(1, -1))
        
        # ex. 0.124412512451231....
        return predict_array[0][1]
    
    def object_killsAnd_first_predict(self, fdragon, fharry, fblood, ftower, fbaron, 
                                    finhib, dragonkills, baronkills, inhibkills,
                                    harrykills, towerkills):
        predict_array = self.object_killsAnd_first_model.predict_proba(
            np.array([harrykills, fharry, inhibkills, fblood, towerkills, dragonkills, baronkills,
                     finhib, fdragon, fbaron, ftower]).reshape(1, -1))
        
        return predict_array[0][1]