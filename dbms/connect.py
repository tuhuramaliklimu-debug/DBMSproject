import mysql.connector as MyConn

try:
    mydb = MyConn.connect(
        host="localhost",
        user="root",
        password="",      
        database="news_management",
        port=3306
    )
    cursor = mydb.cursor()
    cursor.execute("SELECT DATABASE();")
    result = cursor.fetchone()
    print("Connected to database:", result[0])

except MyConn.Error as e:
    print("Error while connecting:", e)

finally:
    if 'mydb' in locals() and mydb.is_connected():
        mydb.close()
        print("Connection closed.")
