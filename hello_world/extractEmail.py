import json
from uploadFile import bucket_name
import boto3
import re
import pandas as pd
from sendToDb import sendToDb

def lambda_handler(event,context):

    try:
        body = json.loads(event["body"])
        object_name : str | None = body["file_name"]
        user_id : str | None = body["user_id"]
        
        if user_id is None or len(user_id) == 0:
            return {
          'statusCode': 200,
          'headers': {
            'Access-Control-Allow-Headers': '*',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'POST, GET'
            },
          'body': json.dumps('not found user')
          }
        
        print(object_name)

        if object_name is None or len(object_name) == 0:
            return {
          'statusCode': 200,
          'headers': {
            'Access-Control-Allow-Headers': '*',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'POST, GET'
            },
          'body': json.dumps('not found object')
          }


        s3 = boto3.client("s3")

        with open(f"/tmp/{object_name}","wb") as file:
            s3.download_fileobj(bucket_name,object_name,file)
        
        extract_excel(object_name,user_id)
        
        
        return {
          'statusCode': 200,
          'headers': {
            'Access-Control-Allow-Headers': '*',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'POST, GET'
            },
          'body': json.dumps('done!')
          }
            
    except Exception as e:
        
        print(str(e))
        return {
          'statusCode': 200,
          'headers': {
            'Access-Control-Allow-Headers': '*',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'POST, GET'
            },
          'body': json.dumps(str(e))
          }
        
        
    
chunk_size = 1024 * 1024

def extract_excel(file_name,  user_id : str) -> int | None:


    global chunk_size

    if user_id is None :

        raise ValueError("user email not found")

    company_names : list[str] = []
    names : list[str] = []
    emails : list[str] = []
    current_designation : list[str] = []

    file_extension = str(file_name).split(".")[-1]
    

    with open(f'/tmp/{file_name}','r') as f:
        print("reading file")
        df = None

        if file_extension == 'csv':
            df = pd.read_csv(f'/tmp/{file_name}')

        else :
            df = pd.read_excel(f'/tmp/{file_name}')

        df.fillna(value=str(''),inplace=True)

        if df is None or df.columns is None :
            raise Exception('DataFrame is empty')

        name_col : str | None = findNames(df.columns)

        if name_col is not None :
            name_row = df[f'{name_col}']
            for row in name_row:
                names.append(str(row))

        company_col : str | None = findCompanyName(df.columns)

        if company_col is not None :
            company_row = df[f'{company_col}']
            for row in company_row:
                company_names.append(str(row))

        email_col : str | None = findEmailName(df.columns)

        if email_col is None :
            raise Exception('No column containing emails found')

        else :
            email_row = df[f'{email_col}']

            for row in email_row :
                emails.append(verifyEmails(str(row)))
                
        cd_col : str | None = findCD(df.columns)
        
        if cd_col is not None:
            cd_row = df[f'{cd_col}']
            for row in cd_row:
                current_designation.append(str(row))

    if len(company_names) == 0 :
        company_names = ['' for _ in range(0,len(emails))]

    if len(names) == 0 :
        names = ['' for _ in range(0 , len(emails)) ]
    
    if len(current_designation) == 0:
        current_designation = ['' for _ in range(0,len(emails))]

    print(names)
    print(company_names)
    print(emails)
    print(current_designation)
    # await operations.insertEmails(emails,names,company_names,user_id)
    
    sendToDb(emails , names , company_names , current_designation , user_id)



def findNames(columns : list[str]) -> str | None:
    name_pattern = r'\b(?:name|names|username|usernames)\b'

    for col in columns :
        if re.match(name_pattern , col.lower().strip()) is not None :
            return col

    return None

def findCompanyName(columns : list[str]) -> str | None :

    company_pattern = r'\b(?:company|companies|company name|company_name|business|enterprise|firm|corporation|inc)\b'

    for col in columns :
        if re.match(company_pattern,col.lower().strip()) is not None:
            return col

    return None

def findEmailName(columns : list[str]) -> str | None :

    email_pattern = r'.*email.*'

    for col in columns :
        if re.match(email_pattern , col.lower().strip()) is not None :
            return col

    return None

def verifyEmails(email: str) -> str:
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

    if re.match(email_pattern, email) is not None:
        return email

    return ''

def findCD(columns : list[str]) -> str | None:
    name_pattern = r'\b(?:current designation|currentDesignation|post|rank)\b'

    for col in columns :
        if re.match(name_pattern , col.lower().strip()) is not None :
            return col

    return None
