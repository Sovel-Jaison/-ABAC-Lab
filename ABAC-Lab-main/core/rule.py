import pickle
class Rule:
    def __init__(self, sub_cond, res_cond, acts, cons):
        self.sub_cond = sub_cond  # Subject conditions
        self.res_cond = res_cond  # Resource conditions
        self.acts = acts  # Allowed actions
        self.cons = cons  # Constraints

    def get_attributes(self):
        user_attributes = {attr for attr, _, _ in self.sub_cond}  
        resource_attributes = {attr for attr, _, _ in self.res_cond}
        action = {attr for attr  in self.acts}
        constraints = {con for con in self.cons}
        # Add attributes from constraints
        for left_attr, op, right_attr in self.cons:
            if op in ("=", ">", "]", "["):
                user_attributes.add(left_attr)
                resource_attributes.add(right_attr)

        return {
            "user": user_attributes,
            "resource": resource_attributes,
            "acts": action,
            "constraints": constraints
        }


    def evaluate(self, user, resource, action):

        # Check if action is allowed
        if action not in self.acts:
            return False

        # Evaluate subject conditions
        for attr, op, value in self.sub_cond:
            user_val = user.get_attribute(attr)
            if user_val is None:
                return False
            if op == "[" and isinstance(value, set):
                if not isinstance(user_val, set) and user_val not in value:
                    return False
            elif op == "]" and isinstance(user_val, set):
                if value not in user_val:
                    return False

        # Evaluate resource conditions
        for attr, op, value in self.res_cond:
            res_val = resource.get_attribute(attr)
            if res_val is None:
                return False
            if op == "[" and isinstance(value, set):
                if not isinstance(res_val, set) and res_val not in value:
                    return False
            elif op == "]" and isinstance(res_val, set):
                if value not in res_val:
                    return False

        # Evaluate constraints
        for left_attr, op, right_attr in self.cons:
            user_val = user.get_attribute(left_attr)
            res_val = resource.get_attribute(right_attr)
            if user_val is None or res_val is None:
                return False

            if op == "=":
                if user_val != res_val:
                    return False
            elif op == ">":  # supseteq
                if not isinstance(user_val, set) or not user_val.issuperset(res_val):
                    return False
            elif op == "]":
                if not isinstance(user_val, set) or res_val not in user_val:
                    return False
            elif op == "[":
                if not isinstance(res_val, set) or user_val not in res_val:
                    return False

        return True



class RuleManager:
    def __init__(self):
        self.rules = []

    def parse_rule(self, line):
        content = line[line.find("(")+1:line.rfind(")")].strip()
        parts = content.split(";")

        # Parse subject conditions
        sub_cond = []
        if parts[0].strip():
            for cond in parts[0].strip().split(","):
                if "[" in cond:
                    attr, val = cond.split("[")
                    val = val.strip()
                    if val.startswith("{"):
                        val = set(val[1:-1].split())
                    sub_cond.append((attr.strip(), "[", val))
                elif "]" in cond:
                    attr, val = cond.split("]")
                    sub_cond.append((attr.strip(), "]", val.strip()))

        # Parse resource conditions
        res_cond = []
        if parts[1].strip():
            for cond in parts[1].strip().split(","):
                if "[" in cond:
                    attr, val = cond.split("[")
                    val = val.strip()
                    if val.startswith("{"):
                        val = set(val[1:-1].split())
                    res_cond.append((attr.strip(), "[", val))
                elif "]" in cond:
                    attr, val = cond.split("]")
                    res_cond.append((attr.strip(), "]", val.strip()))

        # Parse actions
        acts = set()
        if parts[2].strip():
            acts_str = parts[2].strip()
            if acts_str.startswith("{"):
                acts = set(acts_str[1:-1].split())
            else:
                acts = {acts_str}

        # Parse constraints
        cons = []
        if len(parts) > 3 and parts[3].strip():
            for const in parts[3].strip().split(","):
                if "=" in const:
                    left, right = const.split("=")
                    cons.append((left.strip(), "=", right.strip()))
                elif ">" in const:
                    left, right = const.split(">")
                    cons.append((left.strip(), ">", right.strip()))
                elif "]" in const:
                    left, right = const.split("]")
                    cons.append((left.strip(), "]", right.strip()))
                elif "[" in const:
                    left, right = const.split("[")
                    cons.append((left.strip(), "[", right.strip()))

        rule = Rule(sub_cond, res_cond, acts, cons)

        self.rules.append(rule)
        return rule

    def get_rule(self, index):
        """
        Retrieve a rule by its index.

        Args:
            index (int): The index of the rule to retrieve.

        Returns:
            Rule: The rule at the specified index.
        """
        if 0 <= index < len(self.rules):
            return self.rules[index]
        else:
            raise IndexError("Rule index out of range")
        
    def serialize(self, file_path):
        with open(file_path, 'wb') as file:
            pickle.dump(self.rules, file)

    def deserialize(self, file_path):
        with open(file_path, 'rb') as file:
            self.rules = pickle.load(file)