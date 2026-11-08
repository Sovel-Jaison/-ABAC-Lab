import random
from collections import defaultdict

# probability
def probability(p):
    return random.random() < p

# params for scale
nUsers = 400
nDocuments = max(300, nUsers // 2)
nHelpdeskOperators = min(30, nUsers // 10)
nApplicationAdmins = min(30, nUsers // 10)
nCustomers = min(40, nUsers // 2)
roles = ["employee", "manager", "admin", "helpdesk", "customer"]
positions = ["secretary", "director", "seniorOfficeManager", "officeManager", "insuranceAgent"]
documentTypes = ["invoice", "contract", "paycheck", "bankingNote", "salesOffer", "trafficFine"]

# define objects
tenants = ["largeBank", "largeBankLeasing", "newsAgency", "europeRegion", "londonOffice", "reseller"]
customerTenants = ["carLeaser", "ictProvider", "privateReceiver"]
departments = {
    "largeBank": ["largeBankSales", "largeBankICT", "largeBankHR", "largeBankIT", "largeBankAudit"],
    "largeBankLeasing": ["largeBankLeasingCustomerCare", "largeBankLeasingSales"],
    "newsAgency": ["newsAgencyAudit", "newsAgencyIT"],
    "europeRegion": ["europeRegionIT", "europeRegionHR"],
    "londonOffice": ["londonOfficeAudit", "londonOfficeHR", "londonOfficeSales"],
    "reseller": ["resellerSales", "resellerCustomer", "resellerAccounting"]
}

# separate customer tenant departments
def get_customer_departments(tenant):
    base_departments = ["Audit", "Secretary", "Accounting"]
    if tenant == "ictProvider":
        base_departments.append("ICT")
    return [f"{tenant}{dept}" for dept in base_departments]

for customerTenant in customerTenants:
    departments[customerTenant] = get_customer_departments(customerTenant)

offices = {
    "largeBank": 10,
    "largeBankLeasing": 2,
    "ictProvider": 5,
    "newsAgency": 0,
    "europeRegion": 0,
    "londonOffice": 0,
    "reseller": 0
}

for customerTenant in customerTenants:
    offices[customerTenant] = 0

# organizations aka tenants
class Organization:
    def __init__(self, orgId, departments, offices):
        self.orgId = orgId
        self.departments = departments
        self.offices = offices

# users aka subjects
class User:
    def __init__(self, userId, role, organization, department=None, office=None, position=None):
        self.userId = userId
        self.role = role
        self.organization = organization
        self.department = department if department else "none"
        self.office = office if office else "none"
        self.position = position if position else "none"
        self.projects = set()
        self.supervisor = None
        self.supervisee = set()
        self.payrollingPermissions = False
        self.registered = False

    def __str__(self):
        attributes = [
            f"role={self.role}",
            f"position={self.position}",
            f"tenant={self.organization.orgId}",
            f"department={self.department}",
            f"office={self.office}",
            f"registered={'True' if self.registered else 'False'}",
            f"projects={{{' '.join(self.projects)}}}",
            f"supervisor={self.supervisor if self.supervisor else 'none'}",
            f"supervisee={{{' '.join(self.supervisee)}}}",
            f"payrollingPermissions={self.payrollingPermissions}"
        ]
        return f"userAttrib({self.userId}, {', '.join(attributes)})"

# generate organizations / tenants
organizations = {tenant: Organization(tenant, departments[tenant], offices[tenant]) for tenant in tenants}
for customerTenant in customerTenants:
    organizations[customerTenant] = Organization(customerTenant, departments[customerTenant], offices.get(customerTenant, 0))

# generate users
users = []
users_by_department = defaultdict(list)
for i in range(nUsers):
    tenant = random.choice(tenants)
    
    valid_positions = positions if offices[tenant] > 0 else [p for p in positions if p not in ["secretary", "director"]]
    position = random.choice(valid_positions)
    
    office = "none"
    if offices[tenant] > 0 or position in ["secretary", "director"]:
        office = f"{tenant}Office{random.randint(1, offices[tenant])}" if offices[tenant] > 0 else "none"

    department = random.choice(departments[tenant])
    user = User(f"user{i}", "employee", organizations[tenant], department, office, position)
    users.append(user)
    users_by_department[(tenant, department)].append(user)

# generate helpdesk operators
helpdeskOperators = []
for i in range(nHelpdeskOperators):
    tenant = random.choice(tenants)
    user = User(f"hdop{i}", "helpdesk", organizations[tenant])
    helpdeskOperators.append(user)

# generate application admins
applicationAdmins = []
for i in range(nApplicationAdmins):
    tenant = random.choice(tenants)
    user = User(f"admin{i}", "admin", organizations[tenant])
    applicationAdmins.append(user)

# generate customers
customers = []
for i in range(nCustomers):
    tenant = random.choice(customerTenants)
    user = User(f"cstmr{i}", "customer", organizations[tenant], department=random.choice(get_customer_departments(tenant)))
    customers.append(user)

users.extend(helpdeskOperators)
users.extend(applicationAdmins)
users.extend(customers)

# supervisor logic
position_hierarchy = {"secretary": 1, "officeManager": 2, "seniorOfficeManager": 3, "director": 4}
for (tenant, department), dept_users in users_by_department.items():
    dept_users.sort(key=lambda u: position_hierarchy.get(u.position, 0), reverse=True)
    for i, user in enumerate(dept_users):
        if i > 0:
            user.supervisor = dept_users[i - 1].userId
            dept_users[i - 1].supervisee.add(user.userId)

# update registered attribute based on if they are supervisor
for user in users:
    if user.supervisee:
        user.registered = True
    else:
        user.registered = False

# assign payrolling permissions
for (tenant, department), dept_users in users_by_department.items():
    random.choice(dept_users).payrollingPermissions = True
    for user in dept_users:
        if probability(0.5):
            user.payrollingPermissions = True

def get_random_users_from_tenant(users, tenant, count):
    tenant_users = [user for user in users if user.organization.orgId == tenant]
    return random.sample(tenant_users, min(count, len(tenant_users)))

# resources aka documents
class Document:
    def __init__(self, docId, docType, owner, confidential=False, containsPersonalInfo=False):
        self.docId = docId
        self.docType = docType
        self.owner = owner
        self.confidential = confidential
        self.containsPersonalInfo = containsPersonalInfo
        self.tenant = owner.organization.orgId
        self.department = owner.department
        self.office = f"{self.tenant}Office{random.randint(1, offices[self.tenant])}" if offices[self.tenant] > 0 else "none"
        self.recipients = set()

        if self.office != "none":
            office_users = [user for user in users if user.office == self.office]
            self.recipients.update(office_users)
        else:
            self.recipients.update(get_random_users_from_tenant(users, self.tenant, 5))

        self.recipients.update(get_random_users_from_tenant(users, self.tenant, 3))

    def __str__(self):
        attributes = [
            f"type={self.docType}",
            f"owner={self.owner.userId}",
            f"tenant={self.tenant}",
            f"department={self.department}",
            f"office={self.office}",
            f"recipients={{{' '.join(user.userId for user in self.recipients)}}}",
            f"isConfidential={'True' if self.confidential else 'False'}",
            f"containsPersonalInfo={'True' if self.containsPersonalInfo else 'False'}"
        ]
        return f"resourceAttrib({self.docId}, {', '.join(attributes)})"

# generate documents
documents = []
for i in range(nDocuments):
    owner = random.choice(users)
    docType = random.choice(documentTypes)
    confidential = probability(0.6)
    containsPersonalInfo = probability(0.2)
    doc = Document(f"doc{i}", docType, owner, confidential, containsPersonalInfo)
    documents.append(doc)

# assign resources as projects
for doc in documents:
    doc.owner.projects.add(doc.docId)

# output
filename = "edocument.abac"
with open(filename, "w", encoding="utf-8") as f:
    f.write("# ABAC policy for document management system.\n\n")
    f.write("#------------------------------------------------------------\n")
    f.write("# User Attribute Data\n")
    f.write("#------------------------------------------------------------\n\n")
    for user in users:
        f.write(str(user) + "\n")
    
    f.write("\n#------------------------------------------------------------\n")
    f.write("# Resource Attribute Data\n")
    f.write("#------------------------------------------------------------\n\n")
    for doc in documents:
        f.write(str(doc) + "\n")

    # rules
    f.write("\n#------------------------------------------------------------\n")
    f.write("# ABAC Rules\n")
    f.write("#------------------------------------------------------------\n\n")

    # eDocs
    f.write("# 1. An Unregistered Receiver can only view documents sent to them.\n")
    f.write("rule(role [ {customer}, registered [ {False}; ; {view}; uid [ recipients)\n\n")

    f.write("# 2. Helpdesk members can search and view meta-information of documents in the application.\n")
    f.write("rule(role [ {helpdesk}; ; {search readMetaInfo}; uid [ recipients)\n\n")

    f.write("# 3. Helpdesk members can only read the content of documents belonging to tenants they are assigned responsible.\n")
    f.write("rule(role [ {helpdesk}; isConfidential [ {False}; {view}; tenant = tenant)\n\n")

    f.write("# 4. Application admins can view documents that are not confidential.\n")
    f.write("rule(role [ {admin}; isConfidential [ {False}; {view}; )\n\n")

    # large bank
    f.write("# 5. A supervisor can read documents sent by their supervisees.\n")
    f.write("rule(role [ {employee}, registered [ {True}, tenant [ {largeBank}; ; {view}; supervisee ] owner)\n\n")

    f.write("# 6. A project member can read all sent documents related to the project.\n")
    f.write("rule(role [ {employee}, tenant [ {largeBank}; ; {view}; projects ] rid)\n\n")

    f.write("# 7. Only members of the sales department can send, view, or search invoices.\n")
    f.write("rule(role [ {employee}, department [ {largeBankSales}; type [ {invoice}; {send view search}; )\n\n")

    f.write("# 8. Only members of the ICT department can send banking notes and view their status.\n")
    f.write("rule(role [ {employee}, department [ {largeBankICT}; type [ {bankingNote}; {send readMetaInfo}; )\n\n")

    f.write("# 9. Only employees responsible for payrolling can send and view paychecks.\n")
    f.write("rule(role [ {employee}, tenant [ {largeBank}, payrollingPermissions [ {True}; type [ {paycheck}; {send view}; )\n\n")

    f.write("# 10. Only sales department members can send sales offers.\n")
    f.write("rule(role [ {employee}, department [ {largeBankSales}; type [ {salesOffer}; {send}; )\n\n")

    f.write("# 11. Only the bank office manager can send documents.\n")
    f.write("rule(role [ {employee}, tenant [ {largeBank}, position [ {officeManager seniorOfficeManager}; ; {send}; )\n\n")

    f.write("# 12. Audit department members can read all invoices, offers, and documents except those containing personal information.\n")
    f.write("rule(role [ {employee}, department [ {largeBankAudit}; type [ {invoice salesOffer}, containsPersonalInfo [ {False}; {view}; )\n\n")

    # large bank leasing
    f.write("# 13. Only members of Customer Care can view traffic fines.\n")
    f.write("rule(role [ {employee}, department [ {largeBankLeasingCustomerCare}; type [ {trafficFine}; {view}; )\n\n")

    f.write("# 14. Only sales users can send invoices.\n#     Only Customer Care Office members can manually bill a customer.\n")
    f.write("rule(role [ {employee}, department [ {largeBankLeasingSales largeBankLeasingCustomerCare}; type [ {invoice}; {send}; )\n\n")

    # local bank offices
    f.write("# 15. Only the secretary and office director can read documents sent to the bank office.\n")
    f.write("rule(role [ {employee}, position [ {secretary director}; ; {view}; office = office)\n\n")

    # car leaser
    f.write("# 16. Any member of the Accounting department can receive and read invoices.\n")
    f.write("rule(role [ {customer}, department [ {carLeaserAccounting}; type [ {invoice}; {view}; )\n\n")

    # ictProvider
    f.write("# 17. Only secretary members can read invoices.\n")
    f.write("rule(role [ {customer}, department [ {ictProviderSecretary}; type [ {invoice}; {view}; )\n\n")

    # news agency
    f.write("# 18. Audit department members can read all invoices, offers, contracts, and paychecks.\n")
    f.write("rule(role [ {employee}, department [ {newsAgencyAudit}; type [ {invoice salesOffer contract paycheck}; {view}; )\n\n")

    # europe region
    f.write("# 19. Only members of the HR department can send contracts.\n")
    f.write("rule(role [ {employee}, department [ {europeRegionHR}; type [ {contract}; {send}; )\n\n")

    # london office
    f.write("# 20. Members of the Human Resources department can send contracts.\n")
    f.write("rule(role [ {employee}, department [ {londonOfficeHR}; type [ {contract}; {send}; )\n\n")

    f.write("# 21. Any member of the Sales department can send invoices.\n")
    f.write("rule(role [ {employee}, department [ {londonOfficeSales}; type [ {invoice}; {send}; )\n\n")

    f.write("# 22. Any member of the Sales department can read all invoices sent by the department.\n")
    f.write("rule(role [ {employee}, department [ {londonOfficeSales}; type [ {invoice}; {view}; department = department)\n\n")

    # reseller
    f.write("# 23. Only assigned Customer department members can read a subtenant's documents.\n")
    f.write("rule(role [ {employee}, department [ {resellerCustomer}; ; {view}; uid [ recipients)\n\n")

    f.write("# 24. Any member of the Accounting department can send invoices.\n")
    f.write("rule(role [ {employee}, department [ {resellerAccounting}; type [ {invoice}; {send}; )\n\n")

    # registered private receivers
    f.write("# 25. Registered Private Receivers can only read documents they received.\n")
    f.write("rule(role [ {customer}, tenant [ {privateReceiver}; ; {view}; uid [ recipients)\n\n")

print(f"ABAC policy generated and saved as '{filename}'.")


#
