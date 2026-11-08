# Policy Description: University 
*Vesion: v20250308*


This is a sample policy developed by Xu et al. (2015). The policy manages access to university resources for students, instructors, teaching assistants (TAs), department chairs, and staff in the registrar’s and admissions offices. It defines access rules for applications (for admission), gradebooks, transcripts, and course schedules.

**Reference**: Zhongyuan Xu and Scott D. Stoller. *Mining attribute-based access control policies.* IEEE Transactions on Dependable and Secure Computing, 12(5):533–545, September–October 2015.

## Attributes

### Subject/User Attributes
The subjects of this policy include faculty, staff, students, and applicants within the university system. The following attributes are used to describe the subjects.

| Attribute Name      | Multiplicity, Type     | Description                                               | Example Values                                     |
|--------------------|------------------|-----------------------------------------------------------|--------------------------------------------------|
| uid          | Single, String   | User’s unique identifier.                                  | csStu1, csFac1, etc.                         |
| position          | Single, String   | The user's position.        | applicant, student, faculty, staff.             |
| department        | Single, String   | The user's main department, for faculty and staff.                     | cs, ee, registrar, etc.                      |
| crsTaken         | Multi, Set\<String>   | Set of courses taken by a student.             | {cs101, ee602}, etc. |
| crsTaught    | Multi, Set\<String>   | Set of courses for which the user is the instructor ( faculty) or TA (for students) | {cs101, ee602}, etc.                          |
| isChair    | Single, Boolean   | Specifying if a faculty is the chair of their department.                     | True, False  |


### Resource Attributes
The resources of this policy include applications, gradebooks, rosters, and transcripts within the university system. The following attributes are used to describe the resources.

| Attribute Name      | Multiplicity, Type     | Description                                               | Example Values                                     |
|--------------------|------------------|-----------------------------------------------------------|--------------------------------------------------|
| rid      | Single, String   | Resource’s unique identifier                             | cs101roster, ee602gradebook, etc.               |
| type             | Single, String   | Type of resource being accessed.                        | application, gradebook, roster, transcript                       |
| crs       | Single, String   | The course associated with the gradebook or roster                 | cs101, ee602                            |
| student          | Single, String   | The student associated with the transcript or application.                      | csStu1, eeStu3, etc.                           |
| departments      | Multi, Set\<String>   | The department the course is in (for gradebook and roster), and the student’s major department(s) (for transcript).            | {cs, ee}, etc.                            |


## Rules Set
This section defines the policy rules. SubCond (subject condition) specifies requirements related to the subject’s attributes, while ResCond (resource condition) defines conditions based on resource attributes. cons (constraint) applies conditions that depend on both subject and resource attributes.


### Rules for gradebooks

- Rule 1:  A user can read his/her own scores in gradebooks for courses they have taken.

```rule 1
subCond: 
resCond: type ∈ {gradebook}
cons: crsTaken ∋ crs
actions: {readMyScores}
```

- Rule 2: The instructor or TA can add scores and read scores in the gradebook for courses that they are teaching.
```rule 2
subCond: 
resCond: type ∈ {gradebook}
cons: crsTaught ∋ crs
actions: {addScore, readScore}
```

- Rule 3: The instructor for a course can change scores and assign final grades in the gradebook for that course.
```rule 3
subCond: position ∈ {faculty}
resCond: type ∈ {gradebook}
cons: crsTaught ∋ crs
actions: {changeScore, assignGrade}
```
### Rules for rosters

- Rule 4: A user in registrar’s office can read and modify all rosters.
```rule 4
subCond: department ∈ {registrar}
resCond: type ∈ {roster}
cons: 
actions: {read, write}
```

- Rule 5: The instructor of a course can read the course roster.
```rule 5
subCond: position ∈ {faculty}
resCond: type ∈ {roster}
cons: crsTaught ∋ crs
Actions: {read}
```
### Rules for transcripts

- Rule 6: A user can read their own transcript. 
```rule 6
subCond:
resCond: type ∈ {transcript}
cons: uid = student
actions: {read}
```

- Rule 7: The chair of a department can read the transcripts of all students in that department. 
```rule 7
subCond: isChair ∈ {True}
resCond: type ∈ {transcript}
cons: department ∈ departments
actions: {read}
```

- Rule 8: A user in the registrar’s office can read every student’s transcript.
```rule 8
subCond: department ∈ {registrar}
resCond: type ∈ {transcript}
cons: 
actions: {read}
```

### Rules for applications for admission

- Rule 9: A user can check the status of their own application. 
```rule 9
subCond:
resCond: type ∈ {application} 
cons: uid = student
actions: {checkStatus}
```

- Rule 10: A user in the admissions office can read and update the status of every application. 
```rule 10
subCond: department ∈ {admission}
resCond: type ∈ {application}
cons: uid = student
actions: {read, setStauts}
```
