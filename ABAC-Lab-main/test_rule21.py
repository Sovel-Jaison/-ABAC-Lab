from core.myabac import parse_abac_file

policy_file = "DATASETS/edocument/edocument.abac"

users, resources, rules = parse_abac_file(policy_file)

# Rule 21 = index 20 because Python starts at 0
rule = rules.rules[20]

print("=" * 80)
print("RULE 21 DIRECT TEST")
print("=" * 80)

print("\nRule:")
print("Subject:", rule.sub_cond)
print("Resource:", rule.res_cond)
print("Actions:", rule.acts)
print("Constraints:", rule.cons)

matching_users = []
matching_resources = []

# Find users matching Rule 21 subject conditions
for uid, user in users.users.items():
    if (
        user.get_attribute("role") == "employee"
        and user.get_attribute("department") == "londonOfficeSales"
    ):
        matching_users.append(uid)

# Find resources matching Rule 21 resource conditions
for rid, resource in resources.resources.items():
    if resource.get_attribute("type") == "invoice":
        matching_resources.append(rid)

print("\nUsers matching Rule 21:", len(matching_users))
print("Invoice resources:", len(matching_resources))

print("\nSample matching users:")
for uid in matching_users[:10]:
    user = users.users[uid]
    print(
        uid,
        "| tenant =", user.get_attribute("tenant"),
        "| department =", user.get_attribute("department")
    )

print("\nSample invoice resources:")
for rid in matching_resources[:10]:
    resource = resources.resources[rid]
    print(
        rid,
        "| tenant =", resource.get_attribute("tenant"),
        "| department =", resource.get_attribute("department")
    )

print("\n" + "=" * 80)
print("DIRECT RULE EVALUATION")
print("=" * 80)

same_tenant = 0
cross_tenant = 0
examples = []

for uid in matching_users:
    user = users.users[uid]
    user_tenant = user.get_attribute("tenant")

    for rid in matching_resources:
        resource = resources.resources[rid]
        resource_tenant = resource.get_attribute("tenant")

        result = rule.evaluate(user, resource, "send")

        if result:

            if user_tenant == resource_tenant:
                same_tenant += 1
            else:
                cross_tenant += 1

                if len(examples) < 20:
                    examples.append(
                        f"{uid} ({user_tenant}) -> "
                        f"{rid} ({resource_tenant})"
                    )

print("Same-tenant Rule 21 permits:", same_tenant)
print("Cross-tenant Rule 21 permits:", cross_tenant)

print("\nCross-tenant examples:")

if examples:
    for x in examples:
        print(x)
else:
    print("NONE")