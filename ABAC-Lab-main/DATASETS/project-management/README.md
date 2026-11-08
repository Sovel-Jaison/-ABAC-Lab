# Policy Description: Project Management 
*Vesion: v20250308*


This is a sample policy developed by Xu et al. (2015). The policy manages access by department managers, project leaders, employees, contractors, auditors, accountants, and planners to budgets,
schedules, and tasks associated with projects.

**Reference**: Zhongyuan Xu and Scott D. Stoller. *Mining attribute-based access control policies.* IEEE Transactions on Dependable and Secure Computing, 12(5):533–545, September–October 2015.

## Attributes

### Subject/User Attributes
The subjects of this policy include accountants, auditors, planners, managers, project leaders, and technical workers (designers and coders). The following attributes are used to describe the subjects.

| Attribute Name      | Multiplicity, Type     | Description                                               | Example Values                                     |
|--------------------|------------------|-----------------------------------------------------------|--------------------------------------------------|
| uid          | Single, String   | User’s unique identifier.                                  | acc1, aud2, etc.                         |
| adminRoles          | Multi, Set\<String>   | The user's administrative roles.        | {auditor, accountant}, etc.             |
| projects        | Multi, Set\<String>  | Projects the user is working on.                     | {proj11, proj12}, etc.                      |
| projectsLed         | Multi, Set\<String>   | projects led by the user. This is specified explicitly, instead of being implied by a user working on a project and having projectLeader among his administrative roles, because the user might work on some projects in non-leader roles.             | {proj21, proj22}, etc. |
| expertise    | Multi, Set\<String>   | The user's areas of technical expertise. | {design, coding}, etc.                          |
| tasks    | Multi, Set\<String>   | Tasks assigned to the user.                     | {proj11task1a, proj11task1propa}, etc.  |
| department    | Single, String   | The department that the user is in.                     | dept1, dept2, etc.  |
| isEmployee    | Single, Boolean    | Specifying if the user is an employee (True) or a contractor (False).                     | True, False  |


### Resource Attributes
The resources of this policy include budgets, schedules, and tasks for different projects. The following attributes are used to describe the resources.

| Attribute Name      | Multiplicity, Type     | Description                                               | Example Values                                     |
|--------------------|------------------|-----------------------------------------------------------|--------------------------------------------------|
| rid      | Single, String   | Resource’s unique identifier                             | proj11budget, proj11task1a, etc.               |
| type             | Single, String   | Type of resource being accessed.                        | task, budget, schedule                      |
| project       | Single, String   | The project that the task, schedule, or budget is for.                 | proj11, proj21, etc.                            |
| department          | Single, String   | The department that the associated project is in.                      | dept1, dept2, etc.                           |
| expertise      | Multi, Set\<String>   | The areas of technical expertise required to work on the task.            | {design, coding}, etc.                             |
| proprietary    | Single, Boolean    | Specifiying if the task involves proprietary information, which is accessible only to employees (not contractors).                     | True, False  |


## Rules Set
This section defines the policy rules. SubCond (subject condition) specifies requirements related to the subject’s attributes, while ResCond (resource condition) defines conditions based on resource attributes. cons (constraint) applies conditions that depend on both subject and resource attributes.

- Rule 1:  A project leader can read and write the project schedule and budget.

```rule 1
subCond: 
resCond: type ∈ {schedule, budget}
cons: projectsLed ∋ project
actions: {read, write}
```

- Rule 2: A user working on a project can read the project schedule. 
```rule 2
subCond: 
resCond: type ∈ {schedule}
cons: projects ∋ project
actions: {read}
```

- Rule 3: A user can update the status of tasks assigned to him/her.
```rule 3
subCond: 
resCond: type ∈ {task}
cons: tasks ∋ rid
actions: {setStatus}
```

- Rule 4: A user working on a project can read and request to work on a non-proprietary task whose required areas of expertise are among his/her areas of expertise.
```rule 4
subCond: 
resCond: type ∈ {task}, proprietary ∈ {False}
cons: projects ∋ project, expertise ⊇ expertise
actions: {read, request}
```

- Rule 5: An employee working on a project can read and request to work on any task whose required areas of expertise are among his/her areas of expertise
```rule 5
subCond: isEmployee ∈ {True}
resCond: type ∈ {task}
cons: projects ∋ project, expertise ⊇ expertise
actions: {read, request}
```
