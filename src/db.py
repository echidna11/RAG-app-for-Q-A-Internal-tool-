import mysql.connector
from mysql.connector import Error

class MySQLDatabase:
    def __init__(self, host, user, password, database):
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.connection = None

    def connect(self):
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database
            )
            if self.connection.is_connected():
                print("Connected to MySQL database")
        except Error as e:
            print("Error connecting to MySQL database:", e)

    def disconnect(self):
        if self.connection:
            self.connection.close()
            print("Disconnected from MySQL database")
    
    def new_user(self, email_id):
        try:
            cursor = self.connection.cursor()
            select_query = "SELECT * FROM users WHERE email = %s"
            cursor.execute(select_query, (email_id,))
            existing_user = cursor.fetchone()
            if existing_user:
                print("User already exists")
            else:
                insert_query = "INSERT INTO users (email, display_name) VALUES (%s, %s)"
                # Extracting user_name from email_id before the first '.'
                user_name = email_id.split('@')[0].split('.')[0]
                data = (email_id, user_name)
                cursor.execute(insert_query, data)
                self.connection.commit()
                print("New user created successfully")
        except Error as e:
            print("Error creating new user:", e)
        finally:
            cursor.close()


    def get_file_id(self, file_name, email):
        try:
            cursor = self.connection.cursor()

            # Retrieve the user_id using the email
            select_user_id_query = "SELECT user_id FROM users WHERE email = %s"
            cursor.execute(select_user_id_query, (email,))
            user_id = cursor.fetchone()[0]

            # Retrieve the file_id using the file name and user_id
            file_id_query = """
                SELECT file_id FROM files 
                JOIN collections ON files.collection_id = collections.collection_id 
                JOIN topics ON collections.topic_id = topics.topic_id 
                WHERE files.file_name = %s AND topics.user_id = %s
            """
            cursor.execute(file_id_query, (file_name, user_id))
            file_id = cursor.fetchone()[0]

            cursor.fetchall()  # Consume any remaining results

            return file_id
        except Exception as e:
            print("Error fetching file ID:", e)
            return None
        finally:
            cursor.close()


    def get_collection(self, email, topic_name):
        try:
            cursor = self.connection.cursor()

            # Retrieve the user_id using the email
            select_user_id_query = "SELECT user_id FROM users WHERE email = %s"
            cursor.execute(select_user_id_query, (email,))
            user_id = cursor.fetchone()[0]

            # Retrieve the topic_id using the topic name and user_id
            topic_id_query = "SELECT topic_id FROM topics WHERE topic_name = %s AND user_id = %s"
            cursor.execute(topic_id_query, (topic_name, user_id))
            topic_id = cursor.fetchone()[0]

            # Retrieve the collection name using the topic_id
            collection_query = "SELECT collection_name FROM collections WHERE topic_id = %s"
            cursor.execute(collection_query, (topic_id,))
            collection_name = cursor.fetchone()[0]

            return collection_name
        except Exception as e:
            print("Error fetching collection name:", e)
            return None
        finally:
            cursor.close()

    def add_topic(self, topic_name, email):
        try:
            cursor = self.connection.cursor()
            # Assuming there's a users table with an email column and a topics table with topic_name and user_id columns
            user_check_query = "SELECT user_id FROM users WHERE email = %s"
            cursor.execute(user_check_query, (email,))
            result = cursor.fetchone()
            if result:
                user_id = result[0]  # Accessing the first element of the result tuple which should be user_id
                # Inserting into the topics table
                insert_topic_query = "INSERT INTO topics (topic_name, user_id) VALUES (%s, %s)"
                cursor.execute(insert_topic_query, (topic_name, user_id))
                self.connection.commit()
                print("Topic added successfully")
                # Checking if the topic_id exists
                topic_id_query = "SELECT topic_id FROM topics WHERE topic_name = %s AND user_id = %s"
                cursor.execute(topic_id_query, (topic_name, user_id))
                topic_id = cursor.fetchone()[0]
                # Inserting into the collections table
                collections_count_query = "SELECT COUNT(*) FROM collections WHERE topic_id = %s"
                cursor.execute(collections_count_query, (topic_id,))
                collections_count = cursor.fetchone()[0] + 1  # Incrementing the count for the new collection
                collection_name = email.split("@")[0] + f"_{collections_count}_id"
                insert_collection_query = "INSERT INTO collections (collection_name, topic_id) VALUES (%s, %s)"
                cursor.execute(insert_collection_query, (collection_name, topic_id))
                self.connection.commit()
                print("Collection added successfully")
            else:
                print("User not found with email:", email)
        except Error as e:
            print("Error adding topic:", e)
        finally:
            cursor.close()


    def get_user_topics(self, email):
        try:
            cursor = self.connection.cursor()

            # Fetch user ID using email from the users table
            select_user_id_query = "SELECT user_id FROM users WHERE email = %s"
            cursor.execute(select_user_id_query, (email,))
            user_id = cursor.fetchone()[0]  # Assuming user_id is the first column in the result

            # Fetch topics using user_id from the topics table
            select_topics_query = "SELECT topic_name FROM topics WHERE user_id = %s"
            cursor.execute(select_topics_query, (user_id,))
            topics = cursor.fetchall()
            return [topic[0] for topic in topics]  # Extracting topic names from the result

        except Error as e:
            print("Error fetching user topics:", e)
        finally:
            cursor.close()

    def get_files_for_topic(self, topic_name, email):
        try:
            cursor = self.connection.cursor()

            # Get user ID
            select_user_id_query = "SELECT user_id FROM users WHERE email = %s"
            cursor.execute(select_user_id_query, (email,))
            user_id = cursor.fetchone()[0]

            # Get topic ID
            topic_id_query = "SELECT topic_id FROM topics WHERE topic_name = %s AND user_id = %s"
            cursor.execute(topic_id_query, (topic_name, user_id))
            topic_id = cursor.fetchone()[0]

            # Get collection ID
            collection_id_query = "SELECT collection_id FROM collections WHERE topic_id = %s"
            cursor.execute(collection_id_query, (topic_id,))
            collection_id = cursor.fetchone()[0]

            # Get files for the topic and collection
            files_query = "SELECT file_name, drive_URL FROM files WHERE collection_id = %s"
            cursor.execute(files_query, (collection_id,))
            files = cursor.fetchall()

            # Return the files information
            return files
        except Error as e:
            print("Error getting files for topic:", e)
            return []
        finally:
            cursor.close()

    def remove_file_from_topic(self, topic_name, file_name):
        try:
            cursor = self.connection.cursor()

            # Fetch collection_id for the given topic_name
            collection_id_query = "SELECT collections.collection_id FROM collections JOIN topics ON collections.topic_id = topics.topic_id WHERE topics.topic_name = %s"
            cursor.execute(collection_id_query, (topic_name,))
            collection_id = cursor.fetchone()[0]

            # Delete the file from the files table based on file_name and collection_id
            delete_file_query = "DELETE FROM files WHERE file_name = %s AND collection_id = %s"
            cursor.execute(delete_file_query, (file_name, collection_id))
            self.connection.commit()
            print("File removed successfully")
        except Error as e:
            print("Error removing file from topic:", e)
        finally:
            cursor.close()

    def add_file_to_topic(self, topic_name, email, file_name, file_path):
        try:
            cursor = self.connection.cursor()
            select_user_id_query = "SELECT user_id FROM users WHERE email = %s"
            cursor.execute(select_user_id_query, (email,))
            user_id = cursor.fetchone()[0]

            topic_id_query = "SELECT topic_id FROM topics WHERE topic_name = %s AND user_id = %s"
            cursor.execute(topic_id_query, (topic_name, user_id))
            topic_id = cursor.fetchone()[0]

            collection_id_query = "SELECT collection_id FROM collections WHERE topic_id = %s "
            cursor.execute(collection_id_query, (topic_id,))
            collection_id = cursor.fetchone()[0]

            insert_query = "INSERT INTO files (file_name, drive_URL, collection_id) VALUES (%s, %s, %s)"
            data = (file_name, file_path, collection_id)
            cursor.execute(insert_query, data)
            self.connection.commit()
            print("File added successfully")
        except Error as e:
            print("Error adding file:", e)
        finally:
            cursor.close()

    def get_user_id(self, email):
        user_id = None
        try:
            cursor = self.connection.cursor()
            select_user_id_query = "SELECT user_id FROM users WHERE email = %s"
            cursor.execute(select_user_id_query, (email,))
            row = cursor.fetchone()
            if row:
                user_id = row[0]
        except Error as e:
            print("Error fetching user ID:", e)
        finally:
            if cursor:
                cursor.close()
        return user_id

    def get_topic_id(self, user_id, topic_name):
        query = "SELECT topic_id FROM topics WHERE user_id = %s AND topic_name = %s"
        cursor = self.connection.cursor()
        cursor.execute(query, (user_id, topic_name))
        result = cursor.fetchone()  # Fetch one row from the result set
        topic_id = None
        if result:
            topic_id = result[0]  # Assuming the topic ID is in the first column of the result
        cursor.close()  # Close the cursor after processing the result
        return topic_id


    def insert_query(self, user_id, topic_id, query_text, response_text, created_at):
        try:
            cursor = self.connection.cursor()
            insert_query = "INSERT INTO user_interactions (user_id, topic_id, query, response, created_at) VALUES (%s, %s, %s, %s, %s)"
            data = (user_id, topic_id, query_text, response_text, created_at)
            cursor.execute(insert_query, data)
            self.connection.commit()
            print("Query inserted successfully")
        except Error as e:
            print("Error inserting query:", e)
        finally:
            cursor.close()
    
    def get_chat_messages(self, email, topic_name):
        try:
            cursor = self.connection.cursor()
            select_user_id_query = "SELECT user_id FROM users WHERE email = %s"
            cursor.execute(select_user_id_query, (email,))
            user_id = cursor.fetchone()[0]
            if user_id is not None:
                select_query = """
                    SELECT ui.query, ui.response, ui.created_at
                    FROM user_interactions ui
                    WHERE ui.user_id = %s AND ui.topic_id = (
                        SELECT topic_id FROM topics WHERE topic_name = %s
                    )
                    ORDER BY ui.created_at ASC
                """
                cursor.execute(select_query, (user_id, topic_name))
                chat_messages = cursor.fetchall()
                return chat_messages
            else:
                print("User not found with email:", email)
        except Exception as e:
            print("Error fetching chat messages:", e)
        finally:
            cursor.close()

    def insert_file(self, collection_id, file_name, drive_url):
        try:
            cursor = self.connection.cursor()
            insert_query = "INSERT INTO files (collection_id, file_name, drive_URL) VALUES (%s, %s, %s)"
            data = (collection_id, file_name, drive_url)
            cursor.execute(insert_query, data)
            self.connection.commit()
            print("File inserted successfully")
        except Error as e:
            print("Error inserting file:", e)
        finally:
            cursor.close()

    def remove_file(self, file_id):
        try:
            cursor = self.connection.cursor()
            # Check if the file exists
            check_query = "SELECT * FROM files WHERE file_id = %s"
            cursor.execute(check_query, (file_id,))
            file_data = cursor.fetchone()
            if not file_data:
                print("File not found.")
                return

            # Remove the file entry from the database
            delete_query = "DELETE FROM files WHERE file_id = %s"
            cursor.execute(delete_query, (file_id,))
            self.connection.commit()
            print("File removed successfully")
        except Error as e:
            print("Error removing file:", e)
        finally:
            cursor.close()



if __name__ == "__main__":
    db = MySQLDatabase(host='localhost', user='root', password='vikas123', database='mydatabase')
    db.connect()

    db.new_user("JohnDoe")

    db.add_topic("Topic 1", "JohnDoe")

    db.add_file("file.txt", 1)

    db.disconnect()
