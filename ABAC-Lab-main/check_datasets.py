from pathlib import Path

datasets = {
    "E-Document": "DATASETS/edocument/edocument.abac",
    "Healthcare": "DATASETS/healthcare/healthcare.abac",
    "Project Management": "DATASETS/project-management/project-management.abac",
    "University": "DATASETS/university/university.abac",
    "Workforce": "DATASETS/workforce/workforce.abac",
}

for name, file_path in datasets.items():

    path = Path(file_path)

    print("\n" + "=" * 60)
    print(name)
    print("=" * 60)

    if not path.exists():
        print("FILE NOT FOUND:", path)
        continue

    text = path.read_text(errors="ignore")
    lines = text.splitlines()

    user_lines = [x for x in lines if x.startswith("userAttrib(")]
    resource_lines = [x for x in lines if x.startswith("resourceAttrib(")]
    rule_lines = [x for x in lines if x.startswith("rule(")]

    user_tenant = [
        x for x in user_lines
        if "tenant=" in x
    ]

    resource_tenant = [
        x for x in resource_lines
        if "tenant=" in x
    ]

    print("Users:", len(user_lines))
    print("Resources:", len(resource_lines))
    print("Rules:", len(rule_lines))

    print("Users with tenant:", len(user_tenant))
    print("Resources with tenant:", len(resource_tenant))

    if user_tenant:
        print("\nSample user:")
        print(user_tenant[0])

    if resource_tenant:
        print("\nSample resource:")
        print(resource_tenant[0])