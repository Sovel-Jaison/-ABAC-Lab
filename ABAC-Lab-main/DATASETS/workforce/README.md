# Policy Description: Workforce

*Vesion: v20250308*

This policy governs a SaaS workforce management application provided by eWorkforce, which facilitates workflow planning and supply management for service appointments like installations and repairs.

Tenants (eWorkforce customers) create tasks for their customers, which are assigned to technicians working for eWorkforce, its workforce suppliers, or their subcontractors. Work orders are scheduled as needed, and warehouse operators handle supply requests.

The policy defines access rules for eWorkforce employees and specific tenants, such as PowerProtection (a power protection service provider) and TelCo (a telecommunications provider). Permissions to view, assign, and complete tasks depend on factors such as the user’s role, task assignments, managerial supervision, and contract associations within eWorkforce.

This policy is available as a case study in *Decat et al. (2014)*, which provides further details.

**Reference**: Maarten Decat, Jasper Bogaerts, Bert Lagaisse, and Wouter Joosen. *The workforce management case study: functional analysis and access control requirements.* CW Reports CW655,
Department of Computer Science, KU Leuven, February 2014.

## Attributes

### Subject/User Attributes
The subjects of this policy are employees of the system, including managers, helpdesk operators, warehouse operators, and technicians. The following attributes are used to describe the subjects.

| Attribute Name      | Multiplicity, Type     | Description                                               | Example Values                                     |
|--------------------|------------------|-----------------------------------------------------------|--------------------------------------------------|
| uid          | Single, String   | User’s unique identifier                                  | wfmgr001, tech001, etc.                         |
| position          | Single, String   | User's job role or title within the organization.        | workforceManager, technician, etc.             |
| department        | Single, String   | Department to which the user belongs.                     | workforce, warehouse, etc.                      |
| provider         | Single, String   | Organization who is providing the employee               | eWorkforce, telco, powerProtection, subContractor, etc |
| assignedTenant    | Single, String   | Tenant or subtenant assigned to the user for responsibilities. | telco, powerProtection                          |
| assignedRegion    | Single, String   | Region assigned to the user for work.                     | north, south                                    |
| managedStaff      | Multi, Set\<String>  | Staff assigned to a manager. (i.e. technicians assigned to a workforce manager) | {tech001, tech002}, etc. |
| certifications    | Multi, Set\<String>  | Certifications the user holds.                            | {telcoCertifiedTechnician, powerProtectionSpecialist}, etc. |
| isCustomerSupport | Single, Boolean     | Indicates whether a user is customer support or not.     | True, False                                     |
| group            | Single, String   | Indicates which group a user belongs to.                  | residentialSupport, companySupport, provisioning, techSupport |

### Resource Attributes
The resources of this system include work orders, contracts, tasks, resource requests, and stock refill requests. The following attributes are used to describe the resources.

| Attribute Name      | Multiplicity, Type     | Description                                               | Example Values                                     |
|--------------------|------------------|-----------------------------------------------------------|--------------------------------------------------|
| rid      | Single, String   | Resource’s unique identifier                             | contract001, workorder001, task001, etc.               |
| type             | Single, String   | Type of resource being accessed.                        | contract, workOrder, task, etc.                        |
| department       | Single, String   | Department associated with the resource                 | workforce, warehouse                             |
| tenant          | Single, String   | Tenant which a resource belongs to                      | telco, powerProtection                           |
| tenantType      | Single, String   | Type of tenant associated with the resource.            | primary, subtenant                               |
| resourceRegion   | Single, String   | Region in which the task or work order is executed.    | north, south                                     |
| contractStatus   | Single, String   | Status of the related contract or project.              | active, inactive                                |
| associatedContract | Single, String | Contract which a work order belongs to                 | contract001, contract002, etc.                                    |
| associatedWorkOrder | Single, String | Work order which a task belongs to                     | workorder001, workorder002, etc.                                     |
| createdBy       | Single, String   | Employee who created a work order.                     | wfmgr001, tech001, etc.                                         |
| assignedTechnician | Single, String | Technician assigned to complete a specific task or work order. | tech001, tech002, etc. |
| assignedEmployee | Single, String   | Employee assigned to a resource (primarily used for warehouse operators and requests) | whop001, whop002, etc. |
| requiredCertifications | Multi, Set\<String> | Certifications required to execute a specific work order or task. | {telcoCertifiedTechnician, powerProtectionSpecialist}, etc. |
| recurrence       | Single, Boolean     | Indicates whether a work order is one-time or recurring. | True, False                                     |
| isAppointment   | Single, Boolean     | Indicates whether a work order is an appointment. Only appears when recurrence is false. | True, False |
| isComplete   | Single, Boolean     | Indicates whether a resource request or stock refill request has been marked as complete. | True, False |

## Rules Set
This section defines the policy rules. SubCond (subject condition) specifies requirements related to the subject’s attributes, while ResCond (resource condition) defines conditions based on resource attributes. cons (constraint) applies conditions that depend on both subject and resource attributes.


### eWorkforce
#### eWorkforce Helpdesk

- Rule 1:  Only helpdesk operators can create work orders that apply to active contracts of a Primary Tenant for which he/she is assigned responsible. 

```rule 1
subCond: provider ∈ {eWorkforce}, position ∈ {helpdeskOperator}
resCond: type ∈ {contract}, contractStatus ∈ {active}, tenantType ∈ {primary}
cons: assignedTenant = tenant
actions: {createOneTimeWorkOrder, createRecurrentWorkOrder}
```

- Rule 2: Helpdesk operators can only modify or remove work orders that apply to active contracts of a Primary Tenant for which he/she is assigned responsible.
```rule 2
subCond: provider ∈ {eWorkforce}, position ∈ {helpdeskOperator}
resCond: type ∈ {workOrder}, contractStatus ∈ {active}, tenantType ∈ {primary}
cons: assignedTenant = tenant
actions: {modify, delete}
```

#### Application Admins
- Rule 3: Application admins can create appointments for all tenants of eWorkforce.
```rule 3
subCond: provider ∈ {eWorkforce}, position ∈ {applicationAdmin}
resCond: type ∈ {contract}
cons: 
actions: {createAppointment}
```

- Rule 4: Application admins can modify and delete appointments for all tenants of eWorkforce.
```rule 4
subCond: provider ∈ {eWorkforce}, position ∈ {applicationAdmin}
resCond: type ∈ {workOrder}, isAppointment ∈ {True}
cons: 
actions: {modify, delete}
```

#### Internal Workforce
- Rule 5: Only employees of the workforce team can access tasks.
```rule 5
subCond: provider ∈ {eWorkforce}, department ∈ {workforce}
resCond: type ∈ {task}
cons: 
Actions: {view}
```

- Rule 6: Employees can only access tasks of customers which relate to their department. Employees can only access tasks of active projects/contracts.
```rule 6
subCond: provider ∈ {eWorkforce}
resCond: type ∈ {task}, contractStatus ∈ {active}
cons: department = department
actions: {view}
```

- Rule 7: Technicians can only view and complete tasks that are assigned to them.
```rule 7
subCond: provider ∈ {eWorkforce}, position ∈ {technician}
resCond: type ∈ {task}
cons: uid = assignedTechnician
actions: {view, complete}
```

- Rule 8: Workforce Managers can view and complete all tasks assigned to a Technician for which they are assigned responsible.
```rule 8
subCond: provider ∈ {eWorkforce}, position ∈ {workforceManager}
resCond: type ∈ {task}
cons: managedStaff ∋ assignedTechnician
actions: {view, complete}
```

#### Internal Warehouse

- Rule 9: All warehouse managers can mark a stock refill request sent to the warehouse as completed.
```rule 9
subCond: provider ∈ {eWorkforce}, position ∈ {warehouseManager} 
resCond: type ∈ {stockRefillRequest} 
cons: 
actions: {markComplete}
```

- Rule 10: A warehouse operator can only view or complete resource requests assigned to him/her.
```rule 10
subCond: provider ∈ {eWorkforce}, position ∈ {warehouseOperator}
resCond: type ∈ {resourceRequest}
cons: assignedEmployee = uid
actions: {view, complete}
```

- Rule 11: A warehouse manager can view and complete any resource request assigned to any warehouse operator of the warehouse.
```rule 11
subCond: provider ∈ {eWorkforce}, position ∈ {warehouseManager}
resCond: type ∈ {resourceRequest}
cons: managedStaff ∋ assignedEmployee
actions: {view, complete}
```

### PowerProtection

#### Sales Managers
- Rule 12: All sales managers can create work orders. Sales managers can only create one-time work orders.
```rule 12
subCond: provider ∈ {powerProtection}, position ∈ {salesManager}
resCond: type ∈ {contract}, tenant ∈ {powerProtection}
cons:  
actions: {createOneTimeWorkOrder}
```

- Rule 13: All sales managers can view all work orders.
```rule 13
subCond: provider ∈ {powerProtection}, position ∈ {salesManager}
resCond: type ∈ {workOrder}, tenant ∈ {powerProtection}
cons: 
actions: {view}
```

#### Maintenance Managers
- Rule 14: All maintenance managers can create work orders. Maintenance managers can create one-time and recurrent work orders.
```rule 14
subCond: provider ∈ {powerProtection}, position ∈ {maintenanceManager}
resCond: type ∈ {contract}, tenant ∈ {powerProtection}
cons: 
actions: {createOneTimeWorkOrder, createRecurrentWorkOrder}
```

#### Stock Refill Notifications
- Rule 15: Only members of the Provisioning group can receive stock refill notifications.
```rule 15
subCond: provider ∈ {powerProtection}, group ∈ {provisioning}
resCond: type ∈ {stockRefillRequest}, tenant ∈ {powerProtection}
cons: 
actions: {receive}
```

### TelCo

#### Work Orders
- Rule 16: Every employee of TelCo who is a member of Customer Support can use the application to create work orders.
```rule 16
subCond: provider ∈ {telco}, isCustomerSupport ∈ {True}
resCond: type ∈ {contract}, tenant ∈ {telco}
cons:  
actions: {createOneTimeWorkOrder}
```

- Rule 17: Members of Customer Support who are part of the Company Support group can only send one-time work orders. They can also create recurring work orders if they are Sales Managers or Maintenance Managers.
```rule 17
subCond: provider ∈ {telco}, isCustomerSupport ∈ {True}, group ∈ {companySupport}, position ∈ {salesManager, maintenanceManager}
resCond: type ∈ {contract}, tenant ∈ {telco}
cons: 
actions: {createOneTimeWorkOrder, createRecurrentWorkOrder}
```

- Rule 18: Only Members of Customer Support who are part of the Residential Support group and are Maintenance Managers can create recurring work orders; the rest can only create one-time work orders.
```rule 18
subCond: provider ∈ {telco}, position ∈ {maintenanceManager}, isCustomerSupport ∈ {True}, group ∈ {residentialSupport}
resCond: type ∈ {contract}, tenant ∈ {telco} 
cons: 
actions: {createRecurrentWorkOrder}
```

#### Stock Refill Notifications
- Rule 19: Only members of Technician Support can receive stock refill notifications.
```rule 19
subCond: provider ∈ {telco}, group ∈ {techSupport} 
resCond: type ∈ {stockRefillRequest}, tenant ∈ {telco} 
cons:  
actions: {receive}
```

### Helpdesk Supplier

#### Helpdesk Operators
- Rule 20: All Helpdesk Operators can create a new work order.
```rule 20
subCond: provider ∈ {externalHelpdeskSupplier}, position ∈ {helpdeskOperator}
resCond: type ∈ {contract}
cons: 
actions: {createOneTimeWorkOrder, createRecurrentWorkOrder}
```

- Rule 21: All Helpdesk Operators can modify a new work order.
```rule 21
subCond: provider ∈ {externalHelpdeskSupplier}, position ∈ {helpdeskOperator} 
resCond: type ∈ {workOrder};
cons:  
actions: {modify}
```

#### Helpdesk Managers
- Rule 22: Helpdesk Managers can only view work orders. Helpdesk Managers can only view work orders created by Helpdesk Operators who are members of the team they are responsible for.
```rule 22
subCond: provider ∈ {externalHelpdeskSupplier}, position ∈ {helpdeskManager}
resCond: type ∈ {workOrder}
cons: managedStaff ∋ createdBy
actions: {view}
```

### Workforce Supplier

#### General
- Rule 23: Only Technicians or Workforce Managers can access tasks. Employees of a Workforce Supplier can only access tasks of customers which relate to their department. Employees of a Workforce Supplier can only access tasks of active projects/contracts.
```rule 23
subCond: provider ∈ {externalWorkforceSupplier}, position ∈ {workforceManager, technician}
resCond: type ∈ {task}, contractStatus ∈ {active}
cons: department = department
actions: {view}
```

#### Technicians
- Rule 24: Technicians can only view and complete tasks that are assigned to them.
```rule 24
subCond: provider ∈ {externalWorkforceSupplier}, position ∈ {technician} 
resCond: type ∈ {task}
cons: uid = assignedTechnician
actions: {view, complete}
```

#### Workforce Managers
- Rule 25: Workforce Managers can view and complete all tasks assigned to a Technician for whom they are responsible.
```rule 25
subCond: provider ∈ {externalWorkforceSupplier}, position ∈ {workforceManager} 
resCond: type ∈ {task}; 
cons: managedStaff ∋ assignedTechnician
actions: {view, complete}
```

### Subcontractor

#### General
- Rule 26: Only Technicians or Workforce Managers can access tasks. Employees of a Workforce Supplier can only access tasks of customers which relate to their department. Employees of a Workforce Supplier can only access tasks of active projects/contracts.
```rule 26
subCond: provider ∈ {subcontractor}, position ∈ {workforceManager, technician}
resCond: type ∈ {task}, contractStatus ∈ {active}
cons: department = department
actions: {view}
```

#### Technicians
- Rule 27: Technicians can only view and complete tasks that are assigned to them.
```rule 27
subCond: provider ∈ {subcontractor}, position ∈ {technician}
resCond: type ∈ {task}
cons: uid = assignedTechnician
actions: {view, complete}
```

#### Workforce Managers
- Rule 28: Workforce Managers can view and complete all tasks assigned to a Technician in their team.
```rule 28
subCond: provider ∈ {subcontractor}, position ∈ {workforceManager} 
resCond: type ∈ {task} 
cons: managedStaff ∋ assignedTechnician
actions: {view, complete}
```


