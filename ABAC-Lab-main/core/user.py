import pickle
class User:
    def __init__(self, uid):
        self.attributes = {"uid": uid}

    def add_attribute(self, key, value):
        self.attributes[key] = value

    def get_attribute(self, key):
        return self.attributes.get(key)
    
    def get_attributes(self):
        return self.attributes

class UserManager:
    def __init__(self):
        self.users = {}

    def parse_user_attrib(self, line):
        # Remove userAttrib( and ) and split by commas
        content = line[line.find("(")+1:line.rfind(")")].strip()
        parts = content.split(",", 1)
        uid = parts[0].strip()
        user = User(uid)

        if len(parts) > 1:
            attrs = parts[1].strip()
            for attr in attrs.split(","):
                key, value = attr.strip().split("=", 1)
                # Handle set values
                if value.startswith("{"):
                    value = set(value[1:-1].split())
                user.add_attribute(key.strip(), value)

        self.users[uid] = user
        return user

    def get_user(self, uid):
        return self.users.get(uid)

    def serialize(self, file_path):
        with open(file_path, 'wb') as file:
            pickle.dump(self.users, file)

    def deserialize(self, file_path):
        with open(file_path, 'rb') as file:
            self.users = pickle.load(file)