from core.myabac import parse_abac_file, process_request

policy_file = "DATASETS/edocument/edocument.abac"

users, resources, rules = parse_abac_file(policy_file)

print("Users:", len(users.users))
print("Resources:", len(resources.resources))
print("Rules:", len(rules.rules))

actions = [
    "view",
    "send",
    "search",
    "readMetaInfo"
]

results = {}

for action in actions:
    count = 0
    examples = []

    for user_id, user in users.users.items():
        user_tenant = user.attributes.get("tenant")

        for resource_id, resource in resources.resources.items():
            resource_tenant = resource.attributes.get("tenant")

            if user_tenant != resource_tenant:

                request = f"{user_id}, {resource_id}, {action}"

                result = process_request(
                    request,
                    users,
                    resources,
                    rules
                )

                if result == "Permit":
                    count += 1

                    if len(examples) < 5:
                        examples.append(
                            f"{user_id} ({user_tenant}) -> "
                            f"{resource_id} ({resource_tenant})"
                        )

    results[action] = count

    print()
    print("Action:", action)
    print("Cross-tenant permits:", count)

    for example in examples:
        print("  ", example)

print()
print("========== SUMMARY ==========")

for action, count in results.items():
    print(f"{action}: {count}")