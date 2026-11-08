from core.myabac import parse_abac_file

policy_file = "DATASETS/edocument/edocument.abac"

users, resources, rules = parse_abac_file(policy_file)

total = 0
same_tenant = 0
cross_tenant = 0

examples = []

for resource_id, resource in resources.resources.items():

    resource_tenant = resource.get_attribute("tenant")
    owner = resource.get_attribute("owner")

    if owner not in users.users:
        continue

    owner_tenant = users.users[owner].get_attribute("tenant")

    total += 1

    if owner_tenant == resource_tenant:
        same_tenant += 1
    else:
        cross_tenant += 1

        if len(examples) < 10:
            examples.append(
                f"{resource_id}: owner {owner} ({owner_tenant}) "
                f"-> resource tenant {resource_tenant}"
            )

print("=" * 60)
print("OWNER / TENANT ANALYSIS")
print("=" * 60)

print("Resources with valid owners:", total)
print("Same-tenant owners:", same_tenant)
print("Cross-tenant owners:", cross_tenant)

if total:
    print(
        "Cross-tenant percentage:",
        round(cross_tenant / total * 100, 2),
        "%"
    )

print("\nExamples:")

if examples:
    for x in examples:
        print(x)
else:
    print("NONE")