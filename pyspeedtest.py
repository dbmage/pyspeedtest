#!/usr/bin/python3

import os
import sys
import json
import pymysql
from datetime import datetime
from subprocess import Popen, PIPE

dir_path = os.path.dirname(os.path.realpath(__file__))

try:
    config = json.loads(open("%s/config.json" % (dir_path)).read())
except Exception as e:
    print("Unable to open config file: %s" % ( e))
    sys.exit(1)

nowdt = datetime.now()
job = Popen(['speedtest -fjson'], shell=True, stdout=PIPE, stderr=PIPE)
stdout,stderr = job.communicate()
try:
    output = json.loads(stdout.decode('utf-8'))
    output['ping']['latency'] = int(round(output['ping']['latency'], 2))
except:
    output = {'timestamp' : nowdt.strftime("%Y-%m-%dT%I:%M:%SZ"), 'ping' : { 'latency' : 0 }, 'download' : { 'bytes' :0 }, 'upload' : { 'bytes' : 0}}

conn = pymysql.connect(
    host=config['sqlhost'],
    user=config['sqluser'],
    password=config['sqlpass'],
    db=config['sqldb']
)

try:
    cursor = conn.cursor()
    sql = "INSERT INTO %s VALUES (NULL, '%s', %f, %i, %i)" % (config['sqltable'], output['timestamp'], output['ping']['latency'], output['upload']['bytes'], output['download']['bytes'])
    cursor.execute(sql)
    conn.commit()
    conn.close()
except Exception as e:
    print("Unable to update DB %s: %s" % (config['sqldb'], e))
    sys.exit(1)

sys.exit(0)
