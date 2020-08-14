import sqlite3

class DbMaster:

    def __init__(self, db_name):
        self.__db_name = db_name
        self.__connection = sqlite3.connect(db_name)
        self.__cursor = self.__connection.cursor()

    def create_db(self, table_name, col_names_types):
        col_names_str = ''
        for col_name_type in col_names_types:
            col_names_str += col_name_type + ' ' + col_names_types[col_name_type] + ','
        col_names_str = col_names_str[:-1]
        self.__cursor.execute('''CREATE TABLE ''' + str(table_name) +
             '''(''' + col_names_str + ''')''')
        self.__connection.commit()

    def insert_values(self, table_name, values):
        values_str = ''
        for value in values:
            values_str += '\'' + str(value) + '\' ,'
        values_str = values_str[:-1]
        self.__cursor.execute('''INSERT INTO ''' + table_name + ''' VALUES (''' + values_str + ''')''')
        self.__connection.commit()

    # def insert_value(self, table_name, columns, values):
    #     columns_str = ''
    #     for column in columns:
    def update(self, table_name, player_id, columns, values):
        set_values_str = ''
        for column, value in zip(columns, values):
            set_values_str += column + ' = ' + str(value) + ','
        set_values_str = set_values_str[:-1]
        self.__cursor.execute('''UPDATE ''' + table_name + ''' SET ''' + set_values_str + ''' WHERE player_number = ''' + str(player_id))
        self.__connection.commit()

    def __del__(self):
        self.__connection.close()
