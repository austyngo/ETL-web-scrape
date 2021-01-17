from lxml import html
import requests
from bs4 import BeautifulSoup
import pandas as pd

# Start the session
session_requests = requests.session()

login_url = "https://www.ethicalconsumer.org/"

user = #XXXXX
password = #XXXXX

def main():
  session_requests = requests.session()

  result = session_requests.get(login_url)
  tree = html.fromstring(result.text)

  #enter hidden tokens - many sites will have hidden authetication tokens
  auth_token = list(set(tree.xpath("//input[@name='form_build_id']/@value")))[0]
  auth_token2 = list(set(tree.xpath("//input[@name='form_id']/@value")))[0]

  # Create the payload
  payload = {'name': user, 
          'pass': password,
          'form_build_id': auth_token,
          "form_id": auth_token2}

  # Post the payload to the site to log in
  s = session_requests.post(login_url, data=payload)

  # Navigate to the next page and scrape the data
  r = session_requests.get(login_url)

  soup = BeautifulSoup(r.text, 'html.parser')

  cat_link = []

  #open category links
  ind = soup.find_all('a', class_='menu__link')
  for i in ind:
    cat_link.append('https://www.ethicalconsumer.org' + i['href'])

  #create lists for each field to scrape
  brand, company, comp_link, category, rating = [], [], [], [], []
  env, people, animals, pol = [], [], [], []

  for cat in cat_link:
    req = session_requests.get(cat)
    sou = BeautifulSoup(req.text, 'html.parser')
    cat_name = sou.find('h1', class_='title')
    div = sou.find_all('div', class_='product-company')
    for d in div:
      br = d.find('h4')
      print(br.text)
      brand.append(br.text)
      comp = d.find('a')
      if comp is None:
        company.append(br.text)
        comp_link.append('NA')
      else:
        comp_url='https://www.ethicalconsumer.org' + comp['href'] #open company links
        print(comp_url)
        comp_link.append(comp_url)
        print(comp.text)
        company.append(comp.text)
      print(cat_name.text) 
      category.append(cat_name.text)
    
    score = sou.find_all('div', {'class': ['score good', 'score average', 'score bad']})
    for s in score:
      print(s.text)
      rating.append(s.text)

    #find and open links containing ethical information for each brand
    ul = sou.find_all('ul', class_='points lost')

    for u in ul:
      env_rate = u.find('a', {'title': 'View environment-related stories for this company'})
      if env_rate is None:
        env.append('NA')
      else:
        env_url = 'https://www.ethicalconsumer.org' + env_rate['href']
        env_req = session_requests.get(env_url)
        envsoup = BeautifulSoup(env_req.text, 'html.parser')
        envstory = envsoup.find_all('div', class_="field field--name-field-story-body field--type-text-with-summary field--label-hidden field--item")
        env_list = []
        for e in envstory:
          env_list.append(e.text)
        env.append('\b\b'.join(env_list))
        print('\b\b'.join(env_list)) 

      people_rate = u.find('a', {'title': 'View people-related stories for this company'})
      if people_rate is None:
        people.append('NA')
      else:
        people_url = 'https://www.ethicalconsumer.org' + people_rate['href']
        people_req = session_requests.get(people_url)
        peoplesoup = BeautifulSoup(people_req.text, 'html.parser')
        peoplestory = peoplesoup.find_all('div', class_="field field--name-field-story-body field--type-text-with-summary field--label-hidden field--item")
        people_list = []
        for e in peoplestory:
          people_list.append(e.text)
        people.append('\b\b'.join(people_list))
        print('\b\b'.join(people_list))

      animals_rate = u.find('a', {'title': 'View animals-related stories for this company'})
      if animals_rate is None:
        animals.append('NA')
      else:
        animals_url = 'https://www.ethicalconsumer.org' + animals_rate['href']
        animals_req = session_requests.get(animals_url)
        animalssoup = BeautifulSoup(animals_req.text, 'html.parser')
        animalsstory = animalssoup.find_all('div', class_="field field--name-field-story-body field--type-text-with-summary field--label-hidden field--item")
        animals_list = []
        for e in animalsstory:
          animals_list.append(e.text)
        animals.append('\b\b'.join(animals_list))
        print('\b\b'.join(animals_list))

      pol_rate = u.find('a', {'title': 'View politics-related stories for this company'})
      if pol_rate is None:
        pol.append('NA')
      else:
        pol_url = 'https://www.ethicalconsumer.org' + pol_rate['href']
        pol_req = session_requests.get(pol_url)
        polsoup = BeautifulSoup(pol_req.text, 'html.parser')
        polstory = polsoup.find_all('div', class_="field field--name-field-story-body field--type-text-with-summary field--label-hidden field--item")
        pol_list = []
        for e in polstory:
          pol_list.append(e.text)
        pol.append('\b\b'.join(pol_list))
        print('\b\b'.join(pol_list))

  #create dataframe from list store with scraped info
  df = pd.DataFrame({'Brand': brand, 'Company': company, 'Category': category, 'Rating': rating, 'Environment': env, 'People': people, 'Animals': animals, 'Politics': pol})

  return df

if __name__ == '__main__':
  data = main()
  data.to_csv('lumo_data.csv')