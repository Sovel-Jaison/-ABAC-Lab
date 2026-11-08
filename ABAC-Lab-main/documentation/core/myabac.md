# Code Structure of `myabac.py`

## **Overview**

This script provides functionalities for processing ABAC (Attribute-Based Access Control) policies and performing various analyses, such as request evaluation, policy analysis, and resource access visualization. It allows for evaluation of requests, generates heatmaps for policy coverage, and produces bar charts for resource access statistics.

## Key Features

* Evaluates access requests based on ABAC policies.
* Performs policy file analysis, including rule and attribute coverage.
* Generates and visualizes heatmaps for rule and attribute mappings.
* Produces bar charts for top and least accessed resources.
* Supports command-line execution for different modes (`-e`, `-a`, `-b`).

## Imports

#### **Standard Library Imports**

* `sys`: For handling command-line arguments and application termination.

#### **Matplotlib and Seaborn Imports**

For plotting graphs and visualizations.

* `matplotlib.pyplot`: Used for plotting heatmaps and bar charts.
* `numpy`: Provides support for numerical operations, including matrix handling for heatmaps.
* `seaborn`: Used for creating the bar charts with better aesthetics.

#### **Core Imports**

Used for managing ABAC policy components.

* `UserManager`: For managing users and their attributes.
* `ResourceManager`: For managing resources and their attributes.
* `RuleManager`: For managing rules that govern access control.

## Functions

### `parse_abac_file(filename)`

**Purpose**:
Parses an ABAC policy file to extract users, resources, and rules.

**Parameters**:

| Parameter | Type | Description                  |
| --------- | ---- | ---------------------------- |
| filename  | str  | Path to the ABAC policy file |

**Return Value**:
Returns `UserManager`, `ResourceManager`, and `RuleManager` instances populated with data from the parsed ABAC file.

**Example Usage**:

```python
user_mgr, res_mgr, rule_mgr = parse_abac_file("policy.abac")
```

---

### `process_request(request, user_mgr, res_mgr, rule_mgr)`

**Purpose**:
Evaluates a given access request based on the ABAC policy.

**Parameters**:

| Parameter | Type            | Description                                                 |
| --------- | --------------- | ----------------------------------------------------------- |
| request   | str             | Access request in the format "<user>, <resource>, <action>" |
| user\_mgr | UserManager     | Manager containing user data                                |
| res\_mgr  | ResourceManager | Manager containing resource data                            |
| rule\_mgr | RuleManager     | Manager containing rules for access                         |

**Return Value**:
Returns either `'Permit'` or `'Deny'` based on the evaluation of the request.

**Example Usage**:

```python
decision = process_request("user1, resource1, read", user_mgr, res_mgr, rule_mgr)
```

---

### `generate_heatmap_data(user_mgr, res_mgr, rule_mgr)`

**Purpose**:
Generates heatmap data by evaluating the coverage of rules over user and resource attributes.

**Parameters**:

| Parameter | Type            | Description                         |
| --------- | --------------- | ----------------------------------- |
| user\_mgr | UserManager     | Manager containing user data        |
| res\_mgr  | ResourceManager | Manager containing resource data    |
| rule\_mgr | RuleManager     | Manager containing rules for access |

**Return Value**:
Returns a dictionary representing rule-to-attribute coverage, which is used for visualizing the heatmap.

**Example Output**:

```python
{
    0: {"user.name": 5, "resource.type": 3},
    1: {"user.role": 2, "resource.category": 4},
}
```

---

### `visualize_heatmap(heatmap)`

**Purpose**:
Visualizes the heatmap data using Matplotlib, displaying the relationship between rules and user/resource attributes.

**Parameters**:

| Parameter | Type | Description                                             |
| --------- | ---- | ------------------------------------------------------- |
| heatmap   | dict | The heatmap data generated from `generate_heatmap_data` |

**Example Usage**:

```python
visualize_heatmap(heatmap)
```

---

### `generate_bar_data(user_mgr, res_mgr, rule_mgr)`

**Purpose**:
Generates data for a bar chart that shows the resources with the highest and least number of subjects granted permissions.

**Parameters**:

| Parameter | Type            | Description                         |
| --------- | --------------- | ----------------------------------- |
| user\_mgr | UserManager     | Manager containing user data        |
| res\_mgr  | ResourceManager | Manager containing resource data    |
| rule\_mgr | RuleManager     | Manager containing rules for access |

**Return Value**:
Returns two lists of tuples, one for the top 10 resources with the highest access and one for the least.

**Example Output**:

```python
([("resource1", 50), ("resource2", 40)], [("resource5", 10), ("resource6", 5)])
```

---

### `plot_bar_data(top_10_resources, least_10_resources)`

**Purpose**:
Visualizes the top and least accessed resources in bar chart format using Matplotlib and Seaborn.

**Parameters**:

| Parameter            | Type | Description                                   |
| -------------------- | ---- | --------------------------------------------- |
| top\_10\_resources   | list | Top 10 resources with the most access counts  |
| least\_10\_resources | list | Top 10 resources with the least access counts |

**Example Usage**:

```python
plot_bar_data(top_10_resources, least_10_resources)
```

---

### `main()`

**Purpose**:
Handles the command-line execution of the script based on the provided flags and arguments (`-e`, `-a`, `-b`).

**Behavior**:

1. Executes in one of three modes: request evaluation, policy analysis, or resource analysis.
2. Uses the parsed policy file and performs actions like request evaluation, generating heatmaps, or bar chart generation.

**Example Usage**:

```bash
python myabac.py -e policy.abac request.txt
python myabac.py -a policy.abac
python myabac.py -b policy.abac
```

---

## Command-Line Options

* `-e <policy_file> <request_file>`: Evaluate access requests in the specified request file against the provided ABAC policy file.
* `-a <policy_file>`: Analyze the ABAC policy file and generate a heatmap visualizing rule and attribute coverage.
* `-b <policy_file>`: Generate and visualize bar charts showing the top and least accessed resources in the ABAC policy.

## Example Usage

```bash
# Evaluate requests
python myabac.py -e policy.abac requests.txt

# Analyze ABAC policy and visualize rule-attribute coverage
python myabac.py -a policy.abac

# Analyze resources and visualize access statistics
python myabac.py -b policy.abac
```

## Error Handling

* **Invalid Arguments**: Displays usage instructions when incorrect command-line arguments are provided.
* **File Not Found**: Handles file-related errors when the provided policy file is missing or inaccessible.

