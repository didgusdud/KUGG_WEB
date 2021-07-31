from django.shortcuts import render, redirect
#from .models import UserInfo, MatchList
from django.http import HttpResponse,HttpResponseRedirect,HttpResponseNotFound, Http404
from django.urls import reverse
from django.db.models import Count,Q
from .object_analysis_module import ObjectAnalysis
import math
from django.db import connection as conn
import pandas as pd
import numpy as np
from ast import literal_eval
import json
import datetime
import pickle
# Create your views here.


def convert_datetime(unixtime):
	date = datetime.datetime.fromtimestamp(unixtime).strftime('%Y-%m-%d %H:%M:%S')
	return date # format : str

#홈 화면
def menu_list(request):
	# infos = UserInfo.objects.all()
	# context = {'infos' : infos}
	return render(request, 'kugg/menu_list.html')

def detail_info_list(request):
	# infos = UserInfo.objects.all()
	# context = {'infos' : infos}
	return render(request, 'kugg/detail_info_list.html')

def detail_info_search(request):
	# query = request.GET['query']
	# if query:
	# 	infos = UserInfo.objects.filter(name = query)
	# 	#accountId = UserInfo.objects.get(name = query)
	# 	for info in infos:
	# 		accountId = info.accountId
	# 	matches = MatchList.objects.filter(accountId = accountId)
	# 	#matches = MatchList.objects.all()
	# 	if len(infos) > 1:
	# 		infos = list(infos)
	# 		while len(infos) > 1:
	# 			infos.pop()
	# 	context = {'infos' : infos, 'matches' : matches}
	# 	#context = {'infos' : infos}

	return render(request, 'kugg/detail_info_list.html')

def df_to_json(df):
	df_json_records = df.reset_index().to_json(orient ='records') 
	data = [] 
	data = json.loads(df_json_records) 
	return data

def get_item_tree(cid):
	df_item = pd.read_csv('D:/KUGG/kugg/df/df_item.csv')
	idx_0 = df_item[df_item['item0']==0].index
	df_item = df_item.drop(idx_0)
	item = pd.read_csv('D:/KUGG/kugg/df/item.csv')
	item=item.drop(['Unnamed: 0'],axis=1)
	df_item_list=df_item[df_item['championID']==cid]['item_list'].value_counts().head(10)
	df_item_list=df_item_list.to_frame()
	df_item_list=df_item_list.rename({'item_list':'count'},axis='columns')
	df_item_list=df_item_list.rename_axis("item_list").reset_index()
	df_new=df_item_list['item_list'].str.split('/').apply(pd.Series)
	df_item_list=pd.concat([df_item_list,df_new],axis='columns')
	df_item_list=df_item_list.rename({0:'item0',1:'item1',2:'item2',3:'item3',4:'item4',5:'item5'},axis='columns')
	df_item_list = df_item_list.drop(['item_list'],axis='columns')
	df_item0=item
	df_item1=item
	df_item2=item
	df_item3=item
	df_item4=item
	df_item5=item
	df_item0=df_item0.rename({'itemId':'item0'},axis='columns')
	df_item1=df_item1.rename({'itemId':'item1'},axis='columns')
	df_item2=df_item2.rename({'itemId':'item2'},axis='columns')
	df_item3=df_item3.rename({'itemId':'item3'},axis='columns')
	df_item4=df_item4.rename({'itemId':'item4'},axis='columns')
	df_item5=df_item5.rename({'itemId':'item5'},axis='columns')
	df_item0['item0']=pd.to_numeric(df_item0['item0'])
	df_item1['item1']=pd.to_numeric(df_item1['item1'])
	df_item2['item2']=pd.to_numeric(df_item2['item2'])
	df_item3['item3']=pd.to_numeric(df_item3['item3'])
	df_item4['item4']=pd.to_numeric(df_item4['item4'])
	df_item5['item5']=pd.to_numeric(df_item5['item5'])
	df_item_list['item0']=pd.to_numeric(df_item_list['item0'])
	df_item_list['item1']=pd.to_numeric(df_item_list['item1'])
	df_item_list['item2']=pd.to_numeric(df_item_list['item2'])
	df_item_list['item3']=pd.to_numeric(df_item_list['item3'])
	df_item_list['item4']=pd.to_numeric(df_item_list['item4'])
	df_item_list['item5']=pd.to_numeric(df_item_list['item5'])
	df_item_list = pd.merge(df_item_list, df_item0, how = 'left', on = ['item0'], suffixes=('', '_y'))
	df_item_list=df_item_list.rename({'name':'item0name'},axis='columns')
	df_item_list = pd.merge(df_item_list, df_item1, how = 'left', on = ['item1'], suffixes=('', '_y'))
	df_item_list=df_item_list.rename({'name':'item1name'},axis='columns')
	df_item_list = pd.merge(df_item_list, df_item2, how = 'left', on = ['item2'], suffixes=('', '_y'))
	df_item_list=df_item_list.rename({'name':'item2name'},axis='columns')
	df_item_list = pd.merge(df_item_list, df_item3, how = 'left', on = ['item3'], suffixes=('', '_y'))
	df_item_list=df_item_list.rename({'name':'item3name'},axis='columns')
	df_item_list = pd.merge(df_item_list, df_item4, how = 'left', on = ['item4'], suffixes=('', '_y'))
	df_item_list=df_item_list.rename({'name':'item4name'},axis='columns')
	df_item_list = pd.merge(df_item_list, df_item5, how = 'left', on = ['item5'], suffixes=('', '_y'))
	df_item_list=df_item_list.rename({'name':'item5name'},axis='columns')
	#df_item_list=df_item_list.drop(['item0','item1','item2','item3','item4','item5',],axis=1)
	df_item_list=df_item_list.head(1)
	item_tree = df_to_json(df_item_list)
	return item_tree

def json_to_df(json_data):
	df = json_data.replace('\\','')
	df = df[1:-1]				
	df = literal_eval(df)
	return df

#챔피언/소환사 검색
def info_list(request):
	query = request.GET['query']
	champ_df = pd.read_csv('D:/KUGG/kugg/df/Champ.csv')
	champ_list=list(champ_df['name'].values)

	if query:
		#챔피언 검색
		if query in champ_list:
			#cid=122
			for i,r in enumerate(champ_df['name']):
				if query == r:
					cid = champ_df['champion'][i]
			
			item_tree = get_item_tree(int(cid))
			#print(item_tree)
			context = {'selected_champ' : query, 'champ_list':champ_list, 'item_tree':item_tree}
			print("search champion")
			return render(request, 'kugg/selected_champion_list.html', context)
		#소환사명 검색			
		try:
			curs = conn.cursor()
			sql = "select * from usersinfo where sname=(%s)"
			curs.execute(sql,(query,))
			usersinfo = curs.fetchone()
			summonerId = usersinfo[0]
			accountId = usersinfo[1]
			sname = usersinfo[3]
			profileIconId = usersinfo[4]
			
			revisionDate_unix = usersinfo[5]/1000
			revisionDate = convert_datetime(revisionDate_unix)
			summonerLevel = usersinfo[6]
			print("userinfo complete")
		except:
			conn.rollback()
			print("Failed selecting in usersinfo")
			context = {"username": query}
			return render(request, 'kugg/info_list.html',context)
		try:
			sql = "select * from usersleague where summonerId=(%s)"
			curs.execute(sql,(summonerId,))
			usersleague = curs.fetchone()	
			tier = usersleague[0]
			#leagueId = usersleague[1]
			queue = usersleague[2] #게임종류
			lname = usersleague[3] #리그이름
			leaguePoints = usersleague[6]
			srank = usersleague[7] #마스터 1에서 숫자부분
			wins = usersleague[8]
			lossers = usersleague[9]
			veteran = usersleague[10]
			win_rate = math.trunc(wins*100/(wins+lossers))

			info_df = pd.DataFrame(columns=['sname','profileIconId','revisionDate','summonerLevel','tier','queue','lname','leaguePoints','srank','wins','lossers','veteran','win_rate'])
			info_df.loc[0]=[sname,profileIconId,revisionDate,summonerLevel,tier,queue,lname,leaguePoints,srank,wins,lossers,veteran,win_rate]
			#print(info_df)
			# info_json_records = info_df.reset_index().to_json(orient ='records') 
			# info_data = [] 
			# info_data = json.loads(info_json_records) 
			info_data = df_to_json(info_df)
			#print(info_data)
			print("uesrleague complete")
		except:
			conn.rollback()
			info_df = pd.DataFrame(columns=['sname','profileIconId','revisionDate','summonerLevel'])
			info_df.loc[0]=[sname,profileIconId,revisionDate,summonerLevel]
			#print(info_df)
			# info_json_records = info_df.reset_index().to_json(orient ='records') 
			# info_data = [] 
			# info_data = json.loads(info_json_records) 
			info_data = df_to_json(info_df)
			print("Failed selecting in usersleague")
		try:
			sql = "select * from usersmatchlist_sample where accountId=(%s) limit 20" 
			curs.execute(sql,(accountId,))
			data = curs.fetchall()

			platformId=[]
			gameId=[]
			champion_tmp=[]
			queue=[]
			season=[]
			timestamp=[]
			role=[]
			lane=[]
			
			for t in data:
				platformId.append(t[0])
				gameId.append(t[1])
				champion_tmp.append(t[2])
				queue.append(t[3])
				season.append(t[4])
				timestamp.append(t[5])
				role.append(t[6])
				lane.append(t[7])	
			
			champion=[]
			for c in champion_tmp:
				for i,r in enumerate(champ_df['champion']):
					if c == r:
						champion.append(champ_df['name'][i])
			#print(champion)
			columns_matchlist = ['platformId','gameId','champion','queue','season','timestamp','role','lane']
			
			matchlists = []
			gameId_len = len(gameId)
			for idx in range(gameId_len):
				matchlist = [platformId[idx],gameId[idx],champion[idx],queue[idx],season[idx],timestamp[idx],role[idx],lane[idx]]
				matchlists.append(matchlist)
			print("matchlist complete")
			#print(matchlists)
			
		except:
			conn.rollback()
			print("Failed selecting in usersmatchlist")
			
		try:
			#gameId = gameId[-1::-1]
			matchlists = matchlists[-1::-1]
			gameId = tuple(gameId)

			# gameId = (4684958376, 4684716231, 4681708889)
			# gameId_len = 3
			if gameId_len == 1:
				sql = "select * from matchinfo where gameMode='CLASSIC' and gameId=(%s)"  #게임이 여러개면 or연산
			elif gameId_len ==2:
				sql = "select * from matchinfo where gameMode='CLASSIC' and gameId=(%s) or gameId=(%s)"
			elif gameId_len ==3:
				sql = "select * from matchinfo where gameMode='CLASSIC' and gameId=(%s) or gameId=(%s) or gameId=(%s)"
			elif gameId_len ==4:
				sql = "select * from matchinfo where gameMode='CLASSIC' and (gameId=(%s) or gameId=(%s) or gameId=(%s) or gameId=(%s))"
			elif gameId_len ==5:
				sql = "select * from matchinfo where gameMode='CLASSIC' and (gameId=(%s) or gameId=(%s) or gameId=(%s) or gameId=(%s) or gameId=(%s))"
			elif gameId_len ==6:
				sql = "select * from matchinfo where gameMode='CLASSIC' and (gameId=(%s) or gameId=(%s) or gameId=(%s) or gameId=(%s) or gameId=(%s) or gameId=(%s))"
			elif gameId_len ==7:
				sql = "select * from matchinfo where gameMode='CLASSIC' and (gameId=(%s) or gameId=(%s) or gameId=(%s) or gameId=(%s) or gameId=(%s) or gameId=(%s) or gameId=(%s))"
			elif gameId_len ==8:
				sql = "select * from matchinfo where gameMode='CLASSIC' and (gameId=(%s) or gameId=(%s) or gameId=(%s) or gameId=(%s) or gameId=(%s) or gameId=(%s) or gameId=(%s) or gameId=(%s))"
			elif gameId_len ==9:
				sql = "select * from matchinfo where gameMode='CLASSIC' and (gameId=(%s) or gameId=(%s) or gameId=(%s) or gameId=(%s) or gameId=(%s) or gameId=(%s) or gameId=(%s) or gameId=(%s) or gameId=(%s))"
			elif gameId_len ==10:
				sql = "select * from matchinfo where gameMode='CLASSIC' and (gameId=(%s) or gameId=(%s) or gameId=(%s) or gameId=(%s) or gameId=(%s) or gameId=(%s) or gameId=(%s) or gameId=(%s) or gameId=(%s) or gameId=(%s))"
			elif gameId_len ==11:
				sql = "select * from matchinfo where gameMode='CLASSIC' and (gameId=(%s) or gameId=(%s) or gameId=(%s) or gameId=(%s) or gameId=(%s) or gameId=(%s) or gameId=(%s) or gameId=(%s) or gameId=(%s) or gameId=(%s) or gameId=(%s))"
			elif gameId_len ==12:
				sql = "select * from matchinfo where gameMode='CLASSIC' and (gameId=(%s) or gameId=(%s) or gameId=(%s) or gameId=(%s) or gameId=(%s) or gameId=(%s) or gameId=(%s) or gameId=(%s) or gameId=(%s) or gameId=(%s) or gameId=(%s) or gameId=(%s))"
			elif gameId_len ==13:
				sql = "select * from matchinfo where gameMode='CLASSIC' and (gameId=(%s) or gameId=(%s) or gameId=(%s) or gameId=(%s) or gameId=(%s) or gameId=(%s) or gameId=(%s) or gameId=(%s) or gameId=(%s) or gameId=(%s) or gameId=(%s) or gameId=(%s) or gameId=(%s))"
			elif gameId_len ==14:
				sql = "select * from matchinfo where gameMode='CLASSIC' and (gameId=(%s) or gameId=(%s) or gameId=(%s) or gameId=(%s) or gameId=(%s) or gameId=(%s) or gameId=(%s) or gameId=(%s) or gameId=(%s) or gameId=(%s) or gameId=(%s) or gameId=(%s) or gameId=(%s) or gameId=(%s))"
			elif gameId_len ==15:
				sql = "select * from matchinfo where gameMode='CLASSIC' and (gameId=(%s) or gameId=(%s) or gameId=(%s) or gameId=(%s) or gameId=(%s) or gameId=(%s) or gameId=(%s) or gameId=(%s) or gameId=(%s) or gameId=(%s) or gameId=(%s) or gameId=(%s) or gameId=(%s) or gameId=(%s) or gameId=(%s))"
			elif gameId_len ==16:
				sql = "select * from matchinfo where gameMode='CLASSIC' and (gameId=(%s) or gameId=(%s) or gameId=(%s) or gameId=(%s) or gameId=(%s) or gameId=(%s) or gameId=(%s) or gameId=(%s) or gameId=(%s) or gameId=(%s) or gameId=(%s) or gameId=(%s) or gameId=(%s) or gameId=(%s) or gameId=(%s) or gameId=(%s))"
			elif gameId_len ==17:
				sql = "select * from matchinfo where gameMode='CLASSIC' and (gameId=(%s) or gameId=(%s) or gameId=(%s) or gameId=(%s) or gameId=(%s) or gameId=(%s) or gameId=(%s) or gameId=(%s) or gameId=(%s) or gameId=(%s) or gameId=(%s) or gameId=(%s) or gameId=(%s) or gameId=(%s) or gameId=(%s) or gameId=(%s) or gameId=(%s))"
			elif gameId_len ==18:
				sql = "select * from matchinfo where gameMode='CLASSIC' and (gameId=(%s) or gameId=(%s) or gameId=(%s) or gameId=(%s) or gameId=(%s) or gameId=(%s) or gameId=(%s) or gameId=(%s) or gameId=(%s) or gameId=(%s) or gameId=(%s) or gameId=(%s) or gameId=(%s) or gameId=(%s) or gameId=(%s) or gameId=(%s) or gameId=(%s) or gameId=(%s))"
			elif gameId_len ==19:
				sql = "select * from matchinfo where gameMode='CLASSIC' and (gameId=(%s) or gameId=(%s) or gameId=(%s) or gameId=(%s) or gameId=(%s) or gameId=(%s) or gameId=(%s) or gameId=(%s) or gameId=(%s) or gameId=(%s) or gameId=(%s) or gameId=(%s) or gameId=(%s) or gameId=(%s) or gameId=(%s) or gameId=(%s) or gameId=(%s) or gameId=(%s) or gameId=(%s))"
			elif gameId_len ==20:
				print('gamId 20')
				sql = "select * from matchinfo where gameMode='CLASSIC' and (gameId=(%s) or gameId=(%s) or gameId=(%s) or gameId=(%s) or gameId=(%s) or gameId=(%s) or gameId=(%s) or gameId=(%s) or gameId=(%s) or gameId=(%s) or gameId=(%s) or gameId=(%s) or gameId=(%s) or gameId=(%s) or gameId=(%s) or gameId=(%s) or gameId=(%s) or gameId=(%s) or gameId=(%s) or gameId=(%s))"
			curs.execute(sql,gameId)
			
			print("sql complete")
			data_list=[]
			match_num=0
			matchinfo = curs.fetchone()

			print("fetch complete")
			c = 0
			comp_idx = 0
			#print(matchlists[0])

			gameId= gameId[-1::-1]
			#print(gameId)
			matchlists_comp=[]
			while matchinfo:
				#print(matchinfo[8])
				for i,g in enumerate(gameId):
					if g == matchinfo[0]:
						comp_idx = i
				#print(gameId[comp_idx])

				if matchinfo[8] == "CLASSIC" :
					#print("if CLASSIC")
					matchlists_comp.append(matchlists[comp_idx])

					#print(matchinfo[0])
					#print(matchinfo[8])
					teams = matchinfo[10]
					participants = matchinfo[11]
					pId = matchinfo[12]
					print('teams,participants')

					# teams = teams.replace('\\','')
					# teams = teams[1:-1]				
					# teams = literal_eval(teams)
					teams = json_to_df(teams)
					
					# participants = participants.replace('\\','')
					# participants = participants[1:-1]
					# participants = literal_eval(participants)
					participants = json_to_df(participants)
					
					
					# pId = pId.replace('\\','')
					# pId = pId[1:-1]
					# pId = literal_eval(pId)
					pId = json_to_df(pId)
					
					parts = [ pId[i]['player']['accountId'] for i in range(10)]
					#print(all_part)
					for i,a in enumerate(parts):
					    if a == accountId:
					        idx = i
					win_lose = participants[idx]['stats']['win']
					
					if win_lose == True:
						game_win = "승리"
					elif win_lose == False:
						game_win = "패배"

					spell1Id = participants[idx]['spell1Id']
					spell2Id = participants[idx]['spell2Id']
					perkPrimaryStyle = participants[idx]['stats']['perkPrimaryStyle']
					perkSubStyle = participants[idx]['stats']['perkSubStyle']
					item0 = participants[idx]['stats']['item0']
					item1 = participants[idx]['stats']['item1']
					item2 = participants[idx]['stats']['item2']
					item3 = participants[idx]['stats']['item3']
					item4 = participants[idx]['stats']['item4']
					item5 = participants[idx]['stats']['item5']
					item6 = participants[idx]['stats']['item6']
					item = [item0,item1,item2,item3,item4,item5,item6]
					visionWards = participants[idx]['stats']['visionWardsBoughtInGame']
					visionScore = participants[idx]['stats']['visionScore']
					kills = participants[idx]['stats']['kills']
					deaths = participants[idx]['stats']['deaths']
					assists = participants[idx]['stats']['assists']
					kda = round((kills + assists)/deaths,2) if deaths != 0 else 'perfect'
					penta = participants[idx]['stats']['pentaKills']
					quadra = participants[idx]['stats']['quadraKills']
					triple = participants[idx]['stats']['tripleKills']
					double = participants[idx]['stats']['doubleKills']
					if penta >= 1:
					    killmsg = '펜타킬'
					elif quadra >=1:
					    killmsg = '쿼드라킬'
					elif triple >=1:
					    killmsg = '트리플킬'
					elif double >=1: 
					    killmsg = '더블킬'
					else:
					    killmsg = 0
					totalDamageDealt = participants[idx]['stats']['totalDamageDealt']
					totalMinionsKilled = participants[idx]['stats']['totalMinionsKilled']
					champLevel = participants[idx]['stats']['champLevel']
					
					# pname=[]
					# for p in parts:
					# 	sql = "select * from usersinfo where accountId=(%s)"
					# 	curs.execute(sql,(p,))
					# 	data = curs.fetchone()
					# 	pname.append(data[7])
					# print(pname)

					p1champ = participants[0]['championId']
					p2champ = participants[1]['championId']
					p3champ = participants[2]['championId']
					p4champ = participants[3]['championId']
					p5champ = participants[4]['championId']
					p6champ = participants[5]['championId']
					p7champ = participants[6]['championId']
					p8champ = participants[7]['championId']
					p9champ = participants[8]['championId']
					p10champ = participants[9]['championId']
					pchamp_tmp = [p1champ,p2champ,p3champ,p4champ,p5champ,p6champ,p7champ,p8champ,p9champ,p10champ]			
					#print(p1champ)
					gameCreation = matchinfo[2]
					gameDurationH = math.trunc(matchinfo[3]/60)
					gameDurationS = matchinfo[3]%60
					queueId = matchinfo[4]
					mapId = matchinfo[5]
					seasonId = matchinfo[6]
					gameVersion = matchinfo[7][:5]
					gameMode = matchinfo[8]
					gameType = matchinfo[9]
					info = [gameCreation,gameDurationH,gameDurationS,queueId,mapId,seasonId,gameVersion,gameMode,gameType]
					#print(info)
					#print(teams[0]['bans'])
					bans_tmp = [teams[i]['bans'][j]['championId'] for i in range(2) for j in range(5)]
					#print(bans_tmp)
					pchamp=[]
					bans=[]
					
					for c,b in zip(pchamp_tmp,bans_tmp):
						for i,r in enumerate(champ_df['champion']):
							if c == r:
								pchamp.append(champ_df['name'][i])
							if b == r:
								bans.append(champ_df['name'][i])
					#print(bans)
					part = [spell1Id,spell2Id,perkPrimaryStyle,perkSubStyle,item,visionWards,visionScore,kills,deaths,assists,kda,killmsg,totalDamageDealt,totalMinionsKilled,champLevel,pchamp,bans,game_win] #,lane]
					
					match = matchlists_comp[match_num] + info + part  #+ bans
					c+=1
					match_num += 1

					columns_info = ['gameCreation','gameDurationH','gameDurationS','queueId','mapId','seasonId','gameVersion','gameMode','gameType']
					#columns_bans = ['ban1','ban2','ban3','ban4','ban5','ban6','ban7','ban8','ban9','ban10']
					columns_part = ['spell1Id','spell2Id','perkPrimaryStyle','perkSubStyle','item','visionWardsBoughtInGame','visionScore','kills','deaths','assists','kda','killmsg','totalDamageDealt','totalMinionsKilled','champLevel','pchamp','bans','game_win'] #,'lane']
					columns = columns_matchlist + columns_info  + columns_part  #+ columns_bans
					print("dataframe")
					#print(game_win)
					df = pd.DataFrame(columns=columns)
					df.loc[0]=match

					#df에 한줄씩 추가
					# json_records = df.reset_index().to_json(orient ='records')
					# data = [] 
					# data = json.loads(json_records) 
					data = df_to_json(df)
					#json들의 list를 만들어서 20개 json을 담는다
					
					data_list.append(data)
				
				matchinfo = curs.fetchone()
			print("all complete")	
			#print(data_list)
			#print(info_data)
			context = {'match_list': data_list, 'info' : info_data}

			curs.close()
			conn.close()
		except:
			conn.rollback()
			print("Failed selecting in matchinfo")
			context = {'context' : 'NULL'}
	
	else:
		err = "소환사명 또는 챔피언명을 입력해주세요"
		context = {'err' : err}

	return render(request, 'kugg/info_list.html', context)


def platinum_object_list(request):
	obj = ObjectAnalysis()
	t = request.GET.get('tier')
	s1 = request.GET.get('드래곤')
	s2 = request.GET.get('바론')
	s3 = request.GET.get('억제기')
	# s4 = request.GET.get('바람용')
	# s5 = request.GET.get('화염용')
	# s6 = request.GET.get('대지용')
	s7 = request.GET.get('전령')
	s8 = request.GET.get('타워')

	c1 = request.GET.get('드래곤퍼블')
	c2 = request.GET.get('전령퍼블')
	c3 = request.GET.get('킬퍼블')
	c4 = request.GET.get('타워퍼블')
	c5 = request.GET.get('바론퍼블')
	c6 = request.GET.get('억제기퍼블')
	
	sc1 = request.GET.get('sc드래곤퍼블')
	sc2 = request.GET.get('sc전령퍼블')
	sc3 = request.GET.get('sc킬퍼블')
	sc4 = request.GET.get('sc타워퍼블')
	sc5 = request.GET.get('sc바론퍼블')
	sc6 = request.GET.get('sc억제기퍼블')
	sc7 = request.GET.get('sc드래곤')
	sc8 = request.GET.get('sc바론')
	sc9 = request.GET.get('sc억제기')
	sc10 = request.GET.get('sc전령')
	sc11 = request.GET.get('sc타워')

	######
	top1 = request.GET.get('check15')
	top2 = request.GET.get('check16')
	top3 = request.GET.get('check17')
	mid1 = request.GET.get('check24')
	mid2 = request.GET.get('check23')
	mid3 = request.GET.get('check22')
	bot1 = request.GET.get('check25')
	bot2 = request.GET.get('check26')
	bot3 = request.GET.get('check27')
	topin = request.GET.get('check18')
	midin = request.GET.get('check21')
	botin = request.GET.get('check28')
	twin1 = request.GET.get('check19')
	twin2 = request.GET.get('check20')

	red_top1 = request.GET.get('check1')
	red_top2 = request.GET.get('check2')
	red_top3 = request.GET.get('check3')
	red_mid1 = request.GET.get('check12')
	red_mid2 = request.GET.get('check9')
	red_mid3 = request.GET.get('check8')
	red_bot1 = request.GET.get('check14')
	red_bot2 = request.GET.get('check13')
	red_bot3 = request.GET.get('check11')
	red_topin = request.GET.get('check4')
	red_midin = request.GET.get('check7')
	red_botin = request.GET.get('check10')
	red_twin1 = request.GET.get('check5')
	red_twin2 = request.GET.get('check6')

	baron = request.GET.get('Bbaron')
	herald = request.GET.get('Bjeon')
	red_baron = request.GET.get('Rbaron')
	red_herald = request.GET.get('Rjeon')

	water = request.GET.get('Bdragon1')
	air = request.GET.get('Bdragon2')
	earth = request.GET.get('Bdragon3')
	fire = request.GET.get('Bdragon4')
	elder = request.GET.get('Bdragon5')
	

	red_water = request.GET.get('Rdragon1')
	red_air = request.GET.get('Rdragon2')
	red_earth = request.GET.get('Rdragon3')
	red_fire = request.GET.get('Rdragon4')
	red_elder = request.GET.get('Rdragon5')
	
	selected_team = request.GET.get('B/R')
	print(t)
	print(selected_team)
	map_list = [top1, mid1, bot1, top2, mid2, bot2, top3, mid3, bot3, topin, midin, botin, twin1, twin2]
	map_list = map_list + [red_top1,red_top2,red_top3,red_mid1,red_mid2,red_mid3,red_bot1,red_bot2,red_bot3,red_topin,red_midin,red_botin,red_twin1,red_twin2]
	# map_list = map_list +[baron,herald,dragon1,dragon2,dragon3,dragon4,dragon5,dragon6]
	# map_list = map_list +[red_baron,red_herald,red_dragon1,red_dragon2,red_dragon3,red_dragon4,red_dragon5,red_dragon6]
	
	# outer = [map_list[0], map_list[1], map_list[2]]
	# inner = [map_list[3], map_list[4], map_list[5]]
	# base = [map_list[6], map_list[7], map_list[8]]
	# undifined = [map_list[9], map_list[10], map_list[11]]
	# nexus = [map_list[12], map_list[13]]


	hidden = request.GET.get('hidden_flag')
	print(hidden)

	# pred_first_d = math.floor(obj.first_object_predict(1,0,0,0,0,0) * 100)
	# pred_first_h = math.floor(obj.first_object_predict(0,1,0,0,0,0) * 100)
	# pred_first_k = math.floor(obj.first_object_predict(0,0,1,0,0,0) * 100)
	# pred_first_t = math.floor(obj.first_object_predict(0,0,0,1,0,0) * 100)
	# pred_first_b = math.floor(obj.first_object_predict(0,0,0,0,1,0) * 100)
	# pred_first_i = math.floor(obj.first_object_predict(0,0,0,0,0,1) * 100)
	# pred_first_list = [pred_first_d,pred_first_h,pred_first_k,pred_first_t,pred_first_b,pred_first_i]
	# first_message_list = ["드래곤","전령","킬","타워","바론","억제기"]
	
	# first_max_val,first_message = pred_first_list[0] ,first_message_list[0]
	# for i,j in zip(pred_first_list,first_message_list):
	# 	if i > first_max_val:
	# 		first_max_val,first_message = i,j

	# if s8 :
	# 	pred_kills = math.floor(obj.object_kills_predict(s1,s2,s3,s7,s8) * 100)
	# 	#pred_kills = math.floor(pred_kills)
	# 	ss1 = str(int(s1)+1)
	# 	ss2 = str(int(s2)+1)
	# 	ss3 = str(int(s3)+1)
	# 	pred_kills_h = math.floor(obj.object_kills_predict(ss1,s2,s3,s7,s8) * 100)
	# 	pred_kills_b = math.floor(obj.object_kills_predict(s1,ss2,s3,s7,s8) * 100)
	# 	pred_kills_d = math.floor(obj.object_kills_predict(s1,s2,ss3,s7,s8) * 100)
	# 	pred_kills_list = [pred_kills_h,pred_kills_b,pred_kills_d]
	# 	# max_v = max(pred_list)
	# 	kills_message_list = ["전령","바론", "드래곤"]
		
	# 	max_val,message = pred_kills_list[0] ,kills_message_list[0]
		 
	# 	for i,j in zip(pred_kills_list,kills_message_list):
	# 		if i > max_val:
	# 			max_val,message = i,j
	
	# 	if t:			
	# 		context = {'s1' : s1, 
	# 					's2' : s2,
	# 					's3' : s3,
	# 					's7' : s7,
	# 					's8' : s8,
	# 					't' : t,
	# 					'pred_kills' : pred_kills,
	# 					'pred_kills_h' : pred_kills_h,
	# 					'pred_kills_b' : pred_kills_b,
	# 					'pred_kills_d' : pred_kills_d,
	# 					'max_val' : max_val,
	# 					'message' : message,
	# 					'first_max_val' : first_max_val,
	# 					'first_message' : first_message
	# 					}
	# 	else:
	# 		context = {'s1' : s1, 
	# 					's2' : s2,
	# 					's3' : s3,
	# 					's7' : s7,
	# 					's8' : s8,
	# 					'pred_kills' : pred_kills,
	# 					'pred_kills_h' : pred_kills_h,
	# 					'pred_kills_b' : pred_kills_b,
	# 					'pred_kills_d' : pred_kills_d,
	# 					'max_val' : max_val,
	# 					'message' : message,
	# 					'first_max_val' : first_max_val,
	# 					'first_message' : first_message
	# 					}

	# elif c1 or c2 or c3 or c4 or c5 or c6:
	# 	if not c1:
	# 		c1 = 0
	# 	if not c2:
	# 		c2 = 0
	# 	if not c3:
	# 		c3 = 0
	# 	if not c4:
	# 		c4 = 0
	# 	if not c5:
	# 		c5 = 0
	# 	if not c6:
	# 		c6 = 0
	# 	pred_first = math.floor(obj.first_object_predict(c1,c2,c3,c4,c5,c6) * 100)
	# 	flag = 1
	# 	if t:		
	# 		context = {'c1' : c1,
	# 					'c2' : c2,
	# 					'c3' : c3,
	# 					'c4' : c4,
	# 					'c5' : c5,
	# 					'c6' : c6,
	# 					't' : t,
	# 					'flag' : flag,
	# 					'pred_first' : pred_first,
	# 					'first_max_val' : first_max_val,
	# 					'first_message' : first_message}
	# 	else:
	# 		context = {'c1' : c1,
	# 					'c2' : c2,
	# 					'c3' : c3,
	# 					'c4' : c4,
	# 					'c5' : c5,
	# 					'c6' : c6,
	# 					'flag' : flag,
	# 					'notier' : '티어를 선택하지 않았습니다!!',
	# 					'pred_first' : pred_first,
	# 					'first_max_val' : first_max_val,
	# 					'first_message' : first_message}
	# elif sc1 or sc2 or sc3 or sc4 or sc5 or sc6:
	# 	if not sc1:
	# 		sc1 = 0
	# 	if not sc2:
	# 		sc2 = 0
	# 	if not sc3:
	# 		sc3 = 0
	# 	if not sc4:
	# 		sc4 = 0
	# 	if not sc5:
	# 		sc5 = 0
	# 	if not sc6:
	# 		sc6 = 0

	# 	pred_k_f = math.floor(obj.object_killsAnd_first_predict(sc1,sc2,sc3,sc4,sc5,sc6,sc7,sc8,sc9,sc10,sc11)*100)
	# 	context = {'sc1' : sc1,
	# 				'sc2' : sc2,
	# 				'sc3' : sc3,
	# 				'sc4' : sc4,
	# 				'sc5' : sc5,
	# 				'sc6' : sc6,
	# 				'sc7' : sc7,
	# 				'sc8' : sc8,
	# 				'sc9' : sc9,
	# 				'sc10' : sc10,
	# 				'sc11' : sc11,
	# 				'first_message' : first_message,
	# 				'pred_k_f' : pred_k_f}
	if hidden:
		
		for i,r in enumerate(map_list):
			if not r:
				map_list[i]=0
		predict_tmp = 0
		flag_predict=0
		if selected_team == '100':
			print('blue')
			
			if not top3 and not mid3 and not bot3: OUTER_TURRET = 1
			elif not top3 and not mid3 and bot3: OUTER_TURRET = 2
			elif not top3 and mid3 and bot3: OUTER_TURRET = 3
			elif top3 and mid3 and bot3: OUTER_TURRET = 4
			elif top3 and not mid3 and bot3: OUTER_TURRET = 5
			elif not top3 and mid3 and not bot3: OUTER_TURRET = 6
			elif top3 and mid3 and not bot3: OUTER_TURRET = 7
			elif top3 and not mid3 and not bot3: OUTER_TURRET = 8

			if not top2 and not mid2 and not bot2: INNER_TURRET = 1
			elif not top2 and not mid2 and bot2: INNER_TURRET = 2
			elif not top2 and mid2 and bot2: INNER_TURRET = 3
			elif top2 and mid2 and bot2: INNER_TURRET = 4
			elif top2 and not mid2 and bot2: INNER_TURRET = 5
			elif not top2 and mid2 and not bot2: INNER_TURRET = 6
			elif top2 and mid2 and not bot2: INNER_TURRET = 7
			elif top2 and not mid2 and not bot2: INNER_TURRET = 8

			if not top1 and not mid1 and not bot1: BASE_TURRET = 1
			elif not top1 and not mid1 and bot1: BASE_TURRET = 2
			elif not top1 and mid1 and bot1: BASE_TURRET = 3
			elif top1 and mid1 and bot1: BASE_TURRET = 4
			elif top1 and not mid1 and bot1: BASE_TURRET = 5
			elif not top1 and mid1 and not bot1: BASE_TURRET = 6
			elif top1 and mid1 and not bot1: BASE_TURRET = 7
			elif top1 and not mid1 and not bot1: BASE_TURRET = 8

			if not topin and not midin and not botin: UNDEFINED_TURRET = 1
			elif not topin and not midin and botin: UNDEFINED_TURRET = 2
			elif not topin and midin and botin: UNDEFINED_TURRET = 3
			elif topin and midin and botin: UNDEFINED_TURRET = 4
			elif topin and not midin and botin: UNDEFINED_TURRET = 5
			elif not topin and midin and not botin: UNDEFINED_TURRET = 6
			elif topin and midin and not botin: UNDEFINED_TURRET = 7
			elif topin and not midin and not botin: UNDEFINED_TURRET = 8


			if not twin1 and not twin2: NEXUS_TURRET = 1
			elif not twin1 and twin2: NEXUS_TURRET = 2
			elif twin1 and not twin2: NEXUS_TURRET = 2
			elif twin1 and twin2: NEXUS_TURRET = 3

			
			predict_one = math.floor(obj.oneteam_model_predict(selected_team, baron,herald, OUTER_TURRET,
	                          INNER_TURRET, BASE_TURRET, UNDEFINED_TURRET, NEXUS_TURRET,
	                          air, water, earth, fire, elder)*100)
			print(predict_one)
			if predict_one == 0:
				predict_one = 'No data'
			selected_team = 'BLUE'
			context ={'t':t,
						'selected_team':selected_team,
						'predict_one':predict_one,
						}

		elif selected_team == '200':
			print("red team")
			
			if not red_top3 and not red_mid3 and not red_bot3: OUTER_TURRET = 1
			elif not red_top3 and not red_mid3 and red_bot3: OUTER_TURRET = 2
			elif not red_top3 and red_mid3 and red_bot3: OUTER_TURRET = 3
			elif red_top3 and red_mid3 and red_bot3: OUTER_TURRET = 4
			elif red_top3 and not red_mid3 and red_bot3: OUTER_TURRET = 5
			elif not red_top3 and red_mid3 and not red_bot3: OUTER_TURRET = 6
			elif red_top3 and red_mid3 and not red_bot3: OUTER_TURRET = 7
			elif red_top3 and not red_mid3 and not red_bot3: OUTER_TURRET = 8

			if not red_top2 and not red_mid2 and not red_bot2: INNER_TURRET = 1
			elif not red_top2 and not red_mid2 and red_bot2: INNER_TURRET = 2
			elif not red_top2 and red_mid2 and red_bot2: INNER_TURRET = 3
			elif red_top2 and red_mid2 and red_bot2: INNER_TURRET = 4
			elif red_top2 and not red_mid2 and red_bot2: INNER_TURRET = 5
			elif not red_top2 and red_mid2 and not red_bot2: INNER_TURRET = 6
			elif red_top2 and red_mid2 and not red_bot2: INNER_TURRET = 7
			elif red_top2 and not red_mid2 and not red_bot2: INNER_TURRET = 8

			if not red_top1 and not red_mid1 and not red_bot1: BASE_TURRET = 1
			elif not red_top1 and not red_mid1 and red_bot1: BASE_TURRET = 2
			elif not red_top1 and red_mid1 and red_bot1: BASE_TURRET = 3
			elif red_top1 and red_mid1 and red_bot1: BASE_TURRET = 4
			elif red_top1 and not red_mid1 and red_bot1: BASE_TURRET = 5
			elif not red_top1 and red_mid1 and not red_bot1: BASE_TURRET = 6
			elif red_top1 and red_mid1 and not red_bot1: BASE_TURRET = 7
			elif red_top1 and not red_mid1 and not red_bot1: BASE_TURRET = 8

			if not red_topin and not red_midin and not red_botin: UNDEFINED_TURRET = 1
			elif not red_topin and not red_midin and red_botin: UNDEFINED_TURRET = 2
			elif not red_topin and red_midin and red_botin: UNDEFINED_TURRET = 3
			elif red_topin and red_midin and red_botin: UNDEFINED_TURRET = 4
			elif red_topin and not red_midin and red_botin: UNDEFINED_TURRET = 5
			elif not red_topin and red_midin and not red_botin: UNDEFINED_TURRET = 6
			elif red_topin and red_midin and not red_botin: UNDEFINED_TURRET = 7
			elif red_topin and not red_midin and not red_botin: UNDEFINED_TURRET = 8


			if not red_twin1 and not red_twin2: NEXUS_TURRET = 1
			elif not red_twin1 and red_twin2: NEXUS_TURRET = 2
			elif red_twin1 and not red_twin2: NEXUS_TURRET = 2
			elif red_twin1 and red_twin2: NEXUS_TURRET = 3
			predict_one = math.floor(obj.oneteam_model_predict(selected_team, red_baron, red_herald, OUTER_TURRET,
	                          INNER_TURRET, BASE_TURRET, UNDEFINED_TURRET, NEXUS_TURRET,
	                          red_air, red_water, red_earth, red_fire, red_elder)*100)
			if predict_one == 0:
				predict_one = 'No data'
			selected_team = 'RED'
			context ={'t':t,
						'selected_team':selected_team,
						'predict_one':predict_one,
						}
		elif selected_team == '300':
			print("two teams")
			if not top3 and not mid3 and not bot3: OUTER_TURRET = 1
			elif not top3 and not mid3 and bot3: OUTER_TURRET = 2
			elif not top3 and mid3 and bot3: OUTER_TURRET = 3
			elif top3 and mid3 and bot3: OUTER_TURRET = 4
			elif top3 and not mid3 and bot3: OUTER_TURRET = 5
			elif not top3 and mid3 and not bot3: OUTER_TURRET = 6
			elif top3 and mid3 and not bot3: OUTER_TURRET = 7
			elif top3 and not mid3 and not bot3: OUTER_TURRET = 8

			if not top2 and not mid2 and not bot2: INNER_TURRET = 1
			elif not top2 and not mid2 and bot2: INNER_TURRET = 2
			elif not top2 and mid2 and bot2: INNER_TURRET = 3
			elif top2 and mid2 and bot2: INNER_TURRET = 4
			elif top2 and not mid2 and bot2: INNER_TURRET = 5
			elif not top2 and mid2 and not bot2: INNER_TURRET = 6
			elif top2 and mid2 and not bot2: INNER_TURRET = 7
			elif top2 and not mid2 and not bot2: INNER_TURRET = 8

			if not top1 and not mid1 and not bot1: BASE_TURRET = 1
			elif not top1 and not mid1 and bot1: BASE_TURRET = 2
			elif not top1 and mid1 and bot1: BASE_TURRET = 3
			elif top1 and mid1 and bot1: BASE_TURRET = 4
			elif top1 and not mid1 and bot1: BASE_TURRET = 5
			elif not top1 and mid1 and not bot1: BASE_TURRET = 6
			elif top1 and mid1 and not bot1: BASE_TURRET = 7
			elif top1 and not mid1 and not bot1: BASE_TURRET = 8

			if not topin and not midin and not botin: UNDEFINED_TURRET = 1
			elif not topin and not midin and botin: UNDEFINED_TURRET = 2
			elif not topin and midin and botin: UNDEFINED_TURRET = 3
			elif topin and midin and botin: UNDEFINED_TURRET = 4
			elif topin and not midin and botin: UNDEFINED_TURRET = 5
			elif not topin and midin and not botin: UNDEFINED_TURRET = 6
			elif topin and midin and not botin: UNDEFINED_TURRET = 7
			elif topin and not midin and not botin: UNDEFINED_TURRET = 8

			if not twin1 and not twin2: NEXUS_TURRET = 1
			elif not twin1 and twin2: NEXUS_TURRET = 2
			elif twin1 and not twin2: NEXUS_TURRET = 2
			elif twin1 and twin2: NEXUS_TURRET = 3
			if not red_top3 and not red_mid3 and not red_bot3: OUTER_TURRET = 1
			elif not red_top3 and not red_mid3 and red_bot3: OUTER_TURRET = 2
			elif not red_top3 and red_mid3 and red_bot3: OUTER_TURRET = 3
			elif red_top3 and red_mid3 and red_bot3: OUTER_TURRET = 4
			elif red_top3 and not red_mid3 and red_bot3: OUTER_TURRET = 5
			elif not red_top3 and red_mid3 and not red_bot3: OUTER_TURRET = 6
			elif red_top3 and red_mid3 and not red_bot3: OUTER_TURRET = 7
			elif red_top3 and not red_mid3 and not red_bot3: OUTER_TURRET = 8

			if not red_top2 and not red_mid2 and not red_bot2: INNER_TURRET = 1
			elif not red_top2 and not red_mid2 and red_bot2: INNER_TURRET = 2
			elif not red_top2 and red_mid2 and red_bot2: INNER_TURRET = 3
			elif red_top2 and red_mid2 and red_bot2: INNER_TURRET = 4
			elif red_top2 and not red_mid2 and red_bot2: INNER_TURRET = 5
			elif not red_top2 and red_mid2 and not red_bot2: INNER_TURRET = 6
			elif red_top2 and red_mid2 and not red_bot2: INNER_TURRET = 7
			elif red_top2 and not red_mid2 and not red_bot2: INNER_TURRET = 8

			if not red_top1 and not red_mid1 and not red_bot1: BASE_TURRET = 1
			elif not red_top1 and not red_mid1 and red_bot1: BASE_TURRET = 2
			elif not red_top1 and red_mid1 and red_bot1: BASE_TURRET = 3
			elif red_top1 and red_mid1 and red_bot1: BASE_TURRET = 4
			elif red_top1 and not red_mid1 and red_bot1: BASE_TURRET = 5
			elif not red_top1 and red_mid1 and not red_bot1: BASE_TURRET = 6
			elif red_top1 and red_mid1 and not red_bot1: BASE_TURRET = 7
			elif red_top1 and not red_mid1 and not red_bot1: BASE_TURRET = 8

			if not red_topin and not red_midin and not red_botin: UNDEFINED_TURRET = 1
			elif not red_topin and not red_midin and red_botin: UNDEFINED_TURRET = 2
			elif not red_topin and red_midin and red_botin: UNDEFINED_TURRET = 3
			elif red_topin and red_midin and red_botin: UNDEFINED_TURRET = 4
			elif red_topin and not red_midin and red_botin: UNDEFINED_TURRET = 5
			elif not red_topin and red_midin and not red_botin: UNDEFINED_TURRET = 6
			elif red_topin and red_midin and not red_botin: UNDEFINED_TURRET = 7
			elif red_topin and not red_midin and not red_botin: UNDEFINED_TURRET = 8

			if not red_twin1 and not red_twin2: NEXUS_TURRET = 1
			elif not red_twin1 and red_twin2: NEXUS_TURRET = 2
			elif red_twin1 and not red_twin2: NEXUS_TURRET = 2
			elif red_twin1 and red_twin2: NEXUS_TURRET = 3
			
			predict_blue,predict_red = obj.twoteam_model_predict(100, red_baron, red_herald, OUTER_TURRET,
	                          INNER_TURRET, BASE_TURRET, UNDEFINED_TURRET, NEXUS_TURRET,
	                          red_air, red_water, red_earth, red_fire, red_elder, 200, red_baron, red_herald, OUTER_TURRET,
	                          INNER_TURRET, BASE_TURRET, UNDEFINED_TURRET, NEXUS_TURRET,
	                          red_air, red_water, red_earth, red_fire, red_elder)
			predict_blue = predict_blue*100
			predict_red = predict_red*100
			context ={'t':t,
						'selected_team':selected_team,
						'predict_blue':predict_blue,
						'predict_red':predict_red,
						'flag_predict' : flag_predict,
						}
		else:
			no_team = "팀을 선택해주세요!"
			context ={'t':t,
						'no_team': no_team,
					}
	elif t:
		context = {'t' : t}
	else:
		context = {'notier' : '티어를 선택하지 않았습니다!!'}
	return render(request, 'kugg/platinum_object_list.html', context)

def object_list(request):
	tier = request.GET.get('티어')

	if tier == '마스터' :
		context = {'tier' : tier}
		return render(request, 'kugg/platinum_object_list.html', context)
	
	else:
		context = {'notier' : '티어를 선택하지 않았습니다!!'}
		return render(request, 'kugg/object_list.html', context)


def get_best_counter(champion, role):
	with open("kugg/static/analysis_models/matchup.pkl", "rb") as file:
		df_matchup = pickle.load(file)
	df_matchup_temp = df_matchup[(df_matchup['matchup'].str.contains(champion)) & (df_matchup['position'] == role)]
	df_matchup_temp['champion'] = df_matchup_temp['matchup'].apply(lambda x: x.split(' vs ')[0] if x.split(' vs ')[1] == champion else x.split(' vs ')[1])
	df_matchup_temp['win rate'] = df_matchup['win rate']
	df_matchup_temp = df_matchup_temp.sort_values('win rate', ascending = False)
	#print('{} - {}의 카운터 챔피언:'.format(role, champion))
	df_matchup_temp=df_matchup_temp.drop_duplicates('champion',keep='first')
	#print(df_matchup_temp[['champion', 'total matches', 'win rate']].head())
	if (pd.isnull(df_matchup_temp.iloc[0,1])):
		print("no data")
	else:
		df_matchup_temp=df_matchup_temp[['champion', 'total matches', 'win rate']].head(5)
		df_matchup_temp.columns = ['champion', 'total matches', 'win_rate']
	# json_records = df_matchup_temp.reset_index().to_json(orient ='records')
	# counter = [] 
	# counter = json.loads(json_records)
	counter = df_to_json(df_matchup_temp)
	return counter



def get_win_rate(champion, opnt_champion, role):
	# df_win_rate_role = pd.read_csv('D:/KUGG/kugg/win_rate_role.csv')
	with open("kugg/static/analysis_models/matchup.pkl", "rb") as file:
		df_matchup = pickle.load(file)
	df_matchup_temp = df_matchup[(df_matchup['matchup'].str.contains(champion)) & (df_matchup['position'] == role)]
	df_matchup_temp['champion'] = df_matchup_temp['matchup'].apply(lambda x: x.split(' vs ')[0] if x.split(' vs ')[1] == champion else x.split(' vs ')[1])
	df_matchup_temp['win rate'] = df_matchup['win rate']
	df_matchup_temp = df_matchup_temp.sort_values('win rate', ascending = False)
	print('{} - {} vs {}의 승률:'.format(role, champion, opnt_champion))
	df_matchup_temp=df_matchup_temp.drop_duplicates('champion',keep='first')
	df_matchup_temp=df_matchup_temp[df_matchup_temp['champion']==opnt_champion]
	#     print(df_matchup_temp[['total matches', 'win rate']].head())
	try:
		return round(df_matchup_temp.iloc[0][3],1)
	except:
		return "no data"

def champ_rune(cid):
	df_rune=pd.read_csv("D:/KUGG/kugg/df/df_rune.csv")
	df_rune_id=pd.read_csv("D:/KUGG/kugg/df/rune.csv")
	champ_rune=[]
	df_rune_cnt_0=df_rune[df_rune['championID']==cid]['perk0'].value_counts()
	champ_rune.append(df_rune_id[df_rune_id['runeId']==df_rune_cnt_0.index[0]]['rune'].values[0])
	df_rune_cnt_1=df_rune[df_rune['championID']==cid]['perk1'].value_counts()
	champ_rune.append(df_rune_id[df_rune_id['runeId']==df_rune_cnt_1.index[0]]['rune'].values[0])
	df_rune_cnt_2=df_rune[df_rune['championID']==cid]['perk2'].value_counts()
	champ_rune.append(df_rune_id[df_rune_id['runeId']==df_rune_cnt_2.index[0]]['rune'].values[0])
	df_rune_cnt_3=df_rune[df_rune['championID']==cid]['perk3'].value_counts()
	champ_rune.append(df_rune_id[df_rune_id['runeId']==df_rune_cnt_3.index[0]]['rune'].values[0])
	df_rune_cnt_4=df_rune[df_rune['championID']==cid]['perk4'].value_counts()
	champ_rune.append(df_rune_id[df_rune_id['runeId']==df_rune_cnt_4.index[0]]['rune'].values[0])
	df_rune_cnt_5=df_rune[df_rune['championID']==cid]['perk5'].value_counts()
	champ_rune.append(df_rune_id[df_rune_id['runeId']==df_rune_cnt_5.index[0]]['rune'].values[0])
	return champ_rune

def champion_list(request):

	champ_df = pd.read_csv('D:/KUGG/kugg/df/Champ.csv')
	champ_df = champ_df[:-3]
	champ_list=list(champ_df['name'].values)
	
	context = {'champ_list' : champ_list}
	return render(request, 'kugg/champion_list.html', context)

def champion_analysis(request):
	line = request.GET.get('라인')
	tier = request.GET.get('티어')
	my_champ = request.GET.get('내챔피언')
	op_champ = request.GET.get('상대챔피언')

	champ_df = pd.read_csv('D:/KUGG/kugg/df/Champ.csv')
	my_champ_num = champ_df[champ_df['name']==my_champ]['champion'].tolist()[0]
	op_champ_num = champ_df[champ_df['name']==op_champ]['champion'].tolist()[0]

	item_df = pd.read_csv('D:/KUGG/kugg/df/item.csv')

	item0 = request.GET.get('item0')
	item1 = request.GET.get('item1')
	item2 = request.GET.get('item2')
	item3 = request.GET.get('item3')
	item4 = request.GET.get('item4')
	item5 = request.GET.get('item5')
	
	op_item0 = request.GET.get('op_item0')
	op_item1 = request.GET.get('op_item1')
	op_item2 = request.GET.get('op_item2')
	op_item3 = request.GET.get('op_item3')
	op_item4 = request.GET.get('op_item4')
	op_item5 = request.GET.get('op_item5')
	


	if my_champ or op_champ:
		flag = 1
		if not my_champ:
			my_champ = 0
		elif not op_champ:
			op_champ = 0
		if not item0:
			flag_item = 0
			item0 = 3111
		else:
			flag_item = 1
		#아이템트리 시뮬레이션
		with open("kugg/static/analysis_models/item_tree_test.pkl", "rb") as file:
			frame = pickle.load(file)
		frame=frame.to_frame().T

		pred={'tier':tier,'line':line,'championID':my_champ_num,'item0':item0,'item1':item1,'item2':item2,'item3':item3,'item4':item4,'item5':item5,'championID_opnt':op_champ_num,'item0_opnt':op_item0,'item1_opnt':op_item1,'item2_opnt':op_item2,'item3_opnt':op_item3,'item4_opnt':op_item4,'item5_opnt':op_item5}
		X_pred=pd.Series(pred)
		X_pred=X_pred.to_frame().T
		X_pred.drop(['tier','line'],axis='columns',inplace=True)
		X_pred=pd.get_dummies(data=X_pred,columns=['championID','championID_opnt','item0','item1','item2','item3','item4','item5','item0_opnt','item1_opnt','item2_opnt','item3_opnt','item4_opnt','item5_opnt'])
		
		X_test=pd.DataFrame(index=range(0,1),columns=[frame.columns])
		X_test.loc[0]=0
		for j in range(0,len(X_pred.columns)):
		    X_test.loc[0][X_pred.columns[j]]=1

		with open("kugg/static/analysis_models/item_tree.pkl", "rb") as file:
			rf = pickle.load(file)
		win_rate=rf.predict_proba(X_test)[0:,:]*100
		wr = win_rate[0][1]
		wr = round(wr,1)
		#아이템 번호->이름 변경
		item_list = [item0,item1,item2,item3,item4,item5]
		op_item_list = [op_item0,op_item1,op_item2,op_item3,op_item4,op_item5]

		item_name = []
		op_item_name = []
		for i,r in enumerate(item_df['itemId']):
			for item in item_list:
				if int(item) == r:
					print(item_df['name'][i])
					item_name.append(item_df['name'][i])
			for item in op_item_list:
				if int(item) == r:
					op_item_name.append(item_df['name'][i])

		my_item_df = pd.DataFrame(columns=['item0','item1','item2','item3','item4','item5','item0name','item1name','item2name','item3name','item4name','item5name'])
		op_item_df = pd.DataFrame(columns=['item0','item1','item2','item3','item4','item5','item0name','item1name','item2name','item3name','item4name','item5name'])
		my_item_df.loc[0] = item_list+item_name
		op_item_df.loc[0] = op_item_list+op_item_name

		my_item = df_to_json(my_item_df)
		# json_records = op_item_df.reset_index().to_json(orient ='records')
		# op_item = [] 
		# op_item = json.loads(json_records)
		op_item = df_to_json(op_item_df)
		# print(item_name)
		# print(op_item_name)
		# with open("D:/KUGG/kugg/win_rate.pkl", "rb") as file:
		# 	df_win_rate_role = pickle.load(file)
		# df_position = df_win_rate_role.loc[my_champ]
		# json_records = df_position.reset_index().to_json(orient ='records')
		# position_win_rate = [] 
		# position_win_rate = json.loads(json_records)

		# print(type(line))
		# print(line)
		relative_wr = get_win_rate(my_champ,op_champ,line)
		
		counter = get_best_counter(my_champ, line)

		item_tree = get_item_tree(my_champ_num)

		rune_tree = champ_rune(my_champ_num)

		context = {'tier' : tier,
					'line' : line,
					'flag' : flag,
					'my_champ' : my_champ,
					'op_champ' : op_champ,
					'item_win_rate' : wr,
					'my_item' : my_item,
					'op_item' : op_item,
					'counter' : counter,
					'item_tree' : item_tree,
					'my_champ_num' : my_champ_num,
					'relative_wr' : relative_wr,
					'flag_item' : flag_item,
					'rune_tree' : rune_tree,
					}
	else:
		context = {'error' : '챔피언을 선택해주세요!'}
	return render(request, 'kugg/champion_analysis.html', context)