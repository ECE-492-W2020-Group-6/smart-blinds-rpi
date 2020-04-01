'''
Simple script to reset the databse. 

Author: Alex (Yin) Chen
Creation Date: February 1, 2020
'''

from piserver.app import db 

if __name__ == "__main__":
    db.drop_all()
    db.create_all()
