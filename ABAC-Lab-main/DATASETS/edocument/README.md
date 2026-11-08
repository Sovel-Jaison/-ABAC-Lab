# Policy Description: Edocument

*Vesion: v20250324*

This policy governs a SaaS electronic document processing application provided by eDocs, which facilitates the secure distribution of digital and printed documents for various organizations.

Tenants (eDocs customers) use the application to send documents such as invoices, contracts, and notifications to their employees or customers. Documents can be delivered digitally via email, through postal services, or integrated with other platforms.

The policy defines access rules for eDocs employees and specific tenants, such as Large Bank and NewsAgency. Permissions to view, send, or manage documents depend on factors such as the user’s role, department, managerial supervision, and assigned projects within eDocs. 

This policy is available as a case study in *Decat et al. (2014)*, which provides further details.

**Reference**: Maarten Decat, Jasper Bogaerts, Bert Lagaisse, and Wouter Joosen. *The e-document case study: functional analysis and access control requirements.* CW Reports CW655,
Department of Computer Science, KU Leuven, February 2014.

## Attributes

### Subject Attributes
The subjects of this policy are users within the system, including employees, helpdesk operators, application admins, and customers. The following attributes are used to describe the subjects.

| Attribute Name       | Multiplicity, Type      | Description                                      | Example Values                                |
|---------------------|----------------------|--------------------------------------------------|---------------------------------------------|
| uid                | Single, String       | User’s unique identifier                         | user0, user1, user2, etc.                   |
| role               | Single, String       | Role which the user fulfills                    | employee, customer, admin, helpdesk         |
| position           | Single, String       | User's job role or title within the organization | secretary, director, officeManager, etc.    |
| tenant             | Single, String       | Organization to which the user belongs           | largeBank, largeBankLeasing, etc.           |
| department         | Single, String       | Department to which the user belongs             | largeBankSales, largeBankAudit, etc.        |
| office            | Single, String       | Office where the user is located                | largeBankOffice1, largeBankOffice2, etc.    |
| registered         | Single, Boolean      | Indicates if the user is registered in the system | True, False                                 |
| projects          | Multi, Set\<String>   | Projects the user is assigned to                 | Resources IDs                               |
| supervisor        | Single, String       | Supervisor that oversees the user                | User ID                                     |
| supervisee        | Multi, Set\<String>   | Supervisees that the user oversees               | User IDs                                    |
| payrollingPermissions | Single, Boolean  | Users that have permissions to do payrolling     | True, False                                 |

### Resource Attributes
Resources in the system include documents and other entities that users may access. The following attributes are used to describe the resources.

| Attribute Name         | Multiplicity, Type    | Description                                    | Example Values                                |
|-----------------------|--------------------|------------------------------------------------|---------------------------------------------|
| rid                  | Single, String     | Resource’s unique identifier                   | doc0, doc1, doc2, etc.                      |
| type                 | Single, String     | Type of resource being accessed                | invoice, contract, paycheck, bankingNote, etc. |
| owner                | Single, String     | User who owns the resource                     | User ID                                     |
| tenant               | Single, String     | Organization to which the resource belongs     | largeBank, largeBankLeasing, etc.           |
| department           | Single, String     | Department to which the resource belongs       | largeBankSales, largeBankAudit, etc.        |
| office              | Single, String     | Office where the resource is sent or assigned | largeBankOffice1, largeBankOffice2, etc.    |
| recipients          | Multi, Set\<String> | Users authorized to access the document       | User IDs                                    |
| isConfidential      | Single, Boolean    | Indicates if the document is confidential      | True, False                                 |
| containsPersonalInfo | Single, Boolean    | Indicates if the document contains personal data | True, False                             |

## Rules Set
This section defines the policy rules. SubCond (subject condition) specifies requirements related to the subject’s attributes, while ResCond (resource condition) defines conditions based on resource attributes. cons (constraint) applies conditions that depend on both subject and resource attributes.

### eDocs
#### General
- **Rule 1:** An Unregistered Receiver can only view documents sent to them.
```rule
subCond: role ∈ {customer}, registered ∈ {False}
resCond: 
cons: uid ∈ recipients
actions: {view}
```

#### Helpdesk
- **Rule 2:** Helpdesk members can search and view meta-information of documents in the application.
```rule
subCond: role ∈ {helpdesk}
resCond: 
cons: uid ∈ recipients
actions: {search, readMetaInfo}
```

- **Rule 3:** Helpdesk members can only read the content of documents belonging to tenants they are assigned responsible for.
```rule
subCond: role ∈ {helpdesk}
resCond: isConfidential ∈ {False}
cons: tenant = tenant
actions: {search, readMetaInfo}
```

#### Application Admins
- **Rule 4:** Application admins can view documents that are not confidential.
```rule
subCond: role ∈ {admin}
resCond: isConfidential ∈ {False}
cons: 
actions: {view}
```

### Large Bank
#### Supervisees
- **Rule 5:** A supervisor can read documents sent by their supervisees.
```rule
subCond: role ∈ {employee}, registered ∈ {True}, tenant ∈ {largeBank}
resCond: 
cons: supervisee = owner
actions: {view}
```

#### Projects
- **Rule 6:** A project member can read all sent documents related to the project.
```rule
subCond: role ∈ {employee}, tenant ∈ {largeBank}
resCond: 
cons: projects ∋ {rid}
actions: {view}
```

#### Invoices
- **Rule 7:** Only members of the sales department can send, view, or search invoices.
```rule
subCond: role ∈ {employee}, department ∈ {largeBankSales}
resCond: type ∈ {invoice}
cons: 
actions: {send, view, search}
```

#### Banking Notes
- **Rule 8:** Only members of the ICT department can send banking notes and view their status.
```rule
subCond: role ∈ {employee}, department ∈ {largeBankICT}
resCond: type ∈ {bankingNote}
cons: 
actions: {send, readMetaInfo}
```

#### Paychecks
- **Rule 9:** Only employees responsible for payrolling can send and view paychecks.
```rule
subCond: role ∈ {employee}, tenant ∈ {largeBank}, payrollingPermissions ∈ {True}
resCond: type ∈ {paycheck}
cons: 
actions: {send, view}
```

#### Sales Offers
- **Rule 10:** Only sales department members can send sales offers.
```rule
subCond: role ∈ {employee}, department ∈ {largeBankSales}
resCond: type ∈ {salesOffer}
cons: 
actions: {send}
```

#### Internal Communication with Local Bank Offices
- **Rule 11:** Only the bank office manager can send documents.
```rule
subCond: role ∈ {employee}, tenant ∈ {largeBank}, position ∈ {officeManager, seniorOfficeManager}
resCond: 
cons: 
actions: {send}
```

#### Audits
- **Rule 12:** Audit department members can read all invoices, offers, and documents except those containing personal information.
```rule
subCond: role ∈ {employee}, department ∈ {largeBankAudit}
resCond: type ∈ {invoice, salesOffer}, containsPersonalInfo ∈ {False}
cons: 
actions: {view}
```

### Large Bank Leasing
#### Traffic Fines
- **Rule 13:** Only members of Customer Care can view traffic fines.
```rule
subCond: role ∈ {employee}, department ∈ {largeBankLeasingCustomerCare}
resCond: type ∈ {trafficFine}
cons: 
actions: {view}
```

#### Invoices
- **Rule 14:** Only sales users can send invoices. Only Customer Care Office members can manually bill a customer.
```rule
subCond: role ∈ {employee}, department ∈ {largeBankLeasingSales, largeBankLeasingCustomerCare}
resCond: type ∈ {invoice}
cons: 
actions: {send}
```

### Local Bank Offices
#### Applicable Policies
- **Rule 15:** Only the secretary and office director can read documents sent to the bank office.
```rule
subCond: role ∈ {employee}, position ∈ {secretary, director}
resCond: 
cons: office = office
actions: {view}
```

### Car Leaser
#### Invoices
- **Rule 16:** Any member of the Accounting department can receive and read invoices.
```rule
subCond: role ∈ {customer}, department ∈ {carLeaserAccounting}
resCond: type ∈ {invoice}
cons: 
actions: {view}
```

### ICT Provider
#### Invoices
- **Rule 17:** Only secretary members can read invoices.
```rule
subCond: role ∈ {customer}, tenant ∈ {ictProviderSecretary}
resCond: type ∈ {invoice}
cons: 
actions: {view}
```

### NewsAgency
#### Applicable Policies
- **Rule 18:** Audit department members can read all invoices, offers, contracts, and paychecks.
```rule
subCond: role ∈ {employee}, department ∈ {newsAgencyAudit}
resCond: type ∈ {invoice, salesOffer, contract, paycheck}
cons: 
actions: {view}
```

### Europe Region
#### Contracts
- **Rule 19:** Only members of the HR department can send contracts.
```rule
subCond: role ∈ {employee}, department ∈ {europeRegionHR}
resCond: type ∈ {contract}
cons: 
actions: {send}
```

### London Office
#### Contracts
- **Rule 20:** Members of the Human Resources department can send contracts.
```rule
subCond: role ∈ {employee}, department ∈ {londonOfficeHR}
resCond: type ∈ {contract}
cons: 
actions: {send}
```

#### Invoices
- **Rule 21:** Any member of the Sales department can send invoices.
```rule
subCond: role ∈ {employee}, department ∈ {londonOfficeSales}
resCond: type ∈ {invoice}
cons: 
actions: {send}
```

- **Rule 22:** Any member of the Sales department can read all invoices sent by the department.
```rule
subCond: role ∈ {employee}, department ∈ {londonOfficeSales}
resCond: type ∈ {invoice}
cons: department = department
actions: {view}
```

### Reseller
#### Subtenant Document Viewing
- **Rule 23:** Only assigned Customer department members can read a subtenant's documents.
```rule
subCond: role ∈ {employee}, department ∈ {resellerCustomer}
resCond: 
cons: uid ∈ {recipients}
actions: {view}
```

#### Invoices
- **Rule 24:** Any member of the Accounting department can send invoices.
```rule
subCond: role ∈ {employee}, department ∈ {resellerAccounting}
resCond: type ∈ {invoice}
cons: 
actions: {view}
```

### Registered Private Receivers
#### Applicable Policies
- **Rule 25:** Registered Private Receivers can only read documents they received.
```rule
subCond: role ∈ {customer}, tenant ∈ {privateReceiver}
resCond: 
cons: uid ∈ {recipients}
actions: {view}
```

