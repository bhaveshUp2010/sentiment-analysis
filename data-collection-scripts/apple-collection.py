import requests
from datetime import datetime
from db.connection import connect_to_db, execute_query, select_all, select_one


conn = connect_to_db()
cursor = conn.cursor()

base_url = "https://itunes.apple.com"

#niche pickup from db
row = select_one(cursor,"""
    SELECT id, term, last_offset
    FROM niches
    ORDER BY last_processed IS NOT NULL, last_processed
    LIMIT 1""")
niche_id, term, offset = row[0], row[1], row[2]


def get_apps(term, offset):
    url = f"{base_url}/search"
    params = {
        "term": term,
        "entity": "software",
        "limit": 20,
        "offset": offset
    }
    res = requests.get(url, params).json()
    return res["results"]

apps = get_apps(term, offset)

for app in apps:
    try:
        # print(app['trackId'], app['trackName'])
        execute_query(cursor, """
            insert into apps(app_id, app_name, niche_id)
             values (%s, %s, %s)
        """, (app['trackId'], app['trackName'], niche_id))
    except Exception as e:
        print("App insertion failed", e)

execute_query(cursor,"""
              update niches
               set last_offset = last_offset + 20
               where id = %s
              """, (niche_id,))

execute_query(cursor,"""
    UPDATE niches
    SET last_processed = NOW()
    WHERE id = %s
""", (niche_id,))


app_id = select_one(cursor,"""
    select app_id from
    apps where app_id
    not in (select distinct app_id from reviews)
    limit 1
""")[0]

def fetch_reviews(app_id, max_pages = 3):
    all_reviews = []
    for page in range(1, max_pages+1):
        url = f"{base_url}/rss/customerreviews/page={page}/id={app_id}/sortby=mostrecent/json"

        res = requests.get(url)
        data = res.json()
        
        if "entry" not in data["feed"]:
            break

        for r in data["feed"]["entry"][1:]:
            all_reviews.append({
                "text": r["content"]["label"],
                "rating": int(r["im:rating"]["label"]),
                "date": datetime.fromisoformat(r["updated"]["label"].replace("Z",""))
                })
            
    return all_reviews

reviews = fetch_reviews(app_id)

for r in reviews:
    try:
        # print(r)
        execute_query(cursor,"""
            INSERT INTO reviews (app_id, review_text, rating, review_date)
            VALUES (%s, %s, %s, %s)
        """, (app_id, r["text"], r["rating"], r["date"]))
    except Exception as e:
        print("review insertion failed", e)

print(f"Processed niche: {term}")
print(f"app id: {app_id}")
print(f"Inserted {len(reviews)} reviews")


conn.commit()
cursor.close()
conn.close()