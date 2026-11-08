from core.myabac import parse_abac_file

policy_file = "DATASETS/edocument/edocument.abac"

users, resources, rules = parse_abac_file(policy_file)

print("=" * 80)
print("E-DOCUMENT RULE ANALYSIS")
print("=" * 80)

tenant_rules = []
non_tenant_rules = []

for i, rule in enumerate(rules.rules, 1):

    print(f"\nRULE {i}")
    print("-" * 80)

    print("Subject conditions:")
    print(rule.sub_cond)

    print("Resource conditions:")
    print(rule.res_cond)

    print("Actions:")
    print(rule.acts)

    print("Constraints:")
    print(rule.cons)

    # Check whether tenant is explicitly involved anywhere
    tenant_used = False

    for attr, op, value in rule.sub_cond:
        if attr == "tenant":
            tenant_used = True

    for attr, op, value in rule.res_cond:
        if attr == "tenant":
            tenant_used = True

    for left_attr, op, right_attr in rule.cons:
        if left_attr == "tenant" or right_attr == "tenant":
            tenant_used = True

    if tenant_used:
        tenant_rules.append(i)
    else:
        non_tenant_rules.append(i)

print("\n" + "=" * 80)
print("SUMMARY")
print("=" * 80)

print("Total rules:", len(rules.rules))

print("\nRules explicitly involving tenant:")
print(tenant_rules)

print("\nRules NOT explicitly involving tenant:")
print(non_tenant_rules)

print("\nTenant rule count:", len(tenant_rules))
print("Non-tenant rule count:", len(non_tenant_rules))