import pandas as pd

df1 = pd.read_csv("~/data_projects/2020_05_05_myip_ms/test_run_16.csv", dtype=object, encoding="utf-8")
df2 = pd.read_csv("~/data_projects/2020_05_05_myip_ms/test_run_15.csv", dtype=object, encoding="utf-8")

df = pd.concat([df1, df2], axis="rows")

df.drop_duplicates(subset=['website'], inplace=True)


df = df[
    [ 
       
       
       u'website',
       u'website_popularity',
       u'world_site_popular_rating', 
       u'record_update_time', 
       u'dns_records', 
       #u'src',
       ]]

df.to_csv("~/data_projects/2020_05_05_myip_ms/full_run.csv", index=False, encoding="utf-8")