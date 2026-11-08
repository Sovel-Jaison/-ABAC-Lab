import time
import statistics
from core.myabac import parse_abac_file, process_request

POLICY = "DATASETS\\edocument\\edocument.abac"

user_mgr, res_mgr, rule_mgr = parse_abac_file(POLICY)

actions = ["view", "send", "search", "readMetaInfo"]

requests = []

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

            requests.append(
                (
                    user_id,
                    resource_id,
                    action,
                    same_tenant
                )
            )


print()
print("=" * 75)
print("PERFORMANCE BENCHMARK: E1 vs E2")
print("=" * 75)

print(f"Requests prepared: {len(requests)}")

# ---------------------------------------------------------
# Warm-up
# ---------------------------------------------------------

for user_id, resource_id, action, same_tenant in requests[:1000]:

    request = f"{user_id},{resource_id},{action}"

    process_request(
        request,
        user_mgr,
        res_mgr,
        rule_mgr
    )

    if not same_tenant:
        continue


# ---------------------------------------------------------
# E1 benchmark
# ---------------------------------------------------------

e1_times = []

for run in range(3):

    start = time.perf_counter()

    permits = 0

    for user_id, resource_id, action, same_tenant in requests:

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
# E2 benchmark
# ---------------------------------------------------------

e2_times = []

for run in range(3):

    start = time.perf_counter()

    permits = 0

    for user_id, resource_id, action, same_tenant in requests:

        # Proposed tenant-boundary check
        if not same_tenant:
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

e1_avg = statistics.mean(e1_times)
e2_avg = statistics.mean(e2_times)

e1_per_request = (e1_avg / len(requests)) * 1000000
e2_per_request = (e2_avg / len(requests)) * 1000000

e1_throughput = len(requests) / e1_avg
e2_throughput = len(requests) / e2_avg

print()
print("-" * 75)
print("OVERALL RESULTS")
print("-" * 75)

print(f"E1 average execution time : {e1_avg:.6f} seconds")
print(f"E2 average execution time : {e2_avg:.6f} seconds")

print(f"E1 average/request        : {e1_per_request:.3f} microseconds")
print(f"E2 average/request        : {e2_per_request:.3f} microseconds")

print(f"E1 throughput             : {e1_throughput:.2f} requests/sec")
print(f"E2 throughput             : {e2_throughput:.2f} requests/sec")


if e1_avg > 0:

    overhead = ((e2_avg - e1_avg) / e1_avg) * 100

    print(
        f"E2 time change            : "
        f"{overhead:.4f}%"
    )


# ---------------------------------------------------------
# Same-tenant benchmark
# ---------------------------------------------------------

same_requests = [
    x for x in requests
    if x[3]
]

cross_requests = [
    x for x in requests
    if not x[3]
]

print()
print("-" * 75)
print("WORKLOAD COMPOSITION")
print("-" * 75)

print(f"Same-tenant requests      : {len(same_requests)}")
print(f"Cross-tenant requests     : {len(cross_requests)}")


# ---------------------------------------------------------
# Same tenant E1
# ---------------------------------------------------------

start = time.perf_counter()

for user_id, resource_id, action, same_tenant in same_requests:

    request = f"{user_id},{resource_id},{action}"

    process_request(
        request,
        user_mgr,
        res_mgr,
        rule_mgr
    )

same_e1_time = time.perf_counter() - start


# ---------------------------------------------------------
# Same tenant E2
# ---------------------------------------------------------

start = time.perf_counter()

for user_id, resource_id, action, same_tenant in same_requests:

    if same_tenant:

        request = f"{user_id},{resource_id},{action}"

        process_request(
            request,
            user_mgr,
            res_mgr,
            rule_mgr
        )

same_e2_time = time.perf_counter() - start


# ---------------------------------------------------------
# Cross tenant E1
# ---------------------------------------------------------

start = time.perf_counter()

for user_id, resource_id, action, same_tenant in cross_requests:

    request = f"{user_id},{resource_id},{action}"

    process_request(
        request,
        user_mgr,
        res_mgr,
        rule_mgr
    )

cross_e1_time = time.perf_counter() - start


# ---------------------------------------------------------
# Cross tenant E2
# ---------------------------------------------------------

start = time.perf_counter()

for user_id, resource_id, action, same_tenant in cross_requests:

    if not same_tenant:
        decision = "Deny"

cross_e2_time = time.perf_counter() - start


print()
print("-" * 75)
print("SAME-TENANT PERFORMANCE")
print("-" * 75)

print(f"E1 time                  : {same_e1_time:.6f} seconds")
print(f"E2 time                  : {same_e2_time:.6f} seconds")

print(
    f"E1 average/request       : "
    f"{(same_e1_time / len(same_requests)) * 1000000:.3f} microseconds"
)

print(
    f"E2 average/request       : "
    f"{(same_e2_time / len(same_requests)) * 1000000:.3f} microseconds"
)


print()
print("-" * 75)
print("CROSS-TENANT PERFORMANCE")
print("-" * 75)

print(f"E1 time                  : {cross_e1_time:.6f} seconds")
print(f"E2 time                  : {cross_e2_time:.6f} seconds")

print(
    f"E1 average/request       : "
    f"{(cross_e1_time / len(cross_requests)) * 1000000:.3f} microseconds"
)

print(
    f"E2 average/request       : "
    f"{(cross_e2_time / len(cross_requests)) * 1000000:.3f} microseconds"
)

print()
print("=" * 75)
print("BENCHMARK COMPLETE")
print("=" * 75)
