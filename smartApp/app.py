#!/usr/bin/env python
# -*- coding: utf-8 -*-
from flask import Flask, render_template, jsonify, request, redirect, url_for
from flask_restful import Resource, Api
import sqlite3
from sqlite3 import Error
from  urllib import urlopen
from random import *
import datetime

x = randint(1, 100)

#constant for database
DATABASE = "sqlite-autoconf-3230100/project"
SMS_EMAIL = "otcleantech@gmail.com"
PASSWORD = "P@$$w0rd123"
SENDER = "AUTO-HOME"
EMERGENCY_MSG = "Emergency, Temperature is at a critical level"

def create_connection(db_file):
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Error as e:
        print(e)

    return None

def select_all_temp(conn, startDate, endDate):
    cur = conn.cursor()
    print("connected")
    sql = 'SELECT * FROM temps'
    if startDate != "0" :
        sql = sql + " where tdate >= ?"
    if endDate != "0" :
        sql = sql + " and tdate <= ?"
    print(sql)

    cur.execute(sql, [startDate, endDate])
    print("executed")
    return cur.fetchall()

def save_sensor_data(conn, temperature, humidity):
    cur = conn.cursor()

    # insert new record inside temp table
    cur.execute("INSERT INTO temps VALUES (date('now'), time('now'),?,?)", [temperature, humidity])

    return conn.commit()

def get_recent_setting(conn):
    cur = conn.cursor()
    cur.execute('SELECT * FROM setting')
    return cur.fetchall()

def get_recent_temperature(conn):
    cur = conn.cursor()
    cur.execute('SELECT * FROM temps order by ROWID desc limit 1')
    return cur.fetchall()

def save_settings(conn, min_temp, max_temp, emergency_phone, emergency_email):
    cur = conn.cursor()
    #delete previous entries
    cur.execute('DELETE FROM setting')

    # insert new record inside table
    cur.execute('INSERT INTO setting values (?,?,?, ?)', [min_temp, max_temp, emergency_phone, emergency_email])

    return conn.commit()

#Method to send SMS incase of emergency_phone
def send_emergency_message(conn):
    cur = conn.cursor()
    # fetch emergency phone number
    cur.execute('SELECT email FROM setting order by ROWID desc limit 1')
    rows = cur.fetchall()

    for row in rows:
        phone_number = row[0]
    #
    # # call sms api
    #
    url = "https://api.africastalking.com/restless/send?message=" + EMERGENCY_MSG + "&username=tbasetest2018&Apikey=ceeabb27657cd6cfb3952dfae8b7943b4975dbee6a5b55fd4819f333bb1100ee&to=" + "+" + str(phone_number)
    #url= "https://www.smsgator.com/bulksms?email=" + SMS_EMAIL + "&password=" + PASSWORD + "&type=1&dlr=1&destination=" + "+" + str(phone_number) + "&sender=" + SENDER + "&message=" + EMERGENCY_MSG
    print(url)
    resp = urlopen(url)
    return resp.read()



# Making instance of Flask Class
app = Flask(__name__)


# Pinpoints the address
@app.route('/')
def index():
    # Render Templates
     return render_template("home.html")

@app.route('/home')
def home():
    # Render Templates
     return render_template("home.html")

@app.route('/about')
def about():
    # Render Templates
     return render_template("about.html")

@app.route('/plot')
def plot():
    return render_template("plot.html")

@app.route('/send_sms')
def send_sms():
    # create a database connection
    conn = create_connection(DATABASE)
    with conn:
        response = send_emergency_message(conn)
        print(response)


@app.route('/settings')
def settings():
    # create a database connection
    conn = create_connection(DATABASE)

    min_temp = 0
    max_temp = 0
    phone = ""
    email = ""

    with conn:
        print("Get last settings")
        #select_all_temp(conn)
        rows = get_recent_setting(conn)

    if rows:
        min_temp=rows[0][0]
        max_temp=rows[0][1]
        phone=rows[0][2]
        email=rows[0][3]


    return render_template("settings.html", min_temp=min_temp, max_temp=max_temp, email=email, phone=phone)

@app.route('/processSettings', methods = ['POST', 'GET'])
def saveSettings():

    # get inputs from form

    min_temperature = request.form['min_temperature']
    max_temperature = request.form['max_temperature']
    emergency_phone = request.form['emergency_phone']
    emergency_email = request.form['emergency_email']

    # create a database connection
    conn = create_connection(DATABASE)
    with conn:
        print("Sending settings across...")
        #select_all_temp(conn)
        rows = save_settings(conn, min_temperature, max_temperature, emergency_phone, emergency_email)

    #return render_template("settings.html", )
    return redirect(url_for('settings'))

@app.route('/api/post_reading', methods=["GET"])
def post_reading():
    # get post params
    temperature = request.args.get('temperature')
    humidity = request.args.get('humidity')

    print(temperature, humidity)

    # create a database connection
    conn = create_connection(DATABASE)
    with conn:
        print("posting data from sensor")
        #select_all_temp(conn)
        save_sensor_data(conn, temperature, humidity)
        
        # check if temperate is within acceptable settings
        settings = get_recent_setting(conn)

        if settings:
            min_temp = int(settings[0][0])
            max_temp = int(settings[0][1])
            
            if float(temperature) > max_temp:
                send_emergency_message(conn)
            if float(temperature) < min_temp:
                send_emergency_message(conn)

    return "Ok"


@app.route('/api/get_temp', methods=["GET", "POST"])
def temperature():

    # get url params
    startDate = request.args.get('start_date')
    endDate = request.args.get('end_date')

    # create a database connection
    conn = create_connection(DATABASE)
    with conn:
        print("2. Query all temps")
        #select_all_temp(conn)
        rows = select_all_temp(conn, startDate, endDate)

    # build data
    temp = []
    humid = []
    dates = []
    for row in rows:
        temp.append(row[2])
        humid.append(row[3])
        dates.append(row[0])

    return jsonify({'temperature': temp, 'humidity' : humid, 'categories' : dates})
    #return jsonify(rows)

@app.route('/Power')
def power():

    sys.exit(1);

@app.route("/Reading")
def lab_temp():
    # create a database connection
    conn = create_connection(DATABASE)

    temp = 0

    with conn:
        print("Get last temperature from database")
        #select_all_temp(conn)
        rows = get_recent_temperature(conn)

    if rows:
        temp=rows[0][2]
        
    print(temp)
        
    # Render Templates with conditional statements
    flame = False
    if temp is not None:
        return render_template("Reading.html", temp=temp, status_flame=flame)
    else:
        return render_template("No_sensor.html")

if __name__ == '__main__':
    app.run(debug=False)
#    app.run('0.0.0.0')
