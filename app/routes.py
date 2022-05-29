from asyncio import open_connection
from concurrent.futures import process
import sqlite3
from os import abort
from flask import jsonify, redirect, request, send_from_directory
from itsdangerous import base64_decode
from app import app
#from app.ml.counting import get_walrus_count
#import numpy as np


DATABASE = './processing.db'



@app.route('/')
def get_root():
    return redirect('/index.html')


@app.route('/<path:path>')
def get_static(path):
    return send_from_directory('static', path)


@app.route('/walruses', methods = ['GET', 'POST'])
def start_task():
    if request.method == 'POST':
        model = request.get_json()
        if (model.animal != 'walrus'):
            return f'Unknown animal: {model.animal}', 400
        id = insert_new_image(model.img)       
        processed_image, walruses_count = 'PROCESSED_IMAGE', 143 #get_walrus_count(np.array(model.img))
        save_processed_image(id, walruses_count, processed_image)
        return jsonify({'img': processed_image, 'id': id, 'count': walruses_count})
    else:
        cursor = get_db_cursor()
        cursor.execute(f'select * from images')
        records = cursor.fetchall()
        cursor.close()
        return jsonify(records)        


@app.route('/walruses/<id>')
def get_image(id):
    record = get_image_record(id)
    if record is None:
        return 'Record not found', 404
    if record['is_processed'] == 0:
        return 'Record is not processed', 405
    return jsonify({'img': record['processed'], 'count': record['walruses_count']})


@app.route('/walruses/<id>/area/<center_x>/<center_y>')
def get_area_count(id, center_x, center_y):
    record = get_image_record(id)
    if record is None:
        return abort(404, 'Record not found')
    if record['is_processed'] == 0:
        return abort(405, 'Record is not processed')
    return 'Not implemented', 408
    


def get_image_record(id):
    cursor = get_db_cursor()
    cursor.execute(f'select * from images where id = {id}')
    record = cursor.fetchone()
    cursor.close()
    return record


def insert_new_image(img_base64):
    cursor = get_db_cursor()
    cursor.execute(f'insert into images (original) values({img_base64})')
    cursor.connection.commit()
    cursor.close()
    return cursor.lastrowid


def save_processed_image(id, count, img_base64):
    cursor = get_db_cursor()
    cursor.execute(f'update images set is_processed = 1, processed = {img_base64}, walruses_count = {count} where ID = {id}')
    cursor.connection.commit()
    cursor.close()


def get_db_cursor():
    return sqlite3.connect(DATABASE).cursor()

if __name__ == '__main__':
   app.run(debug = True)