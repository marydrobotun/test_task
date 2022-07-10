import requests
from bs4 import BeautifulSoup
import string

alphabets = {}

def process_one_page(url):
    article = requests.get(url)
    tree = BeautifulSoup(article.text, 'html.parser')
    animals = tree.find_all('ul')[2]
    for animal in animals.find_all('a'):
        #print(animal.get('title'))
        alphabets[animal.get('title')[0]] += 1
    for i in tree.find('div', id='mw-pages').find_all('a'):
        if i.text == 'Следующая страница':
            return 'https://ru.wikipedia.org/' + i.get('href')
    return None


for latin_letter in string.ascii_uppercase:
    alphabets[latin_letter] = 0
А = ord('А')
for cyrillic_letter in ''.join([chr(i) for i in range(А,А+32)]):
    alphabets[cyrillic_letter] = 0
alphabets[chr(1025)] = 0

url = 'https://ru.wikipedia.org/w/index.php?title=%D0%9A%D0%B0%D1%82%D0%B5%D0%B3%D0%BE%D1%80%D0%B8%D1%8F%3A%D0%96%D0%B8%D0%B2%D0%BE%D1%82%D0%BD%D1%8B%D0%B5_%D0%BF%D0%BE_%D0%B0%D0%BB%D1%84%D0%B0%D0%B2%D0%B8%D1%82%D1%83&from=%D0%90'

while True:
    if url:
        url = process_one_page(url)
    else:
        break


for i in alphabets.keys():
    print(i, ':', alphabets[i])