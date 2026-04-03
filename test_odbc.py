import platform
import subprocess

def is_mssql_driver_installed():
    """
    Checks if the Microsoft ODBC Driver for SQL Server is installed.
    Returns True if found, False otherwise.
    """
    # --- LAYER 1: The Python Check ---
    # First, we see if Python can actually see the driver.
    try:
        import pyodbc
        drivers = pyodbc.drivers()
        # Look for the modern drivers (e.g., "ODBC Driver 17 for SQL Server")
        if any("ODBC Driver" in d and "for SQL Server" in d for d in drivers):
            return True
        # Look for older native clients just in case
        if any("SQL Server Native Client" in d for d in drivers):
            return True
    except Exception:
        # If pyodbc throws an ImportError or OSError (like missing libodbc.so.2),
        # we catch it gracefully and move to the OS-level check.
        pass

    # --- LAYER 2: The OS-Level Pre-Flight Check ---
    system = platform.system()

    if system == "Windows":
        import winreg
        try:
            # Query the Windows Registry for installed ODBC Drivers
            reg_path = r"SOFTWARE\ODBC\ODBCINST.INI\ODBC Drivers"
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, reg_path) as key:
                # Loop through the registry keys to find SQL Server
                for i in range(winreg.QueryInfoKey(key)[1]):
                    name, value, _ = winreg.EnumValue(key, i)
                    if "ODBC Driver" in name and "for SQL Server" in name and value == "Installed":
                        return True
        except WindowsError:
            pass
            
    elif system in ["Darwin", "Linux"]: 
        # Darwin is macOS. Both Mac and Linux use unixODBC.
        try:
            # Run the unixODBC command to query installed drivers
            result = subprocess.run(["odbcinst", "-q", "-d"], capture_output=True, text=True)
            if "ODBC Driver" in result.stdout and "SQL Server" in result.stdout:
                return True
        except FileNotFoundError:
            # The 'odbcinst' command doesn't even exist, meaning unixODBC isn't installed
            pass

    return False

# --- Test the function ---
if __name__ == "__main__":
    if is_mssql_driver_installed():
        print("✅ MS-SQL ODBC Driver is installed and ready.")
    else:
        print("❌ MS-SQL ODBC Driver is MISSING.")