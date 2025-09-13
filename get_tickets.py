import configparser
from fastapi import FastAPI,form
import json

config=configparser.ConfigParser()
config.read('config.properties')

app=FastAPI()
lang=config['']

"""Sample Scenario: 
A customer types: “Filter invoices for last month, vendor=‘IndiSky’, status=failed.” Then: “Why did these fail?” Assistant explains (e.g., “missing GSTIN in 7 files”) and offers: “Create a ticket and notify me when fixed.” Next day, customer returns—chat shows prior context, open ticket, and a new update; customer says “download the fixed report.”
What this tests: Do actions, explain context, create/track support, and continue the conversation across sessions with role-appropriate visibility.
"""
def Filter_data():
    user_id:int()
    status:str("Success")
    "vendor":
    user_query:""


async def get_filtered_tickets(query):
    mapping=json.read(role.json)
    print("First from the user request we will fetch user id-to get idea of role")#read role.json to map the role
    if query.user_id not in mapping.id:
        return "No such user Exist"
    else:
        #Check the role
        role_id=mapping.get_role()
        #based on different different filteration perform data retrival accordingly
        
    print('Get request of tickets accordingly will call database function here and return invoice data as per filter')




