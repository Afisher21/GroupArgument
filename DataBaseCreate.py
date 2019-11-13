#!python3
# DatabaseCreate.py
from bs4 import BeautifulSoup
f = open("questions.html",'rt',encoding="utf8")
soup = BeautifulSoup(f, features='html.parser')

games = soup.find_all('div',{'class':'full module moduleTable'})

DataBase = {}
for game in games:
    prompt = game.h2.contents[0]
    responsedata = []
    for td in game.div.table.tbody:
        temp = td.get_text()
        parts = temp.split('\n')
        responsedata.append((parts[0].strip(), parts[1].strip()))
    DataBase[prompt] = responsedata
    
f2 = open("DataBase.py", 'w+')
f2.write('# db follows the form {"Prompt":[("Response","count"),("Response","Count")],...}\n\n')
f2.write('db = {\n')
keys = list(DataBase.keys())
for index in range(len(keys)):
    if index is 0:
        f2.write('\t""" ')
    else:
        f2.write(',\n\t""" ')
    f2.write(keys[index] +' """:' + str(DataBase[keys[index]]))
f2.write('\n}')
#f2.write(str(DataBase))
f2.close()

# (alt)
