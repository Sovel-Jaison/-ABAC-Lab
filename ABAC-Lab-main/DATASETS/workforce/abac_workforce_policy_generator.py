import random
import numpy as np

# seed
seed = random.randint(0, int(1e9))
random.seed(seed)
np.random.seed(seed)
print(f"# Seed: {seed}")

# distributions
def uniform_dist(min_val, max_val):
    return np.random.randint(min_val, max_val + 1)

def boolean_dist(prob):
    return np.random.rand() < prob

# generate regions
def get_region():
    return random.choice(["north", "south"])

# certifications
certifications_pool = {
    "telco": "telcoCertifiedTechnician",
    "powerProtection": "powerProtectionSpecialist"
}

# generate user certifications
def get_certifications(tenant):
    certs = set()
    if boolean_dist(0.6):  
        certs.add(certifications_pool[tenant])  
        if boolean_dist(0.3):  
            other_tenant = "telco" if tenant == "powerProtection" else "powerProtection"
            certs.add(certifications_pool[other_tenant])
    return certs

# isCustomerSupport
def get_is_customer_support():
    return boolean_dist(0.3)

# group
def get_group(is_customer_support):
    if is_customer_support:
        return random.choice(["residentialSupport", "companySupport"])
    elif boolean_dist(0.2):
        return random.choice(["provisioning", "techSupport"]) 
    else:
        return "none" # add value as none because some users are not part of a group



### USERS ###
### USER PARAMETERS
NmanagersPerDepartment = 30
NstaffPerManager = (1, 3)  # range of how many staff (i.e. operators, technicians, etc.) per manager 

# user storage
users = {"appadmin": [], "wfmgr": [], "tech": [], "hdmgr": [], "hdop": [],
         "whmgr": [], "whop": [], "slmgr": [], "mtmgr": []}
tech_certifications = {}

# init counts
counts = {key: 0 for key in users}

# position names
position_names = {
    "wfmgr": "workforceManager", "tech": "technician",
    "hdmgr": "helpdeskManager", "hdop": "helpdeskOperator",
    "whmgr": "warehouseManager", "whop": "warehouseOperator",
    "slmgr": "salesManager", "mtmgr": "maintenanceManager",
    "appadmin": "applicationAdmin"
}
tenants = ["telco", "powerProtection"]
user_tenants = {role: {tenant: [] for tenant in tenants} for role in users}

# provider mapping
provider_map = {
    "wfmgr": "workforceProvider", "tech": "workforceProvider",
    "hdmgr": "helpdeskProvider", "hdop": "helpdeskProvider",
    "whmgr": "warehouseProvider", "whop": "warehouseProvider",
    "slmgr": "primaryTenant", "mtmgr": "primaryTenant",
    "appadmin": "workforceProvider"
}



# provider probabilities
def get_provider_for_role(role, tenant=None):
    if role in ["hdop", "hdmgr"]:
        return random.choices(
            ["eWorkforce", "externalHelpdeskSupplier"], [0.6, 0.4])[0]
    elif role == "tech":
        return random.choices(
            ["eWorkforce", "externalWorkforceSupplier", "subcontractor"], [0.5, 0.3, 0.2])[0]
    elif role == "wfmgr":
        return random.choices(
            ["eWorkforce", "externalWorkforceSupplier", "subcontractor"], [0.5, 0.3, 0.2])[0]
    elif role == "whmgr":
        return random.choices(
            ["eWorkforce", "externalWarehouseSupplier", "subcontractor"], [0.5, 0.3, 0.2])[0]
    elif role == "whop":
        return random.choices(
            ["eWorkforce", "externalWarehouseSupplier", "subcontractor"], [0.5, 0.3, 0.2])[0]
    elif role == "slmgr" or role == "mtmgr":
        return tenant # for sales and maintenance managers, provider tenant matches assigned tenant. wouldnt make sense to have a telco manager assigned to powerProtection
    elif role == "appadmin":
        return "eWorkforce"
    else:
        return "unknown"

# generate managers and their staff
for manager_role, staff_role, department in [
    ("wfmgr", "tech", "workforce"), ("hdmgr", "hdop", "helpdesk"),
    ("whmgr", "whop", "warehouse"), ("slmgr", None, "sales"),
    ("mtmgr", None, "maintenance")
]:
    # generate param amount of managers for each dept
    for i in range(NmanagersPerDepartment): 
        tenant = tenants[i % 2]  # alternate between telco and powerProtection
        counts[manager_role] += 1
        manager_id = f"{manager_role}{counts[manager_role]:03}"
        assigned_region = get_region()
        managed_staff = []
        is_customer_support = get_is_customer_support()
        group = get_group(is_customer_support)
        
        # assign provider for managers
        manager_provider = get_provider_for_role(manager_role, tenant)
        users[manager_role].append(
            f"userAttrib({manager_id}, position={position_names[manager_role]}, department={department}, provider={manager_provider}, "
            f"assignedTenant={tenant}, assignedRegion={assigned_region}, managedStaff={{}}, isCustomerSupport={is_customer_support}, group={group})"
        )
        user_tenants[manager_role][tenant].append(manager_id)
        
        # generate param amount of staff for each manager 
        if staff_role:
            num_staff = uniform_dist(NstaffPerManager[0], NstaffPerManager[1])
            for _ in range(num_staff):
                counts[staff_role] += 1
                staff_id = f"{staff_role}{counts[staff_role]:03}"
                staff_provider = manager_provider  # staff has same provider as manager

                # only include certifications for technicians. no one else
                certs = get_certifications(tenant) if staff_role == "tech" else set()

                if staff_role == "tech":
                    tech_certifications[staff_id] = certs
                
                certs_str = f", certifications={{{' '.join(certs)}}}" if staff_role == "tech" else ""
                
                users[staff_role].append(
                    f"userAttrib({staff_id}, position={position_names[staff_role]}, department={department}, provider={staff_provider}, "
                    f"assignedTenant={tenant}, assignedRegion={assigned_region}{certs_str}, isCustomerSupport={is_customer_support}, group={group})"
                )
                user_tenants[staff_role][tenant].append(staff_id)
                managed_staff.append(staff_id)
            
            # update manager with assigned staff
            users[manager_role][-1] = (
                f"userAttrib({manager_id}, position={position_names[manager_role]}, department={department}, provider={manager_provider}, "
                f"assignedTenant={tenant}, assignedRegion={assigned_region}, managedStaff={{{' '.join(managed_staff)}}}, isCustomerSupport={is_customer_support}, group={group})"
            )
# add 1 application admin
users["appadmin"].append("userAttrib(appadmin001, position=applicationAdmin, department=admin, provider=eWorkforce)")



### RESOURCES ###
### RESOURCE PARAMETERS
NcontractsPerTenant = 5
NworkOrdersPerContract = 5
NtasksPerWorkOrder = 3
NtaskDeviation = 1 # plus/minus deviation from the initial tasksPerWorkOrder
NrequestsPerTenant = 10 

# resource storage
contracts, work_orders, tasks, stock_refill_requests, resource_requests = [], [], [], [], []

# two tenants in total. referenced from workforce-management.txt
for i, tenant in enumerate(tenants):

    # N contracts per primary tenant, 60% of them active and 30% is inactive
    contract_ids = []
    Nactive = NcontractsPerTenant // 2  
    remaining = NcontractsPerTenant - Nactive  

    contract_statuses = ["active"] * Nactive + ["active" if boolean_dist(0.5) else "inactive" for _ in range(remaining)]
    random.shuffle(contract_statuses)

    for j in range(NcontractsPerTenant):
        contract_id = f"contract{i*NcontractsPerTenant + j + 1:03}"
        contract_region = get_region()

        contracts.append(
            f"resourceAttrib({contract_id}, type=contract, department=workforce, tenant={tenant}, tenantType=primary, "
            f"resourceRegion={contract_region}, contractStatus={contract_statuses[j]})"
        )
        contract_ids.append(contract_id)

        # generate work orders per contract
        for k in range(NworkOrdersPerContract):
            work_order_id = f"workorder{i*NcontractsPerTenant*NworkOrdersPerContract + j*NworkOrdersPerContract + k + 1:03}"
            
            assigned_technician = random.choice(user_tenants["tech"][tenant])
            created_by = random.choice(user_tenants["hdop"][tenant])  
            recurrence = boolean_dist(0.5)
            is_appointment = boolean_dist(0.3) if not recurrence else False
            
            assigned_tech_certs = tech_certifications.get(assigned_technician, set())
            required_cert = certifications_pool[tenant] if certifications_pool[tenant] in assigned_tech_certs else ""
            certs_str = f", requiredCertifications={{{required_cert}}}" if required_cert else ", requiredCertifications={}"
            
            work_orders.append(
                f"resourceAttrib({work_order_id}, type=workOrder, department=workforce, tenant={tenant}, tenantType=primary, "
                f"resourceRegion={contract_region}, contractStatus={contract_statuses[j]}, associatedContract={contract_id}, createdBy={created_by}, "
                f"assignedTechnician={assigned_technician}{certs_str}, recurrence={recurrence}, isAppointment={is_appointment})"
            )

            # generate tasks per work order
            num_tasks = uniform_dist(NtasksPerWorkOrder - NtaskDeviation, NtasksPerWorkOrder + NtaskDeviation)
            for _ in range(num_tasks):
                task_id = f"task{len(tasks) + 1:03}"
                tasks.append(
                    f"resourceAttrib({task_id}, type=task, department=workforce, tenant={tenant}, tenantType=primary, "
                    f"resourceRegion={contract_region}, contractStatus={contract_statuses[j]}, associatedContract={contract_id}, "
                    f"associatedWorkOrder={work_order_id}, assignedTechnician={assigned_technician}{certs_str})"
                )

    # Generate stock refill requests per tenant
    for j in range(NrequestsPerTenant):
        request_id = f"stockrefill{i*NrequestsPerTenant + j + 1:03}"
        resource_region = get_region()
        contract_status = random.choice(["active", "inactive"])
        assigned_employee = random.choice(user_tenants["whop"][tenant])
        is_complete = boolean_dist(0.5)

        stock_refill_requests.append(
            f"resourceAttrib({request_id}, type=stockRefillRequest, department=warehouse, tenant={tenant}, tenantType=primary, "
            f"resourceRegion={resource_region}, contractStatus={contract_status}, assignedEmployee={assigned_employee}, "
            f"isComplete={is_complete})"
        )

    # Generate resource requests per tenant
    for j in range(NrequestsPerTenant):
        request_id = f"resourcereq{i*NrequestsPerTenant + j + 1:03}"
        resource_region = get_region()
        contract_status = random.choice(["active", "inactive"])
        assigned_employee = random.choice(user_tenants["whop"][tenant])
        assigned_technician = random.choice(user_tenants["tech"][tenant])
        is_complete = boolean_dist(0.5)

        resource_requests.append(
            f"resourceAttrib({request_id}, type=resourceRequest, department=warehouse, tenant={tenant}, tenantType=primary, "
            f"resourceRegion={resource_region}, contractStatus={contract_status}, assignedEmployee={assigned_employee}, "
            f"isComplete={is_complete}, assignedTechnician={assigned_technician})"
        )



### OUTPUT ###
# output policy in .abac file
filename = "workforce.abac"
with open(filename, "w", encoding="utf-8") as file:
    file.write("# ABAC policy for a workforce management system.\n\n")

    file.write("#------------------------------------------------------------\n")
    file.write("# User Attribute Data\n")
    file.write("#------------------------------------------------------------\n")
    for position, user_list in users.items():
        file.write(f"\n# {position_names.get(position, position)}\n")
        for user in user_list:
            file.write(user + "\n")
    
    file.write("\n#------------------------------------------------------------\n")
    file.write("# Resource Attribute Data\n")
    file.write("#------------------------------------------------------------\n")
    file.write("\n# Contracts\n")
    for contract in contracts:
        file.write(contract + "\n")
    file.write("\n# Work Orders\n")
    for work_order in work_orders:
        file.write(work_order + "\n")
    file.write("\n# Tasks\n")
    for task in tasks:
        file.write(task + "\n")
    file.write("\n# Resource Requests\n")
    for request in resource_requests:
        file.write(request + "\n")
    file.write("\n# Stock Refill Requests\n")
    for request in stock_refill_requests:
        file.write(request + "\n")

# ABAC RULES
    file.write("\n#------------------------------------------------------------\n")
    file.write("# ABAC Rules\n")
    file.write("#------------------------------------------------------------\n\n")

    # eWorkforce
    file.write("#------------------------------\n")
    file.write("# eWorkforce \n")
    file.write("#------------------------------\n")
    
    file.write("\n# eWorkforce Helpdesk\n#-----")
    file.write("\n# 1. Only helpdesk operators can create work orders that apply to active contracts of a Primary Tenant for which he/she is assigned responsible.\n")
    file.write("rule(provider [ {eWorkforce}, position [ {helpdeskOperator}; type [ {contract}, contractStatus [ {active}, tenantType [ {primary}; {createOneTimeWorkOrder createRecurrentWorkOrder}; assignedTenant = tenant)\n")
    file.write("\n# 2. Helpdesk operators can only modify or remove work orders that apply to active contracts of a Primary Tenant for which he/she is assigned responsible.\n")
    file.write("rule(provider [ {eWorkforce}, position [ {helpdeskOperator}; type [ {workOrder}, contractStatus [ {active}, tenantType [ {primary}; {modify delete}; assignedTenant = tenant)\n")

    file.write("\n\n# Application Admins\n#-----")
    file.write("\n# 3. Application admins can create appointments for all tenants of eWorkforce.\n")
    file.write("rule(provider [ {eWorkforce}, position [ {applicationAdmin}; type [ {contract}; {createAppointment}; )\n")
    file.write("\n# 4. Application admins can modify and delete appointments for all tenants of eWorkforce.\n")
    file.write("rule(provider [ {eWorkforce}, position [ {applicationAdmin}; type [ {workOrder}, isAppointment [ {True}; {modify delete}; )\n")

    file.write("\n\n# Internal Workforce\n#-----")
    file.write("\n# 5. Only employees of the workforce team can access tasks.\n")
    file.write("rule(provider [ {eWorkforce}, department [ {workforce}; type [ {task}; {view}; )\n")
    file.write("\n# 6. Employees can only access tasks of customers which relate to their department.\n# Employees can only access tasks of active projects/contracts.\n")
    file.write("rule(provider [ {eWorkforce}; type [ {task}, contractStatus [ {active}; {view}; department = department)\n")
    file.write("\n# 7. Technicians can only view and complete tasks that are assigned to them.\n")
    file.write("rule(provider [ {eWorkforce}, position [ {technician}; type [ {task}; {view complete}; uid = assignedTechnician)\n")
    file.write("\n# 8. Workforce Managers can view and complete all tasks assigned to a Technician for which they are assigned responsible.\n")
    file.write("rule(provider [ {eWorkforce}, position [ {workforceManager}; type [ {task}; {view complete}; managedStaff ] assignedTechnician)\n")

    file.write("\n\n# Internal Warehouse\n#-----")
    file.write("\n# 9. All warehouse managers can mark a stock refill request sent to the warehouse as completed.\n")
    file.write("rule(provider [ {eWorkforce}, position [ {warehouseManager}; type [ {stockRefillRequest}; {markComplete}; )\n")
    file.write("\n# 10. A warehouse operator can only view or complete resource requests assigned to him/her.\n")
    file.write("rule(provider [ {eWorkforce}, position [ {warehouseOperator}; type [ {resourceRequest}; {view complete}; uid = assignedEmployee)\n")
    file.write("\n# 11. A warehouse manager can view and complete any resource request assigned to any warehouse operator of the warehouse.\n")
    file.write("rule(provider [ {eWorkforce}, position [ {warehouseManager}; type [ {resourceRequest}; {view complete}; managedStaff ] assignedEmployee)\n\n")

    # PowerProtection
    file.write("\n#------------------------------\n")
    file.write("# PowerProtection\n")
    file.write("#------------------------------\n")
    
    file.write("\n# PowerProtection Sales Managers\n#-----")
    file.write("\n# 12. All sales managers can create work orders.\n# Sales managers can only create one-time work orders.\n")
    file.write("rule(provider [ {powerProtection}, position [ {salesManager}; type [ {contract}, tenant [ {powerProtection}; {createOneTimeWorkOrder}; )\n")
    file.write("\n# 13. All sales managers can view all work orders.\n")
    file.write("rule(provider [ {powerProtection}, position [ {salesManager}; type [ {workOrder}, tenant [ {powerProtection}; {view}; )\n")
    
    file.write("\n\n# PowerProtection Maintenance Managers\n#-----")
    file.write("\n# 14. All maintenance managers can create work orders.\n# Maintenance managers can create one-time and recurrent work orders.\n")
    file.write("rule(provider [ {powerProtection}, position [ {maintenanceManager}; type [ {contract}, tenant [ {powerProtection}; {createOneTimeWorkOrder createRecurrentWorkOrder}; )\n")
    
    file.write("\n\n# PowerProtection Stock Refill Notifications\n#-----")
    file.write("\n# 15. Only members of the Provisioning group can receive stock refill notifications.\n")
    file.write("rule(provider [ {powerProtection}, group [ {provisioning}; type [ {stockRefillRequest}, tenant [ {powerProtection}; {receive}; )\n\n")
    
    # TelCo
    file.write("\n#------------------------------\n")
    file.write("# TelCo\n")
    file.write("#------------------------------\n")
    
    file.write("\n# TelCo Work Orders\n#-----")
    file.write("\n# 16. Every employee of TelCo which is member of Customer Support can use the application to create work orders.\n")
    file.write("rule(provider [ {telco}, isCustomerSupport [ {True}; type [ {contract}, tenant [ {telco}; {createOneTimeWorkOrder}; )\n")
    file.write("\n# 17. Members of Customer Support which are part of the Company Support group can only send one-time work orders. They can also create recurring work orders if they are Sales Managers or Maintenance Managers.\n")
    file.write("rule(provider [ {telco}, isCustomerSupport [ {True}, group [ {companySupport}, position [ {salesManager maintenanceManager}; type [ {contract}, tenant [ {telco}; {createOneTimeWorkOrder createRecurrentWorkOrder}; )\n")
    file.write("\n# 18. Only Members of Customer Support which are part of the Residential Support group and are Maintenance Managers can create recurring work orders, the rest can only create one-time work orders.\n")
    file.write("rule(provider [ {telco}, position [ {maintenanceManager}, isCustomerSupport [ {True}, group [ {residentialSupport}; type [ {contract}, tenant [ {telco}; {createRecurrentWorkOrder}; )\n")
    
    file.write("\n\n# TelCo Stock Refill Notifications\n#-----")
    file.write("\n# 19. Only members of Technician Support can receive stock refill notifications.\n# All members of Technician Support can receive stock refill notifications.\n")
    file.write("rule(provider [ {telco}, group [ {techSupport}; type [ {stockRefillRequest}, tenant [ {telco}; {receive}; )\n\n")
    
    # Helpdesk Supplier 
    file.write("\n#------------------------------\n")
    file.write("# Helpdesk Supplier\n")
    file.write("#------------------------------\n")
    
    file.write("\n# Helpdesk Supplier Helpdesk Operators\n#-----")
    file.write("\n# 20. All Helpdesk Operators can create a new work order.\n")
    file.write("rule(provider [ {externalHelpdeskSupplier}, position [ {helpdeskOperator}; type [ {contract}; {createOneTimeWorkOrder createRecurrentWorkOrder}; )\n")
    file.write("\n# 21. All Helpdesk Operators can modify a new work order.\n")
    file.write("rule(provider [ {externalHelpdeskSupplier}, position [ {helpdeskOperator}; type [ {workOrder}; {modify}; )\n")
    
    file.write("\n\n# Helpdesk Supplier Helpdesk Managers\n#-----")
    file.write("\n# 22. Helpdesk Managers can only view work orders.\n# Helpdesk Managers can only view work orders created by Helpdesk Operators which are members of the team they are responsible for.\n")
    file.write("rule(provider [ {externalHelpdeskSupplier}, position [ {helpdeskManager}; type [ {workOrder}; {view}; managedStaff ] createdBy)\n\n")
    
    # Workforce Supplier 
    file.write("\n#------------------------------\n")
    file.write("# Workforce Supplier\n")
    file.write("#------------------------------\n")
    
    file.write("\n# Workforce Supplier General\n#-----")
    file.write("\n# 23. Only Technicians or Workforce Managers can access tasks.\n# Employees of a Workforce Supplier can only access tasks of customers which relate to their department\n# Employees of a Workforce Supplier can only access tasks of active projects/contracts.\n")
    file.write("rule(provider [ {externalWorkforceSupplier}, position [ {workforceManager technician}; type [ {task}, contractStatus [ {active}; {view}; department = department)\n")
    
    file.write("\n\n# Workforce Supplier Technicians\n#-----")
    file.write("\n# 24. Technicians can only view and complete tasks that are assigned to them.\n")
    file.write("rule(provider [ {externalWorkforceSupplier}, position [ {technician}; type [ {task}; {view complete}; uid = assignedTechnician)\n")
    
    file.write("\n\n# Workforce Supplier Workforce Managers\n#-----")
    file.write("\n# 25. Workforce Managers can view and complete all tasks assigned to a Technician for which they are assigned responsible.\n")
    file.write("rule(provider [ {externalWorkforceSupplier}, position [ {workforceManager}; type [ {task}; {view complete}; managedStaff ] assignedTechnician)\n\n")
    
    # Subcontractor 
    file.write("\n#------------------------------\n")
    file.write("# Subcontractor\n")
    file.write("#------------------------------\n")
    
    file.write("\n# Subcontractor General\n#-----")
    file.write("\n# 26. Only Technicians or Workforce Managers can access tasks.\n# Employees of a Workforce Supplier can only access tasks of customers which relate to their department.\n# Employees of a Workforce Supplier can only access tasks of active projects/contracts.\n")
    file.write("rule(provider [ {subcontractor}, position [ {workforceManager technician}; type [ {task}, contractStatus [ {active}; {view}; department = department)\n")
    
    file.write("\n\n# Subcontractor Technicians\n#-----")
    file.write("\n# 27. Technicians can only view and complete tasks that are assigned to them.\n")
    file.write("rule(provider [ {subcontractor}, position [ {technician}; type [ {task}; {view complete}; uid = assignedTechnician)\n")
    
    file.write("\n\n# Subcontractor Workforce Managers\n#-----")
    file.write("\n# 28. Workforce Managers can view and complete all tasks assigned to a Technician in their team.\n")
    file.write("rule(provider [ {subcontractor}, position [ {workforceManager}; type [ {task}; {view complete}; managedStaff ] assignedTechnician)\n\n")

print(f"ABAC policy generated and saved as '{filename}'.")


