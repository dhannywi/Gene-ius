#!/usr/bin/env python3

import json
from flask import Flask, request, send_file
import redis
import requests
import yaml
import os
import matplotlib.pyplot as plt

app = Flask(__name__)
# rd = redis.Redis(host='redis-db', port=6379, db=0, decode_responses=True)
# rd_1 = redis.Redis(host='redis-db', port=6379, db=1)

redis_ip = os.environ.get('REDIS_IP')
if not redis_ip:
    raise Exception()
# initiate db tab 0 for storing data
rd = redis.Redis(host=redis_ip, port=6379, db=0, decode_responses=True)
# initiate db tab 1 for plotting
rd_1 = redis.Redis(host=redis_ip, port=6379, db=1)


# ---------------------------- Methods ---------------------------------
def get_config() -> dict:
    '''
    Function reads a configuration file and return the associated values, or return a default.
    Args:
        None
    Returns:
        result (dict): A dictionary containing configuration (default or custom).
    '''
    default_config = {"debug": True}
    try:
        with open('config.yaml', 'r') as f:
            return yaml.safe_load(f)
    except Exception as e:
        # print(f"Couldn't load the config file; details: {e}")
        return default_config

# ---------------------------- API routes ---------------------------------
@app.route('/data', methods=['POST', 'GET', 'DELETE'])
def hgnc_data() -> list:
    '''
    Function write/read/delete data stored in redis database depending on method requested.
    Returns list of nested dictionaries or status string.
    Returns:
        result (list): List of nested dictionaries of the HGNC data  for "GET" method,
                       or status info (string) for "POST" and "DELETE" method.
    '''
    if request.method == 'GET':
        if len(rd.keys()) == 0:
            return 'No data in db.\n'
        data = []
        for item in rd.keys():
            data.append(json.loads(rd.get(item)))
        return data

    elif request.method == 'POST':
        response = requests.get(url='https://ftp.ebi.ac.uk/pub/databases/genenames/hgnc/json/hgnc_complete_set.json')
        for item in response.json()['response']['docs']:
            rd.set(item.get('hgnc_id'), json.dumps(item))
        return 'Data loaded\n'
    
    elif request.method == 'DELETE':
        rd.flushdb()
        return f'Data deleted, there are {len(rd.keys())} keys in the db\n'
    
    else:
        return 'The method you tried does not exist.\n'

@app.route('/genes', methods=['GET'])
def get_hgnc_id() -> list:
    '''
    Function fetches data from db and return a list of all hgnc_id fields (set as keys in db).
    Returns:
        result (list): A list of hgnc_id
    '''
    if len(rd.keys()) == 0:
        return 'No data in db.\n'
    return rd.keys()

@app.route('/genes/<hgnc_id>', methods=['GET']) 
def get_gene_data(hgnc_id: str) -> dict:
    '''
    Given a string, this function retrieve data from database based on the requested hgnc_id.
    Returns a dictionary containing gene data for a given hgnc_id.
    Args:
        hgnc_id (str): A specific hgnc_id in the data set, requested by user.
    Returns:
        result (dict): Gene data for a specific hgnc_id from the database.
                       Returns an error message (str) in cases of invalid input or no data.
    '''
    if len(rd.keys()) == 0:
        return 'No data in db.\n'
    elif hgnc_id not in rd.keys():
        return 'hgnc_id requested is invalid.\n'
    else:
        return json.loads(rd.get(hgnc_id))


@app.route('/image', methods=['POST', 'GET', 'DELETE']) 
def get_image() -> str:
    '''
    Function write/read/delete plot image in redis database depending on method requested.
    Returns plot image.
    Returns:
        result (bytes): Plot image  for "GET" method,
                       or status info (string) for "POST" and "DELETE" method.
    '''
    if request.method == 'POST':
        if len(rd.keys()) == 0:
            return 'No data in db.\n'
        plot_data = {}
        for e in rd.keys():
            # check if key exist - add value by 1 if it exist, if not create new key and set value as 1
            key = json.loads(rd.get(e))['locus_group']
            if key in plot_data:
                plot_data[key] += 1
            else:
                plot_data[key] = 1
        # get key and value for plotting
        x = [i for i in plot_data.keys()]
        y = [i for i in plot_data.values()]
        # create barplot
        plt.bar(x, y, color ='lightblue', width = 0.4)
        plt.xlabel("locus group")
        plt.ylabel("count")
        plt.title("Number of registered genes per locus group")
        plt.savefig('./locus_grp.png')
        plt.show()
        # save to redis db
        file_bytes = open('./locus_grp.png', 'rb').read()
        rd_1.set('locus_plot', file_bytes)
        return 'Plot saved to db.\n'
        
    elif request.method == 'GET':
        if len(rd.keys()) == 0:
            return 'No data in db.\n'
        elif b'locus_plot' not in rd_1.keys():
            return 'Plot not in db, pls execute "POST" method to create plot.\n'
        # get plot image from db
        path = './locus_grp.png'
        with open(path, 'wb') as f:
            f.write(rd_1.get('locus_plot'))
        print('Fetching plot from db.\n')
        return send_file(path, mimetype='image/png', as_attachment=True)
    
    elif request.method == 'DELETE':
        # delete plot image from db
        rd_1.delete('locus_plot')
        return 'Plot deleted from db.\n'
    
    else:
        return 'The method you tried does not exist.\n'

# ---------------------------- Run App ---------------------------------
if __name__ == '__main__':    
    config = get_config()
    if config.get('debug', True):
        app.run(debug=True, host='0.0.0.0')
    else:
        app.run(host='0.0.0.0')

