from collections import Counter
from core.myabac import parse_abac_file

POLICY = "DATASETS\\edocument\\edocument.abac"

user_mgr, res_mgr, rule_mgr = parse_abac_file(POLICY)

actions = ["view", "send", "search", "readMetaInfo"]

rule_counts = Counter()
cross_total = 0
cross_permits = 0

examples = {}

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

        if user_tenant == resource_tenant:
            continue

        for action in actions:

            cross_total += 1

            matching_rules = []

            for rule_index, rule in enumerate(rule_mgr.rules, start=1):

                try:
                    if rule.evaluate(user, resource, action):
                        matching_rules.append(rule_index)
                except Exception:
                    pass

            if matching_rules:

                cross_permits += 1

                for rule_index in matching_rules:
                    rule_counts[rule_index] += 1

                    if rule_index not in examples:
                        examples[rule_index] = (
                            user_id,
                            user_tenant,
                            resource_id,
                            resource_tenant,
                            action
                        )


print()
print("=" * 70)
print("CROSS-TENANT PERMIT ? RULE ATTRIBUTION")
print("=" * 70)

print(f"Cross-tenant requests tested : {cross_total}")
print(f"Cross-tenant requests with "
      f"matching rule(s)            : {cross_permits}")

print()
print("--- RULE CONTRIBUTIONS ---")

for rule_index, count in sorted(
    rule_counts.items(),
    key=lambda x: x[1],
    reverse=True
):

    print(
        f"Rule {rule_index:2d} : "
        f"{count:5d} cross-tenant matches"
    )

print()
print("--- EXAMPLE FOR EACH MATCHING RULE ---")

for rule_index in sorted(examples):

    user_id, user_tenant, resource_id, resource_tenant, action = \
        examples[rule_index]

    print(
        f"Rule {rule_index:2d} -> "
        f"{user_id} ({user_tenant}) -> "
        f"{resource_id} ({resource_tenant}) : {action}"
    )

print()
print("=" * 70)
