import urllib.parse
from sqlalchemy import create_engine

def get_db_engine(server='localhost', database='master'):
    """
    Creates and returns a SQLAlchemy engine for the MS-SQL Docker container.
    """
    username = 'sa'
    raw_password = 'eKyhH>"UGj]W=bqT|t,VMF?<Qj"%ow£YS[;=!|i]GTjR_GqIpG'
    
    # URL-encode the password to handle special characters safely
    encoded_password = urllib.parse.quote_plus(raw_password)
    
    # Create the connection string using pyodbc
    connection_string = f"mssql+pyodbc://{username}:{encoded_password}@{server}/{database}?driver=ODBC+Driver+17+for+SQL+Server"
    
    return create_engine(connection_string)
