from pymongo import MongoClient

connector = MongoClient(
    'mongodb://anhphamduy:cuncun123@ds125362.mlab.com:25362/atschool')
db = connector.atschool
