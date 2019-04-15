from bs4 import BeautifulSoup
import mechanize
import numpy as np
import pandas as pd

class MonashWebsiteScraper:
    def __init__(self,username,password,roundNumbers=[]):
        self.url = "http://probabilistic-footy.monash.edu/~footy/tips.shtml"
        self.username = username
        self.password = password
        self.roundNumbers = roundNumbers

        #maps monash team names to my team codes. Changes abbreviations to your own ones        
        self.mappingMonashTeamToCode = {
            'Adelaide':'ADE', 'Brisbane':'BRL', 'Carlton':'CAR', 'Collingwood':'COL', 'Essendon':'ESS',
            'Fremantle':'FRE', 'Geelong':'GEE', 'Gold_Coast':'GCS', 'Hawthorn':'HAW', 'Melbourne':'MEL',
            'Kangaroos':'NTH', 'P_Adelaide':'PRT', 'Richmond':'RIC', 'St_Kilda':'STK', 'Sydney':'SYD',
            'W_Coast':'WCE', 'W_Bulldogs':'WBD', 'G_W_Sydney':'GWS'
        }

        self.roundsUpdated = []

    def updateTipsForSeason(self):
        self.getTipsForSeason()

        if len(self.roundNumbers) > 0:
            rounds = self.roundNumbers
        else:
            rounds = sorted(list(set(self.tipsForSeason['roundnumber'])))

        for roundNumber in rounds:
            if roundNumber != '0':

                try:
                    self.getTipsForRound(roundNumber)
                    self.updateTipsForRound(roundNumber)
                    self.roundsUpdated.append(roundNumber)
                except Exception as e:
                    print(e)
                    print('updating failed for round {}'.format(roundNumber))
            else:
                print('No rounds to update')

    def updateTipsForRound(self,roundNumber):
        self.restartBrowser('info',roundNumber)
        self.updateTipsProb()

        self.restartBrowser('normal',roundNumber)
        self.updateTipsNormal()

        self.restartBrowser('gauss',roundNumber)
        self.updateTipsGauss()
    
    def restartBrowser(self,compType,roundNumber):
        
        self.br = mechanize.Browser()
        self.br.set_handle_robots(False) # ignore robots
        self.br.open(self.url)
        self.br.select_form(method="POST")
        
        self.br["name"] = self.username
        self.br["passwd"] = self.password
        self.br["comp"] = [compType]
        self.br["round"] = [str(int(roundNumber))]
        self.res = self.br.submit()
        self.content = self.res.read()
        self.soup = BeautifulSoup(self.content, "lxml")
        self.br.select_form(method="post")
        
    def getTipsForSeason(self):
        #should make a dataframe with columns:
        #df = dataframe with columns: roundnumber, predictedwinner, probability, marginpredict, stdevMarginPredict
        
        self.tipsForSeason = df
        
    def getTipsForRound(self,roundNumber):
        self.tipsForRound = self.tipsForSeason.query('roundnumber==@roundNumber')
    
    def updateTipsProb(self):
        
        rows = self.soup.findAll('table',{"align" : "center"})[0].findAll('tr')

        for row in rows[1:]:

            cells = row.findAll('td')
            teamOptions = [cell for cell in cells if cell.text.replace('\n','') in self.mappingMonashTeamToCode.keys()]
            
            inputProbabilityName = row.findAll('input',{'type':'text'})[0].attrs['name']

            for team in teamOptions:
                teamCode = self.mappingMonashTeamToCode[team.text.replace('\n','')]
                if teamCode in list(self.tipsForRound['predictedwinner']):
                    inputWinnerName = team.findAll('input')[0].attrs['name']
                    inputWinnerValue = team.findAll('input')[0].attrs['value']
                    inputProbabilityValue = str(self.tipsForRound.query('predictedwinner==@teamCode')['probability'].iloc[0]/100)
                    self.br.form.set_value([inputWinnerValue],name=inputWinnerName)
                    self.br.form.set_value(inputProbabilityValue,name=inputProbabilityName)
                    break
        
        self.br.submit()
    
    def updateTipsNormal(self):
        rows = self.soup.findAll('table',{"align" : "center"})[0].findAll('tr')

        for row in rows[1:]:

            cells = row.findAll('td')
            teamOptions = [cell for cell in cells if cell.text.replace('\n','') in self.mappingMonashTeamToCode.keys()]

            inputMarginName = row.findAll('input',{'type':'text'})[0].attrs['name']

            for team in teamOptions:
                teamCode = self.mappingMonashTeamToCode[team.text.replace('\n','')]
                if teamCode in list(self.tipsForRound['predictedwinner']):
                    inputWinnerName = team.findAll('input')[0].attrs['name']
                    inputWinnerValue = team.findAll('input')[0].attrs['value']
                    inputMarginValue = str(round(self.tipsForRound.query('predictedwinner==@teamCode')['marginpredict'].iloc[0]))
                    self.br.form.set_value([inputWinnerValue],name=inputWinnerName)
                    self.br.form.set_value(inputMarginValue,name=inputMarginName)
                    break
        
        self.br.submit()
    
    def updateTipsGauss(self):
        rows = self.soup.findAll('table',{"align" : "center"})[0].findAll('tr')

        for row in rows[1:]:

            cells = row.findAll('td')
            teamOptions = [cell for cell in cells if cell.text.replace('\n','') in self.mappingMonashTeamToCode.keys()]

            inputs = row.findAll('input',{'type':'text'})
            for inputObject in inputs:
                if 'margin' in inputObject.attrs['name']:
                    inputMarginName = inputObject.attrs['name']
                elif 'std' in inputObject.attrs['name']:
                    inputStdName = inputObject.attrs['name']

            for team in teamOptions:
                teamCode = self.mappingMonashTeamToCode[team.text.replace('\n','')]
                if teamCode in list(self.tipsForRound['predictedwinner']):
                    inputWinnerName = team.findAll('input')[0].attrs['name']
                    inputWinnerValue = team.findAll('input')[0].attrs['value']
                    inputMarginValue = str((self.tipsForRound.query('predictedwinner==@teamCode')['marginpredict'].iloc[0]))
                    inputStdValue = str((self.tipsForRound.query('predictedwinner==@teamCode')['stdevmarginpredict'].iloc[0]))
                    self.br.form.set_value([inputWinnerValue],name=inputWinnerName)
                    self.br.form.set_value(inputMarginValue,name=inputMarginName)
                    self.br.form.set_value(inputStdValue,name=inputStdName)
                    break

        self.br.submit()
