class UsersDatabase:
    def __init__(self):
        self.database = {}

    def create_user(self, username, password):
        self.database[username] = password

    def get_password(self, username):
        try:
            return self.database[username]
        except KeyError:
            return None

    def set_password(self, username, password):
        self.database[username] = password

