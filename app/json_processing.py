import json
import jsonschema
from jsonschema import validate


class JsonProcessing:
    """
    A class to represent a data file JSON.
    """
    def __init__(self, json_content):
        self.json_content = json_content

    def validate(self):
        """
        Checks if the json file matches the pattern in the "schema.json" file.
        :param: JSON file
        :return: (bool) True or False
        """
        json_data = self.json_content

        with open('schema.json', 'r') as scheme:
            googleapis_schema = json.load(scheme)
        try:
            validate(instance=json_data, schema=googleapis_schema)
        except jsonschema.exceptions.ValidationError:
            return False
        return True

    def parse_and_extract(self):
        """
        Parse JSON content from www.googleapis.com/books/v1/volumes and extracts relevant data.
        :param: JSON content
        :return parsed_data: a list of volumes
        """
        list_of_volume_info = []
        for item in self.json_content['items']:
            auxiliary_list = []
            for info in item:
                if info == 'volumeInfo' or info == 'id':
                    auxiliary_list.append(item[info])

            auxiliary_list[1]['bookid'] = auxiliary_list[0]
            list_of_volume_info.append(auxiliary_list[1])

        searched_information = ["title", "authors", "published_date", "categories",
                                "average_rating", "ratings_count", "thumbnail", "bookid"]

        extracted_data = []
        for raw_information in list_of_volume_info:
            needed_info = {}
            for info in raw_information:

                if info in searched_information:
                    needed_info[info] = raw_information[info]
                elif info == "imageLinks":
                    needed_info["thumbnail"] = raw_information[info]["thumbnail"]
                elif info in ["publishedDate", "averageRating", "ratingsCount"]:
                    for char in info:
                        if char != char.lower():
                            needed_info[info.replace(char, "_"+char.lower())] = raw_information[info]

            extracted_data.append(needed_info)

        parsed_data = []
        for book in extracted_data:
            parsed_data.append(self.add_missing_info(book, searched_information))
        return parsed_data

    @staticmethod
    def add_missing_info(book_information, searched_information):
        """
        parse_and_extract() helper.
        """
        for info in searched_information:
            if info not in book_information:
                if info in ['average_rating', 'ratings_count']:
                    book_information[info] = None
                elif info in ['authors', 'categories']:
                    book_information[info] = []
                else:
                    book_information[info] = ""

        return book_information
