import mysql.connector
class Inventory:
    def connect(self, query, values, write, col):
        """This function connects to the mySQL database, executing queries and returning True
        if the queries went through, and False if they did not. It can read and write to the
        database, storing any data in a data tuple."""
        try:
            connection = mysql.connector.connect(host='localhost',
                                              database = 'inventory',
                                              user = 'root',
                                              password = 'root')
            cursor = connection.cursor(buffered=True)
            if write:
                cursor.execute(query, values)
            else:
                cursor.execute(query)
                if col:
                    self.data = cursor.fetchall()
                else:
                    self.data = cursor.fetchone()
            print("balls")
            connection.commit()
            return True
        except mysql.connector.Error as error:
            print(f"Database error: {error}")
            cursor.close()
            connection.close()
            return False
    def addInventory(self, char_id):
        mysql_insert_row_query = "CREATE TABLE `%s` (Inventory VARCHAR(100), id INT PRIMARY KEY)"
        mysql_insert_row_values = (char_id,)
        self.connect(mysql_insert_row_query, mysql_insert_row_values, True, False)
        return