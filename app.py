from docker_sql_start import *
from data_generator import *
from test_odbc import *
from models import *
import sys

import pandas as pd
import random

def main():
    if not is_mssql_driver_installed():
        print("WARNING: MS-SQL ODBC Driver not detected.")
        print("The database connection will likely fail.")
        
        try:
            input("Press [ENTER] to continue anyway, or [CTRL+C] to cancel... ")
        except KeyboardInterrupt:
            print("\nCancelled by user.")
            sys.exit(1)

    print("Verifying MS-SQL Docker container...")
    if not verify_docker_sql():
        print("Failed to verify Docker SQL container. Aborting.")
        return False
    
    print("Initiating Data Generation...")
    if generate_data(rows=10000, overwrite=False) is False:
        print("Data generation failed. Aborting.")
        return False
    
    print("Initiating Model Training...")
    trained_models = run_training_pipeline()
    
    # Run the mass evaluation
    eval_models(trained_models)
    
    # Start the Web UI
    from server import start_server
    start_server(trained_models)

if __name__ == "__main__":
    main()