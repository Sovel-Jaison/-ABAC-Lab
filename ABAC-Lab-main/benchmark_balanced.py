import time
import random
from core.myabac import parse_abac_file, process_request

POLICY = "DATASETS\\edocument\\edocument.abac"

user_mgr, res_mgr, rule_mgr = parse_abac_file(POLICY)

actions = ["view", "send", "search", "readMetaInfo"]

same_requests = []
cross_requests = []

# ---------------------------------------------------------
# Build the complete request pools
# ---------------------------------------------------------

for user_num in range(500):

    user_id = f"user{user_num}"
    user = user_mgr.get_user(user_id)

    if not user:
        continue

    user_tenant = user.attributes.get("tenant")

    for doc_num in range(300):

        resource_id = f"doc{doc_num}"
        resource = res_mgr.get_resource(resource_id)

        if not resource:
            continue

        resource_tenant = resource.attributes.get("tenant")

        same_tenant = user_tenant == resource_tenant

        for action in actions:

            item = (
                user_id,
                resource_id,
                action
            )

            if same_tenant:
                same_requests.append(item)
            else:
                cross_requests.append(item)


# ---------------------------------------------------------
# Create balanced workload
# ---------------------------------------------------------

random.seed(42)

random.shuffle(same_requests)
random.shuffle(cross_requests)

N = min(
    len(same_requests),
    len(cross_requests)
)

same_sample = same_requests[:N]
cross_sample = cross_requests[:N]

balanced_requests = []

for same_item, cross_item in zip(
    same_sample,
    cross_sample
):

    balanced_requests.append(same_item)
    balanced_requests.append(cross_item)

random.shuffle(balanced_requests)


print()
print("=" * 75)
print("BALANCED WORKLOAD BENCHMARK: E1 vs E2")
print("=" * 75)

print(f"Same-tenant requests       : {len(same_sample)}")
print(f"Cross-tenant requests      : {len(cross_sample)}")
print(f"Total balanced requests    : {len(balanced_requests)}")


# ---------------------------------------------------------
# Warm-up
# ---------------------------------------------------------

for user_id, resource_id, action in balanced_requests[:1000]:

    request = f"{user_id},{resource_id},{action}"

    process_request(
        request,
        user_mgr,
        res_mgr,
        rule_mgr
    )


# ---------------------------------------------------------
# E1
# ---------------------------------------------------------

e1_times = []

for run in range(3):

    start = time.perf_counter()

    permits = 0

    for user_id, resource_id, action in balanced_requests:

        request = f"{user_id},{resource_id},{action}"

        decision = process_request(
            request,
            user_mgr,
            res_mgr,
            rule_mgr
        )

        if decision == "Permit":
            permits += 1

    elapsed = time.perf_counter() - start

    e1_times.append(elapsed)

    print(
        f"E1 Run {run + 1}: "
        f"{elapsed:.6f} seconds "
        f"({permits} permits)"
    )


# ---------------------------------------------------------
# E2
# ---------------------------------------------------------

e2_times = []

for run in range(3):

    start = time.perf_counter()

    permits = 0

    for user_id, resource_id, action in balanced_requests:

        user = user_mgr.get_user(user_id)
        resource = res_mgr.get_resource(resource_id)

        user_tenant = user.attributes.get("tenant")
        resource_tenant = resource.attributes.get("tenant")

        # Tenant boundary
        if user_tenant != resource_tenant:

            decision = "Deny"

        else:

            request = f"{user_id},{resource_id},{action}"

            decision = process_request(
                request,
                user_mgr,
                res_mgr,
                rule_mgr
            )

        if decision == "Permit":
            permits += 1

    elapsed = time.perf_counter() - start

    e2_times.append(elapsed)

    print(
        f"E2 Run {run + 1}: "
        f"{elapsed:.6f} seconds "
        f"({permits} permits)"
    )


# ---------------------------------------------------------
# Results
# ---------------------------------------------------------

e1_avg = sum(e1_times) / len(e1_times)
e2_avg = sum(e2_times) / len(e2_times)

total = len(balanced_requests)

e1_per_request = (
    e1_avg / total
) * 1_000_000

e2_per_request = (
    e2_avg / total
) * 1_000_000

e1_throughput = total / e1_avg
e2_throughput = total / e2_avg

time_change = (
    (e2_avg - e1_avg) /
    e1_avg
) * 100

print()
print("-" * 75)
print("BALANCED WORKLOAD RESULTS")
print("-" * 75)

print(f"E1 average execution time : {e1_avg:.6f} seconds")
print(f"E2 average execution time : {e2_avg:.6f} seconds")

print(f"E1 average/request        : {e1_per_request:.3f} microseconds")
print(f"E2 average/request        : {e2_per_request:.3f} microseconds")

print(f"E1 throughput             : {e1_throughput:.2f} requests/sec")
print(f"E2 throughput             : {e2_throughput:.2f} requests/sec")

print(f"E2 time change            : {time_change:.4f}%")

print()
print("=" * 75)
print("BALANCED BENCHMARK COMPLETE")
print("=" * 75)
