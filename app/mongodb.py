from bson import ObjectId
from pymongo import MongoClient
import os


class SessionDB:
    def __init__(self):
        DATABASE_URI = os.environ['DATABASE_URI']
        self.client = MongoClient(DATABASE_URI)
        self.database = self.client["library"]
        self.collection = self.database["books"]


    def load_books(self):
        books = self.collection.find()
        output = []
        for book in books:
            elem = {}
            for item in book:
                if item == '_id':
                    elem[item] = str(book[item])
                else:
                    elem[item] = book[item]
            output.append(elem)
        return output

    def load_book(self, bookid):
        data = self.collection.find_one({"_id": ObjectId(bookid)})
        output = {item: data[item] for item in data if item != '_id'}
        return output

    def sort_books(self, data, dec):
        if not dec:
            sorted_books = self.collection.find().sort(data)
            output = [{item: data[item] for item in data if item != '_id'} for data in sorted_books]
        else:
            sorted_books = self.collection.find().sort(data, -1)
            output = [{item: data[item] for item in data if item != '_id'} for data in sorted_books]
        return output

    def save_all(self, data):
        newbookslist = data
        self.collection.insert_many(newbookslist)
        output = {'Status': 'Successfully Inserted'}
        return output

