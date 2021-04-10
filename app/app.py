import requests
from flask import Flask, request, json
from mongodb import SessionDB
from json_processing import JsonProcessing


app = Flask(__name__)


@app.route('/')
def base():
    return json.jsonify({"Status": "UP"}), 200


@app.route('/mongodb', methods=['GET'])
def get_books():
    mongo = SessionDB()
    response = mongo.load_books()

    if request.args:
        if request.args['sort']:
            if request.args['sort'][0] != "-":
                response = mongo.sort_books(request.args['sort'], False)
            else:
                response = mongo.sort_books(request.args['sort'][1:], True)
        #todo filtr
    return json.jsonify(response), 200


@app.route('/mongodb/<bookid>', methods=['GET'])
def get_book(bookid):
    mongo = SessionDB()
    response = mongo.load_book(bookid)
    return json.jsonify(response), 200


@app.route('/db', methods=['POST'])
def add_books():
    data = request.json
    if 'q' not in data:
        return json.jsonify({"error": "the data sent is incorrect"}), 400

    q = request.json['q']
    resposne = requests.get(f'https://www.googleapis.com/books/v1/volumes?q={q}')
    raw_books_data = JsonProcessing(resposne.json())

    if raw_books_data.validate():
        parsed_book_list = raw_books_data.parse_and_extract()
        mongo = SessionDB()
        response = mongo.save_all(parsed_book_list)
        return json.jsonify(response), 201
    else:
        return json.jsonify({"error": "the data sent is incorrect"}), 400




# if __name__ == '__main__':
#     app.run(debug=True, port=5000, host='0.0.0.0')