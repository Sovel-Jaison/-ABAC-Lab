from core.myabac import parse_abac_file

policy_file = "DATASETS/edocument/edocument.abac"

users, resources, rules = parse_abac_file(policy_file)

total = 0
same_tenant = 0
cross_tenant = 0

examples = []

for resource_id, resource in resources.resources.items():

    resource_tenant = resource.get_attribute("tenant")
    recipients = resource.get_attribute("recipients")

    if not recipients:
        continue

    for user_id in recipients:

        if user_id not in users.users:
            continue

        user = users.users[user_id]
        user_tenant = user.get_attribute("tenant")

        total += 1

        if user_tenant == resource_tenant:
            same_tenant += 1
        else:
            cross_tenant += 1

            if len(examples) < 20:
                examples.append(
                    f"{user_id} ({user_tenant}) -> "
                    f"{resource_id} ({resource_tenant})"
                )

print("=" * 60)
print("RECIPIENT / TENANT ANALYSIS")
print("=" * 60)

print("Total recipient-resource relationships:", total)
print("Same-tenant relationships:", same_tenant)
print("Cross-tenant relationships:", cross_tenant)

if total:
    print(
        "Cross-tenant percentage:",
        round((cross_tenant / total) * 100, 2),
        "%"
    )

print("\nCross-tenant examples:")

if examples:
    for example in examples:
        print(example)
else:
    print("NONE")
