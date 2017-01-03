import urllib
import BeautifulSoup
import csv
import pandas as pd
import re
from pandasql import sqldf


def processPage(urlLink):
    rawHtml = urllib.urlopen(urlLink).read()
    soup = BeautifulSoup.BeautifulSoup(rawHtml)
    return soup

def convertToFloat(string):
    if string == '':
        return ''
    else:
        return float(string)

def formatColumnName(col):
    newCol = col.lower().replace(' ', '_')

    checkInt = re.search('^[0-9]+', newCol)
    if checkInt:
        newCol = '_' + newCol + '_gdp_per_capita'

    return unicode(newCol)


#Extract 2016 Medal counts by country from Wikipedia
olyMedalsUrl = "https://en.wikipedia.org/wiki/2016_Summer_Olympics_medal_table"

olySoup = processPage(olyMedalsUrl)

tables = olySoup.findAll('table')
medalCountTable = tables[1]

rows = medalCountTable.findAll('tr')

medalTable = []
ukGold, ukSilver, ukBronze, ukTotal = 0, 0, 0, 0
medalHeaders = ['country', 'gold', 'silver', 'bronze', 'total']

for row in rows:

    if row.th.a:

        medals = row.th.findNextSiblings('td')
        
        #Combine Ireland and GBR as United Kingdom
        if row.th.a.string == 'Ireland' or row.th.a.string == 'Great Britain':

            ukGold += int(medals[0].string)
            ukSilver += int(medals[1].string)
            ukBronze += int(medals[2].string)
            ukTotal += int(medals[3].string)

        elif 'd\'Ivoire' in row.th.a.string:

            newRow = [unicode('Ivory Coast'), int(medals[0].string), int(medals[1].string), int(medals[2].string), int(medals[3].string)]
            medalTable.append(newRow)

        else:

            newRow = [unicode(row.th.a.string), int(medals[0].string), int(medals[1].string), int(medals[2].string), int(medals[3].string)]
            medalTable.append(newRow)

#append UK row
newRow = ['United Kingdom', ukGold, ukSilver, ukBronze, ukTotal]
medalTable.append(newRow)


#check medalTable for consistency
for row in medalTable:
    if row[0] == 'Country':
        continue
    if row[1] + row[2] + row[3] != row[4]:
        print "error with " + row[0]


#Read income per capita data from csv file (via WorldBank)
gdpTable = []
try:

    with open('data/GdpPerCapita.csv', 'r+') as csvfile:
        reader = csv.reader(csvfile)

        for row in reader:

            #Use header row as is (i.e. with string values)
            if row[0] == 'Country Name': 
                
                gdpHeaders = [formatColumnName(cell) for cell in row]
            
            #All other rows, convert numerical columns from string to float    
            else:
                #print unicode(row[0])
                newRow = []
                newRow.append(unicode(row[0]))
                newRow.append(unicode(row[1]))
                newRow.append(unicode(row[2]))
                newRow.append(unicode(row[3]))

                for i in range(4, len(row)):
                    newRow.append(convertToFloat(row[i]))

                gdpTable.append(newRow)

except Exception, e:
    print "Error in opening/reading file: ", e


#combine the datasources by querying dataframes
gdp_df = pd.DataFrame(gdpTable, columns=gdpHeaders)
medals_df = pd.DataFrame(medalTable, columns=medalHeaders)


#delete empty columns from gdp_df (no data yet for 2016)
del gdp_df['']
del gdp_df['_2016_gdp_per_capita']


#query to join datasources
query = """SELECT m.country as country,
                  m.gold as gold,
                  m.silver as silver,
                  m.bronze as bronze,
                  m.total as total,
                  g.country_name as country_name, 
                  g.country_code as country_code, 
                  g.indicator_name as indicator_name, 
                  g.indicator_code as indicator_code, 
                  round(g._2015_gdp_per_capita, 2) as _2015_gdp_per_capita
           FROM medals_df m
           LEFT JOIN gdp_df g
           ON m.country = g.country_name
           WHERE m.country NOT IN (\'Independent Olympic Athletes\', \'Chinese Taipei\')
        """

final_df = sqldf(query, locals())
print final_df

final_df.to_csv("d3data.csv")





