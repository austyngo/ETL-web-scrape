import pandas as pd 
from sqlalchemy import create_engine

host = 'XXXX'
user = 'XXXX'
password = 'XXXX'
db = 'XXXX'

engine = create_engine(f"mysql+mysqlconnector://{user}:{password}@{host}/{db}", pool_pre_ping=True)

df = pd.read_csv(r"data.csv")
df['Category'] = df['Category'].str.lstrip().str.rstrip() #scraped data contained some whitespace

def new_table(column, df=df):
    table = df[[f'{column}', 'Rating']]
    tb_grp = table.groupby(f'{column}').mean().reset_index() #create average rating values for categories and companies
    tb_grp[f'{column}id'] = tb_grp.index #create unique IDs for each table using grouped index
    tb_grp['Rating'] = tb_grp['Rating'].round(2)
    return tb_grp

df_companies = new_table('Company')
df_categories = new_table('Category')

#add foreign keys to original brand table linking to new tables
df = df.join(df_categories[['Category', 'Categoryid']].set_index('Category'), on= 'Category') 
df = df.join(df_companies[['Company', 'Companyid']].set_index('Company'), on= 'Company')

df_companies = df_companies.set_index('Companyid')
df_categories = df_categories.set_index('Categoryid')

df = df.drop(['Unnamed: 0', 'Category', 'Company'], axis=1) #drop category and company names from brand table
df['brandid'] = df.index 
df = df.set_index('brandid')

#load tables to database
df_companies.to_sql(con=engine, name='companies', if_exists='append')
df_categories.to_sql(con=engine, name='categories', if_exists='append')
df.to_sql(con=engine, name='brands', if_exists='append')

print('Success!')