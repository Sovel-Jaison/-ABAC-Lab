import sys
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from core.user import UserManager
from core.res import ResourceManager
from core.rule import RuleManager

def parse_abac_file(filename):
    """
    Delegate parsing based on what line contains (user, resource, or rule)

    Args:
        filename (str): path to file

    Returns:
        UserManager, ResourceManager, RuleManager: initalized objects poulated based on parsed abac
    """
    user_mgr = UserManager()
    res_mgr = ResourceManager()
    rule_mgr = RuleManager()

    with open(filename, 'r', encoding="UTF-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue

            if line.startswith('userAttrib'):
                user_mgr.parse_user_attrib(line)
            elif line.startswith('resourceAttrib'):
                res_mgr.parse_resource_attrib(line)
            elif line.startswith('rule'):
                rule_mgr.parse_rule(line)

    return user_mgr, res_mgr, rule_mgr

def process_request(request, user_mgr, res_mgr, rule_mgr):
    """
    Given a request in the form "<user>, <resource>, <action>" the function

    Args:
        request (str): request string to be evaluated
        user_mgr (UserManager): holds user data from abac
        res_mgr (ResourceManager): holds resources from abac
        rule_mgr (RuleManager): holds rules from abac

    Returns:
        str: 'Permit' or 'Deny'
    """
    sub_id, res_id, action = request.strip().split(',')

    user = user_mgr.get_user(sub_id)
    resource = res_mgr.get_resource(res_id)

    if not user or not resource:
        return "Deny"

    # Check if any rule permits the action
    for rule in rule_mgr.rules:
        if rule.evaluate(user, resource, action):
            return "Permit"

    return "Deny"

def generate_heatmap_data(user_mgr, res_mgr, rule_mgr):
    """
    Perform rule analysis and produce a heatmap  

    Arguments:
        user_mgr (UserManager): Manages users and their attributes.
        res_mgr (ResourceManager): Manages resources and their attributes.
        rule_mgr (RuleManager): Manages rules for authorization.

    Returns:
        None
    """
    heatmap = {}
    all_actions = set()
    for rule in rule_mgr.rules:
        all_actions.update(rule.acts)

    # Prepare attribute mappings and rule coverage
    for rule_idx, rule in enumerate(rule_mgr.rules):
        heatmap[rule_idx] = {}
        rule_attributes = rule.get_attributes()

        # Initialize attribute count for the rule
        for attr in rule_attributes["user"]:
            heatmap[rule_idx][f"user.{attr}"] = 0
        for attr in rule_attributes["resource"]:
            heatmap[rule_idx][f"resource.{attr}"] = 0

        # Evaluate rule over all users and resources
        for uid, user in user_mgr.users.items():
            for rid, resource in res_mgr.resources.items():
                for action in all_actions:
                    if rule.evaluate(user, resource, action):
                        # Increment counts for referenced attributes
                        for attr in rule_attributes["user"]:
                            if attr in user.attributes:
                                heatmap[rule_idx][f"user.{attr}"] += 1
                        for attr in rule_attributes["resource"]:
                            if attr in resource.attributes:
                                heatmap[rule_idx][f"resource.{attr}"] += 1

    # Display analysis results
    print("Policy Coverage Analysis Heatmap:")
    print("Rules vs. Attributes (counts of authorizations covered):\n")
    for rule_idx, attributes in heatmap.items():
        print(f"Rule {rule_idx}: {rule_mgr.get_rule(rule_idx).get_attributes()}")
        for attr, count in attributes.items():
            print(f"  {attr}: {count}")
        print()

    return heatmap


def visualize_heatmap(heatmap):
    """
    Visualize the heatmap using Matplotlib.
    
    Args:
        heatmap (dict): Heatmap data from rule object analysis.
        
    Returns:
        None
    """

    # Prepare data for visualization
    rules = list(heatmap.keys())
    attributes = sorted(list({attr for attrs in heatmap.values() for attr in attrs}))
    data = np.zeros((len(rules), len(attributes)))

    for rule_idx, attrs in heatmap.items():
        for attr, count in attrs.items():
            rule_pos = rules.index(rule_idx)
            attr_pos = attributes.index(attr)
            data[rule_pos, attr_pos] = count

    # Plot heatmap
    plt.figure(figsize=(10, 8))
    plt.imshow(data, cmap="Blues", interpolation="nearest")
    plt.xticks(ticks=range(len(attributes)), labels=attributes, rotation=90)
    plt.yticks(ticks=range(len(rules)), labels=[f"Rule {r}" for r in rules])
    plt.colorbar(label="Authorization Count")
    plt.title("Policy Coverage Analysis Heatmap")
    plt.xlabel("Attributes")
    plt.ylabel("Rules")
    plt.tight_layout()
    plt.show()

def generate_bar_data(user_mgr, res_mgr, rule_mgr):
    """
    Perform the resources analysis and return two bar data sets:
    - Top 10 resources with the highest number of subjects granted permissions.
    - Top 10 resources with the least number of subjects having permissions.

    Args:
        user_mgr (UserManager): Manages users and their attributes.
        res_mgr (ResourceManager): Manages resources and their attributes.
        rule_mgr (RuleManager): Manages rules for authorization.
    
    Returns:
        tuple: Two lists of tuples (resource, access count) for the top 10 resources with the highest and least access.
    """

    bar_data = {}
    all_actions = set()

    # Collect all actions from the rules
    for rule in rule_mgr.rules:
        all_actions.update(rule.acts)

    # Prepare attribute mappings and rule coverage
    for rid, resource in res_mgr.resources.items():
        resource_name = resource.get_name()
        bar_data[resource_name] = 0
        for uid, user in user_mgr.users.items():
            for rule_idx, rule in enumerate(rule_mgr.rules):
                # Evaluate if the resource is accessible
                for action in all_actions:
                    if rule.evaluate(user, resource, action):
                        bar_data[resource_name] += 1

    # Sort the resources by the number of subjects with access (highest to lowest)
    sorted_bar_data = dict(sorted(bar_data.items(), key=lambda item: item[1], reverse=True))

    # Get top 10 resources with the highest number of subjects
    top_10_resources = list(sorted_bar_data.items())[:10]
    # Get top 10 resources with the least number of subjects
    least_10_resources = list(sorted_bar_data.items())[-10:]

    return top_10_resources, least_10_resources

def plot_bar_data(top_10_resources, least_10_resources):
    # Create the subplot layout: 1 row, 2 columns
    fig, axes = plt.subplots(1, 2, figsize=(15, 6))

    # Plot the top 10 resources with the highest access (on the first subplot)
    visualize_bar(axes[0], top_10_resources, "Top 10 Resources with Highest Access")
    # Plot the top 10 resources with the least access (on the second subplot)
    visualize_bar(axes[1], least_10_resources, "Top 10 Resources with Least Access")

    # Display the plots
    plt.tight_layout()
    plt.show()


def visualize_bar(ax, data, title):
    """
    Helper function to plot a bar chart on a given axis.

    Args:
        ax (matplotlib.axes.Axes): The axis to plot on.
        data (list of tuples): List of tuples (resource, access count).
        title (str): The title for the bar chart.
    
    Returns:
        None
    """

    # Unzip the data into resources and access counts
    resources, access_count = zip(*data)

    # Convert access counts to float if necessary
    access_count = list(map(float, access_count))  # Ensure access_count is numeric

    # Create a seaborn barplot on the provided axis
    sns.barplot(x=access_count, y=resources, ax=ax, palette="Blues_d")  # Horizontal bar plot
    ax.set_xlabel("Number of Subjects")
    ax.set_ylabel("Resources")
    ax.set_title(title)

def main():
    if len(sys.argv) > 4 or (sys.argv[1] not in ['-e', '-a', '-b']):
        print("Usage: for request file evaluation python3 myabac.py -e <policy_file> <request_file>\n")
        print("for policy file analysis use  python3 myabac.py -a <policy_file> ")
        print("for resources analysis use  python3 myabac.py -b <policy_file> ")
        sys.exit(1)

    policy_file = sys.argv[2]

    # Parse the policy file
    user_mgr, res_mgr, rule_mgr = parse_abac_file(policy_file)

    if sys.argv[1] == "-e":
        request_file = sys.argv[3]
    # Process requests
        with open(request_file, 'r', encoding="UTF-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue

                decision = process_request(line, user_mgr, res_mgr, rule_mgr)
                print(f"{line}: {decision}")

    if sys.argv[1]=="-a":
        heatmap = generate_heatmap_data(user_mgr, res_mgr, rule_mgr)
        visualize_heatmap(heatmap)
 

    if sys.argv[1]=="-b":
        top10, least10 = generate_bar_data(user_mgr, res_mgr, rule_mgr)
        plot_bar_data(top10, least10)

if __name__ == "__main__":
    main()