from pymongo import MongoClient
import os


class SessionDB:
    def __init__(self):
        MONGODB_URI = os.environ['MONGODB_URI']
        self.client = MongoClient(MONGODB_URI)
        self.database = self.client["library"]
        self.collection = self.database["books"]

    def load_books(self):
        books = self.collection.find()
        output = [{item: data[item] for item in data if item != '_id'} for data in books]
        return output

    def load_book(self, bookid):
        try:
            data = self.collection.find_one({"bookid": bookid})
            output = {item: data[item] for item in data if item != '_id'}
        except BaseException:
            output = {}
        return output

    def sort_books(self, data, dec):
        if not dec:
            sorted_books = self.collection.find().sort(data)
            output = [{item: data[item] for item in data if item != '_id'} for data in sorted_books]
        else:
            sorted_books = self.collection.find().sort(data, -1)
            output = [{item: data[item] for item in data if item != '_id'} for data in sorted_books]
        return output

    def filter_books(self, data):
        if len(data) == 1:
            filtered_books = self.collection.find(data[0])
        else:
            filtered_books = self.collection.find({"$and": data})

        output = [{item: data[item] for item in data if item != '_id'} for data in filtered_books]
        return output

    def insert_all(self, data):
        new_books_list = data
        self.collection.insert_many(new_books_list)
        output = {'Status': 'Successfully Inserted'}
        return output

    def delete_book(self, data):
        self.collection.delete_one({'bookid': data})
        output = data
        return output
