#Database
import psycopg2

try:
    connection = psycopg2.connect(user="postgres",
                                  password="admin",
                                  host="127.0.0.1",
                                  port="5432",
                                  database="prova")
    cursor = connection.cursor()

    postgreSQL_select_Query = "insert into film values (2, '2001: Odissea nello spazio', 'Stanley Kubrick', '1968-04-04');"    #immettere query qui
    cursor.execute(postgreSQL_select_Query)

    connection.commit()     #conferma e salva modifiche sul db
    
except (Exception, psycopg2.Error) as error:
    print("Error while fetching data from PostgreSQL", error)
finally:
    # closing database connection.
    if connection:
        cursor.close()
        connection.close()
        print("PostgreSQL connection is closed")
