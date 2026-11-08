from core.myabac import parse_abac_file, process_request

POLICY = "DATASETS\\edocument\\edocument.abac"

user_mgr, res_mgr, rule_mgr = parse_abac_file(POLICY)

actions = ["view", "send", "search", "readMetaInfo"]

total = 0
permits = 0
denies = 0

same_total = 0
same_permits = 0
same_denies = 0

cross_total = 0
cross_permits = 0
cross_denies = 0

cross_examples = []

for user_num in range(500):
    user_id = f"user{user_num}"
    user = user_mgr.get_user(user_id)

    if not user:
        continue

    user_tenant = user.attributes.get("tenant")

    for doc_num in range(300):
        resource_id = f"doc{doc_num}"
        resource = res_mgr.get_resource(resource_id)

        if not resource:
            continue

        resource_tenant = resource.attributes.get("tenant")

        same_tenant = user_tenant == resource_tenant

        for action in actions:
            total += 1

            request = f"{user_id},{resource_id},{action}"

            decision = process_request(
                request,
                user_mgr,
                res_mgr,
                rule_mgr
            )

            if decision == "Permit":
                permits += 1
            else:
                denies += 1

            if same_tenant:
                same_total += 1

                if decision == "Permit":
                    same_permits += 1
                else:
                    same_denies += 1

            else:
                cross_total += 1

                if decision == "Permit":
                    cross_permits += 1

                    if len(cross_examples) < 20:
                        cross_examples.append(
                            (
                                user_id,
                                user_tenant,
                                resource_id,
                                resource_tenant,
                                action
                            )
                        )
                else:
                    cross_denies += 1


print()
print("=" * 65)
print("E-DOCUMENT ABAC BASELINE ANALYSIS")
print("=" * 65)

print(f"Total requests tested        : {total}")
print(f"Total permits                : {permits}")
print(f"Total denies                 : {denies}")

print()
print("--- SAME-TENANT REQUESTS ---")
print(f"Same-tenant requests         : {same_total}")
print(f"Same-tenant permits          : {same_permits}")
print(f"Same-tenant denies           : {same_denies}")

print()
print("--- CROSS-TENANT REQUESTS ---")
print(f"Cross-tenant requests        : {cross_total}")
print(f"Cross-tenant permits         : {cross_permits}")
print(f"Cross-tenant denies          : {cross_denies}")

if cross_total > 0:
    print(
        f"Cross-tenant permit rate     : "
        f"{(cross_permits / cross_total) * 100:.4f}%"
    )

if permits > 0:
    print(
        f"Cross-tenant share of permits: "
        f"{(cross_permits / permits) * 100:.4f}%"
    )

print()
print("--- SAMPLE CROSS-TENANT PERMITS ---")

for example in cross_examples:
    user_id, user_tenant, resource_id, resource_tenant, action = example

    print(
        f"{user_id} ({user_tenant}) -> "
        f"{resource_id} ({resource_tenant}) : {action}"
    )

print()
print("=" * 65)
