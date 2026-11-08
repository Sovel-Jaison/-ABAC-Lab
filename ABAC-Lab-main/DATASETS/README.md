# .abac Files Description

*Vesion: v20250308*

This document outlines the format of .abac policy files. To ensure compatibility with the ABAC Lab application parser, please follow these guidelines when creating new policy files.

For a detailed description of the policy language, please refer to our paper: TBD.

Note that the two words "user" and "subject" are used interchangeably in this document.



#

An ABAC policy input file contains lines of the forms:

```
userAttrib(uid, attribute1=value1, attribute2=value2, ...)

resourceAttrib(rid, attribute1=value1, attribute2=value2, ...)
```

The `userAttrib` and `resourceAttrib` lines define the users (subjects) and resources in the policy, respectively.
- The first argument of a `userAttrib` is automatically assigned to an attribute named `uid`, which is the id of the user. 
The first argument of a `resourceAttrib` is automatically assigned to an attribute named `rid`, which is the id of the resource.  
- `value1`, `value2`, ... are atomic values or sets of atomic values.
	- An atomic value is a string that starts with a character other than a left curly brace.  
	- A set has the form `{element1 element2 ...}`. **Note that elements of a set are separated by spaces, not commas.**

<br/>

`userAttrib` and `resourceAttrib` statements must precede rule `statements` described below.

<br/>

```
rule(subCond; resCond; acts; cons)
```

The `rule` lines define the rules of the policy.

- `subCond` is a subject condition. It is a conjunction, with the conjuncts separated by commas. Each conjunct has the form 
`attr [ {value1 value2 ...}`, where `attr` is a single-valued user attribute and `[` denotes the "in" operator (note that elements of a set are separated by spaces, not commas), or 
`attr ] value`
, where attr is a muli-valued attribute, value is an atomic value, and `]` denotes the "contains" operator.

- `resCond` is a resource condition. The syntax is analogous to the syntax for subject condition.

- `acts` is a set of actions.

- `cons` is a constraint. It is a conjunction of atomic constraints, with the
conjuncts separated by commas. An atomic constraint is a formula of one of the following forms:
    ```
    aum > arm 
    aus [ arm
    aum ] ars
    aus = ars
    ```
    , where `aus` is a single-valued user attribute, `aum` is a multi-valued user attribute, `ars` is a single-valued resource attribute, and `arm` is a multi-valued resource attribute. Note that `>` denotes the "supseteq" (⊇) operator.



<br/>

```
# Comments
```
Lines starting with `#` are comments.

