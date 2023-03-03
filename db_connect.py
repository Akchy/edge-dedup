import mysql.connector

# Creating connection object
db = mysql.connector.connect(
	host = "localhost",
	user = "root",
	password = "",
    database = "server"
)