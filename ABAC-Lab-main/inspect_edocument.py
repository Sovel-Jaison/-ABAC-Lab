from core.myabac import parse_abac_file

policy_file = "DATASETS/edocument/edocument.abac"

users, resources, rules = parse_abac_file(policy_file)

print("=" * 70)
print("E-DOCUMENT DATASET")
print("=" * 70)

print("\nUSER ATTRIBUTES")
print("-" * 70)

for user_id, user in list(users.users.items())[:5]:
    print(user_id)
    print(user.attributes)
    print()

print("\nRESOURCE ATTRIBUTES")
print("-" * 70)

for resource_id, resource in list(resources.resources.items())[:5]:
    print(resource_id)
    print(resource.attributes)
    print()

print("\nRULES")
print("-" * 70)

for i, rule in enumerate(rules.rules, 1):
    print(f"Rule {i}:")
    print(rule)
    print()