import pickle
class Resource:
    def __init__(self, rid):
        self.attributes = {"rid": rid}

    def add_attribute(self, key, value):
        self.attributes[key] = value

    def get_attribute(self, key):
        return self.attributes.get(key)

    def get_name(self):
        return next(iter(self.attributes.values()))
    
    def get_attributes(self):
        return self.attributes

class ResourceManager:
    def __init__(self):
        self.resources = {}

    def parse_resource_attrib(self, line):
        content = line[line.find("(")+1:line.rfind(")")].strip()
        parts = content.split(",", 1)
        rid = parts[0].strip()
        resource = Resource(rid)

        if len(parts) > 1:
            attrs = parts[1].strip()
            for attr in attrs.split(","):
                key, value = attr.strip().split("=", 1)
                # Handle set values
                if value.startswith("{"):
                    value = set(value[1:-1].split())
                resource.add_attribute(key.strip(), value)

        self.resources[rid] = resource
        return resource

    def get_resource(self, rid):
        return self.resources.get(rid)

    def serialize(self, file_path):
        with open(file_path, 'wb') as file:
            pickle.dump(self.resources, file)

    def deserialize(self, file_path):
        with open(file_path, 'rb') as file:
            self.resources = pickle.load(file)