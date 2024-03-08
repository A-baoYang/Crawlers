import pyodbc

cnxn_str = ("Driver={SQL Server Native Client 11.0};"
            "Server=192.168.2.3,14330;"
            "Trusted_Connection=yes;")
cnxn = pyodbc.connect(cnxn_str)