import requests
from flask import Flask, request, json
from app.mongodb import SessionDB
from app.json_processing import JsonProcessing


app = Flask(__name__)


@app.route('/')
def base():
    return json.jsonify({"Status": "UP"}), 200


@app.route('/books', methods=['GET'])
def get_books():
    mongo = SessionDB()
    response = mongo.load_books()

    if request.args:
        if 'sort' in request.args:
            if request.args['sort']:
                if request.args['sort'][0] != "-":
                    response = mongo.sort_books(request.args['sort'], False)
                else:
                    response = mongo.sort_books(request.args['sort'][1:], True)
        else:
            args = request.args
            lst = [{a: v} for a, v in args.items()]
            response = mongo.filter_books(lst)

        return json.jsonify(response), 200
    return json.jsonify(response), 200


@app.route('/books/<bookid>', methods=['GET'])
def get_book(bookid):
    mongo = SessionDB()
    response = mongo.load_book(bookid)
    if response == {}:
        return json.jsonify({"error": "the book with the given id does not exist"}), 400
    else:
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
        new_books = []
        replaced_books = []

        mongo = SessionDB()

        for book in parsed_book_list:
            if mongo.load_book(book['bookid']) == {}:
                new_books.append(book)
            else:
                mongo.delete_book(book['bookid'])
                replaced_books.append(book)

        mongo.insert_all(new_books + replaced_books)

        if len(new_books) != 0:
            if len(new_books) == len(parsed_book_list):
                return json.jsonify({"added books": len(new_books)}), 201
            else:
                return json.jsonify({"added books": len(new_books)}, {"replaced_books": len(replaced_books)}), 201
        else:
            return json.jsonify({"info": "the given data already exists in the database"}), 200
    else:
        return json.jsonify({"error": "the data sent is incorrect"}), 400
