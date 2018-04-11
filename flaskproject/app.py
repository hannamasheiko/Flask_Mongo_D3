from flask import Flask
from flask import render_template
from pymongo import MongoClient

from flaskproject.iso import COUNTRY_ISO_CODES

app = Flask(__name__)

client = MongoClient('mongodb://localhost:27017/')
db = client.world_bank


@app.route("/")
def hello():
    col_world = db.world
    data_collection = col_world.find()
    regions_id = []
    # discard data about the regions
    for d in data_collection:
        if d['countryshortname'] == d['regionname']:
            regions_id.append(d['_id'])
    clean_data = col_world.find({"_id": {"$nin": regions_id}})


    sum_proj_country = col_world.aggregate([
        {"$group": {"_id": {"countryshortname": "$countryshortname"}, "lendprojectcost": {"$sum": "$lendprojectcost"}}}
    ])

    country_and_cost = []
    total_projectcost_bycountry = []
    for z in sum_proj_country:
        country_and_cost.append({z['_id']['countryshortname']: {'Cost': z['lendprojectcost']}})
        total_projectcost_bycountry.append(z["lendprojectcost"])

    maxval = max(total_projectcost_bycountry)
    minval = min(total_projectcost_bycountry)

    transmitted_data = []
    # form the resulting list
    for s in clean_data:
        iso_country_code = COUNTRY_ISO_CODES.get(s['countrycode'], False)
        if iso_country_code:
            iso_code = iso_country_code
        else:
            continue
        project_name_and_cost = []
        country_by_code = col_world.find({"countrycode": s['countrycode']})
        total_cost = 0
        for item in country_by_code:
            total_cost += item['lendprojectcost']
            project_name_and_cost.append([item['project_name'], item['lendprojectcost']])
        transmitted_data.append({'Countrycode': iso_code,
                                 'Country': s['countryshortname'],
                                 'Projects': project_name_and_cost,
                                 'total_cost': total_cost})

    return render_template('index.html', transmitted_data=transmitted_data, maxval=maxval, minval=minval)


if __name__ == "__main__":
    app.run()
