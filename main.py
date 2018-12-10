from flask import Flask
# from aip import AipNlp
from Room import room
from api import *
import json
import math
import pygal

app = Flask(__name__, static_folder='./', static_url_path='', root_path='./')
sess, sentences, aspects, sentence_lens, sentence_locs, labels, dropout_keep_prob, predict_label = load_model()

@app.route('/')
def hello():
    return 'Hello, World!'

@app.route('/analysis/<text>/<Room>')
def Analysis(text, Room):
# Using baidu API
    # print("Link Start!")
    # APP_ID = '14600213'
    # API_KEY = 'eT1ao3lstG3R8o50gK904550'
    # SECRET_KEY = 'DLeA9yYGoQG7ocYoz7KNot7YWtseNFEG'
    # client = AipNlp(APP_ID, API_KEY, SECRET_KEY)
    # options = {}
    # options["type"] = 1 
    # result = client.commentTag(text, options)
    result = commentTag(text, sess, sentences, aspects, sentence_lens, sentence_locs, labels, dropout_keep_prob, predict_label)
    aspect = result["items"]

# Load the Room information
    f = open('Room_List.json', 'r')
    Room_List = json.load(f)
    f.close()
# Analyze the comment and update the data info
    temp = {}
    temp["Service"] = 0; temp["Location"] = 0; temp["Environment"] = 0; temp["Price"] = 0;

    for item in aspect:
        if item["prop"] == "服务":
            level = item["sentiment"]
            temp["Service"] = temp["Service"] + level - 1
            Room_List[Room]["Service"][level] = Room_List[Room]["Service"][level] + 1

        elif item["prop"] == "环境":
            level = item["sentiment"]
            temp["Environment"] = temp["Environment"] + level - 1
            Room_List[Room]["Environment"][level] = Room_List[Room]["Environment"][level] + 1   

        elif item["prop"] == "地点":
            level = item["sentiment"]
            temp["Location"] = temp["Location"] + level - 1
            Room_List[Room]["Location"][level] = Room_List[Room]["Location"][level] + 1

        elif item["prop"] == "性价比":
            level = item["sentiment"]
            temp["Price"] = temp["Price"] + level - 1
            Room_List[Room]["Price"][level] = Room_List[Room]["Price"][level] + 1

        else:
            level = item["sentiment"]
            Room_List[Room]["Others"][level] = Room_List[Room]["Others"][level] + 1

    # Write the Room data
    Temp = json.dumps(Room_List, sort_keys = True, ensure_ascii = False, indent = 2)
    File = open('Room_List.json', 'w')
    File.write(Temp)  
    File.close() 

    for i in temp:
        if temp[i] > 1:
            temp[i] = 1
        elif temp[i] < -1:
            temp[i] = -1

    line_chart = pygal.HorizontalBar(x_title = 'Level of Attitude')
    line_chart.title = 'The Analysis Result in Aspects'
    line_chart.add('Price', temp["Price"])
    line_chart.add('Environment', temp["Environment"])
    line_chart.add('Location', temp["Location"])
    line_chart.add('Service', temp["Service"])
    # line_chart.render_to_file('analysis.svg')
    return line_chart.render_response()


@app.route('/score/<Room>')
def Show_Grading(Room):
    # Load the Room information
    f = open('Room_List.json', 'r')
    Room_List = json.load(f)
    f.close()
    room_current = room(Room)
    room_current.Load(Room_List[Room])
    room_current.Calc_Grade()
    radar_chart = pygal.Radar(fill = True, range = (0,100))
    radar_chart.title = room_current.name + ' Grading'
    radar_chart.x_labels = ['Price', 'Environment', 'Location', 'Service', 'Others']
    radar_chart.add(room_current.name, [room_current.P_grade, room_current.E_grade, room_current.L_grade, room_current.S_grade, room_current.O_grade])
    return radar_chart.render_response()

@app.route('/comparison/<Room>/<Room_C>')
def Comparison(Room, Room_C):
    f = open('Room_List.json', 'r')
    Room_List = json.load(f)
    f.close()
    room_1= room(Room)
    room_1.Load(Room_List[Room])
    room_1.Calc_Grade()
    room_2= room(Room_C)
    room_2.Load(Room_List[Room_C])
    room_2.Calc_Grade()
    radar_chart = pygal.Radar(fill = True, range = (0,100))
    radar_chart.title = 'Grading Comparison'
    radar_chart.x_labels = ['Price', 'Environment', 'Location', 'Service', 'Others']
    radar_chart.add(room_1.name, [room_1.P_grade, room_1.E_grade, room_1.L_grade, room_1.S_grade, room_1.O_grade])
    radar_chart.add(room_2.name, [room_2.P_grade, room_2.E_grade, room_2.L_grade, room_2.S_grade, room_2.O_grade])
    return radar_chart.render_response()


if __name__ == '__main__': 
    text = "我觉得这个交通很差，离地铁站很远"
    Temp = commentTag(text, sess, sentences, aspects, sentence_lens, sentence_locs, labels, dropout_keep_prob, predict_label)
    print("Ready Go!")
    app.run(debug = True)
    