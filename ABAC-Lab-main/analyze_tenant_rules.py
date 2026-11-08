from core.myabac import parse_abac_file

POLICY = "DATASETS\\edocument\\edocument.abac"

user_mgr, res_mgr, rule_mgr = parse_abac_file(POLICY)

print()
print("=" * 75)
print("ABAC RULE TENANT-CONDITION ANALYSIS")
print("=" * 75)

for rule_index, rule in enumerate(rule_mgr.rules, start=1):

    tenant_conditions = []

    for condition in rule.sub_cond:
        if condition[0] == "tenant":
            tenant_conditions.append(("SUBJECT", condition))

    for condition in rule.res_cond:
        if condition[0] == "tenant":
            tenant_conditions.append(("RESOURCE", condition))

    for condition in rule.cons:
        if condition[0] == "tenant":
            tenant_conditions.append(("CONSTRAINT", condition))

    if tenant_conditions:
        status = "YES"
    else:
        status = "NO"

    print(
        f"Rule {rule_index:2d} | "
        f"Tenant condition: {status}"
    )

    if tenant_conditions:
        for location, condition in tenant_conditions:
            print(
                f"           {location}: {condition}"
            )

print("=" * 75)
