from core.myabac import parse_abac_file, process_request

POLICY = "DATASETS\\edocument\\edocument.abac"

user_mgr, res_mgr, rule_mgr = parse_abac_file(POLICY)

actions = ["view", "send", "search", "readMetaInfo"]

total = 0

e1_permits = 0
e2_permits = 0

cross_total = 0
cross_e1_permits = 0
cross_e2_permits = 0
cross_blocked = 0

same_total = 0
same_e1_permits = 0
same_e2_permits = 0

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

            # E1: Original ABAC
            request = f"{user_id},{resource_id},{action}"

            e1_decision = process_request(
                request,
                user_mgr,
                res_mgr,
                rule_mgr
            )

            if e1_decision == "Permit":
                e1_permits += 1

            # E2: Tenant check + original ABAC
            if not same_tenant:
                e2_decision = "Deny"
            else:
                e2_decision = e1_decision

            if e2_decision == "Permit":
                e2_permits += 1

            # Classification
            if same_tenant:

                same_total += 1

                if e1_decision == "Permit":
                    same_e1_permits += 1

                if e2_decision == "Permit":
                    same_e2_permits += 1

            else:

                cross_total += 1

                if e1_decision == "Permit":
                    cross_e1_permits += 1

                    if e2_decision == "Deny":
                        cross_blocked += 1

                if e2_decision == "Permit":
                    cross_e2_permits += 1


print()
print("=" * 70)
print("E1 vs E2 TENANT-AWARE ABAC EXPERIMENT")
print("=" * 70)

print()
print("--- OVERALL ---")
print(f"Total requests tested        : {total}")
print(f"E1 original ABAC permits     : {e1_permits}")
print(f"E2 tenant-aware permits      : {e2_permits}")

print()
print("--- SAME-TENANT ---")
print(f"Same-tenant requests         : {same_total}")
print(f"E1 same-tenant permits       : {same_e1_permits}")
print(f"E2 same-tenant permits       : {same_e2_permits}")

print()
print("--- CROSS-TENANT ---")
print(f"Cross-tenant requests        : {cross_total}")
print(f"E1 cross-tenant permits      : {cross_e1_permits}")
print(f"E2 cross-tenant permits      : {cross_e2_permits}")
print(f"Cross-tenant permits blocked : {cross_blocked}")

if cross_e1_permits > 0:
    blocked_rate = (cross_blocked / cross_e1_permits) * 100

    print(
        f"Cross-tenant blocking rate   : "
        f"{blocked_rate:.4f}%"
    )

if e1_permits > 0:
    reduction = ((e1_permits - e2_permits) / e1_permits) * 100

    print(
        f"Permit reduction             : "
        f"{reduction:.4f}%"
    )

if same_e1_permits > 0:
    preservation = (
        same_e2_permits / same_e1_permits
    ) * 100

    print(
        f"Same-tenant permit preserved : "
        f"{preservation:.4f}%"
    )

print()
print("=" * 70)
