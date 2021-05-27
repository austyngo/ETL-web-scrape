# Extracting Data with Web Scraping
Creating dataset by navigating multiple pages to scrape data and load to SQL database

## [scrape_eth.py](https://github.com/austyngo/ETL-web-scrape/blob/master/scrape_eth.py)
This script navigates the entire website to scrape company, brand, and category information and creates a dataframe.

## [to_sql.py](https://github.com/austyngo/ETL-web-scrape/blob/master/to_sql.py)
This script separates the scraped dataframe into brand, company, and catagory tables and creates unique identifiers for each table. The tables are then loaded into an existing SQL database using SQLalchemy.

### Logging in to a site
Start a session.
```python
session_requests = requests.session()

login_url = "https://www.ethicalconsumer.org/"

result = session_requests.get(login_url)
tree = html.fromstring(result.text)

```
Set the log in credentials as variables and create the payload (dictionary storing credentials). Many sites will require hidden credentials to log in, which can be scraped in the source. For this site it looked like this:
```python
user = 'XXXXX'
password = 'XXXXX'
auth_token = list(set(tree.xpath("//input[@name='form_build_id']/@value")))[0]
auth_token2 = list(set(tree.xpath("//input[@name='form_id']/@value")))[0]

payload = {'name': user, 
          'pass': password,
          'form_build_id': auth_token,
          "form_id": auth_token2}
```
Post the payload to the site and navigate to the next page to scrape the data
```python
s = session_requests.post(login_url, data=payload)
r = session_requests.get(login_url)
soup = BeautifulSoup(r.text, 'html.parser')
```

### Navigating a site
In this example, there is a page for each category of brands.
```python
#create a list to store URLs
cat_link=[]
#search for tags containing text referencing catagory pages
ind = soup.find_all('a', class_='menu__link')
#iterate through the tags and append item to URL list with the hompage URL
for i in ind:
    cat_link.append('https://www.ethicalconsumer.org' + i['href']) 
```
With each page stored. We can now iterate through the URL list to scrape information.
```python
for cat in cat_link:
    req = session_requests.get(cat)
    sou = BeautifulSoup(req.text, 'html.parser')
    cat_name = sou.find('h1', class_='title')
```
