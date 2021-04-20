from lxml import html
import requests
from bs4 import BeautifulSoup
import pandas as pd

login_url = "https://www.ethicalconsumer.org/"

user = 'XXXX'
password = 'XXXX'

def session_():
  # Start the session
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

  return session_requests

def get_links(session):
  cat_link = []

  # Navigate to the next page and scrape the data
  r = session.get(login_url)
  soup = BeautifulSoup(r.text, 'html.parser')
  #open category links
  ind = soup.find_all('a', class_='menu__link')
  for i in ind:
    cat_link.append('https://www.ethicalconsumer.org' + i['href'])
  return cat_link

def get_info(links, session):
  brand, company, comp_link, category, rating = [], [], [], [], []
  env, people, animals, pol = [], [], [], []

  for cat in links:
    req = session.get(cat)
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

    fields = ['View environment-related stories for this company', 'View people-related stories for this company', 'View animals-related stories for this company', 'View politics-related stories for this company']

    for f, c in zip(fields,[env, people, animals, pol]):
      for u in ul:
        rate = u.find('a', {'title': f})
        if rate is None:
          env.append('NA')
        else:
          url = 'https://www.ethicalconsumer.org' + rate['href']
          req = session.get(url)
          envsoup = BeautifulSoup(req.text, 'html.parser')
          story = envsoup.find_all('div', class_="field field--name-field-story-body field--type-text-with-summary field--label-hidden field--item")
          r_list = []
          for s in story:
            r_list.append(s.text)
          c.append('\b\b'.join(r_list))
          print('\b\b'.join(r_list)) 

  #create dataframe from list store with scraped info
  df = pd.DataFrame({'Brand': brand, 'Company': company, 'Category': category, 'Rating': rating, 'Environment': env, 'People': people, 'Animals': animals, 'Politics': pol})

  return df

def main():
  site_session = session_()
  links = get_links(site_session)
  data = get_info(links, site_session)
  return data 

if __name__ == '__main__':
  data = main()
  data.to_csv('data.csv')