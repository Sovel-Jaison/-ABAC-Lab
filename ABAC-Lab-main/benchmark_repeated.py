#!/usr/bin/env python3
"""
benchmark_repeated.py -- repeated timing of E1 / E2 / E3 on the REAL ABAC Lab code path.

Same request construction and same timed code path as benchmark.py / benchmark_balanced.py
(f-string request -> core.myabac.process_request), but with repeated runs, several balanced
seeds, a cross-tenant sweep and the E3 (rewritten policy) variants.

Pipelines
---------
  E1       process_request on the original policy
  E2-flag  tenant check = pre-computed same_tenant flag (as in benchmark.py, natural workload)
  E2-look  tenant check done INSIDE the timed loop: get_user, get_resource, read both
           'tenant' attributes, compare (as in benchmark_balanced.py)
  E3-all   process_request on a policy with `tenant = tenant` appended to all 25 rules
  E3-aff   same, only for the 13 rules that produce a cross-tenant permit in E1

Timed region (all pipelines): building the request string "user,doc,action", the tenant
check (for E2), and process_request (string split, user/resource lookup, rule loop),
and permit counting. File parsing and workload construction are outside the timer.

Usage:  python benchmark_repeated.py DATASETS/edocument/edocument.abac --runs 15
Output: results_timing/timing_results.csv  (+ environment.json)
"""
import argparse, csv, gc, json, os, platform, random, statistics, sys, time

from core.myabac import parse_abac_file, process_request
from core.rule import Rule, RuleManager

ACTIONS = ["view", "send", "search", "readMetaInfo"]
AFFECTED = [7, 8, 9, 10, 11, 12, 13, 14, 18, 19, 20, 21, 24]   # from tenant_experiments.py audit


def patched_manager(rule_mgr, indices=None):
    rm = RuleManager()
    rm.rules = [Rule(r.sub_cond, r.res_cond, r.acts, list(r.cons) + [("tenant", "=", "tenant")])
                if (indices is None or i in indices) else r
                for i, r in enumerate(rule_mgr.rules, 1)]
    return rm


def build_pools(user_mgr, res_mgr):
    """Same enumeration as benchmark.py: user0..user499 x doc0..doc299 x 4 actions."""
    same, cross = [], []
    for un in range(500):
        uid = f"user{un}"
        u = user_mgr.get_user(uid)
        if not u:
            continue
        ut = u.attributes.get("tenant")
        for dn in range(300):
            rid = f"doc{dn}"
            r = res_mgr.get_resource(rid)
            if not r:
                continue
            is_same = ut == r.attributes.get("tenant")
            for a in ACTIONS:
                (same if is_same else cross).append((uid, rid, a))
    return same, cross


def run_e1(w, um, rm, ru):
    n = 0
    for u, r, a in w:
        if process_request(f"{u},{r},{a}", um, rm, ru) == "Permit":
            n += 1
    return n


def run_e2_flag(w, um, rm, ru, flags):
    n = 0
    for (u, r, a), same in zip(w, flags):
        if not same:
            d = "Deny"
        else:
            d = process_request(f"{u},{r},{a}", um, rm, ru)
        if d == "Permit":
            n += 1
    return n


def run_e2_look(w, um, rm, ru):
    n = 0
    for u, r, a in w:
        user = um.get_user(u)
        res = rm.get_resource(r)
        if user.attributes.get("tenant") != res.attributes.get("tenant"):
            d = "Deny"
        else:
            d = process_request(f"{u},{r},{a}", um, rm, ru)
        if d == "Permit":
            n += 1
    return n


def time_one(name, ratio, w, um, rm, ru, ru_all, ru_aff, runs, rng, rows):
    flags = [um.get_user(u).attributes.get("tenant") == rm.get_resource(r).attributes.get("tenant")
             for u, r, a in w]                                   # pre-computed OUTSIDE the timer
    pipes = {
        "E1": lambda: run_e1(w, um, rm, ru),
        "E2-flag": lambda: run_e2_flag(w, um, rm, ru, flags),
        "E2-look": lambda: run_e2_look(w, um, rm, ru),
        "E3-all": lambda: run_e1(w, um, rm, ru_all),
        "E3-aff": lambda: run_e1(w, um, rm, ru_aff),
    }
    for f in pipes.values():                                      # warm-up (first 1000 requests)
        pass
    for u, r, a in w[:1000]:
        process_request(f"{u},{r},{a}", um, rm, ru)
    samples = {k: [] for k in pipes}
    permits = {}
    gc.disable()
    try:
        for _ in range(runs):
            order = list(pipes)
            rng.shuffle(order)
            for k in order:
                t0 = time.perf_counter()
                p = pipes[k]()
                samples[k].append(time.perf_counter() - t0)
                permits[k] = p
    finally:
        gc.enable()
    for k, s in samples.items():
        for i, x in enumerate(s, 1):
            rows.append({"workload": name, "cross_ratio": ratio, "requests": len(w), "pipeline": k,
                         "run": i, "permits": permits[k], "elapsed_seconds": round(x, 6),
                         "microseconds_per_request": round(1e6 * x / len(w), 4)})
    base = statistics.mean(samples["E1"])
    print(f"{name:<22}n={len(w):>6}  " + "  ".join(
        f"{k} {statistics.mean(v):.4f}s({100*(statistics.mean(v)-base)/base:+.1f}%)" for k, v in samples.items()),
        flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("policy")
    ap.add_argument("--runs", type=int, default=15)
    ap.add_argument("--seeds", type=int, nargs="+", default=[42, 43, 44])
    ap.add_argument("--ratios", type=float, nargs="+", default=[0.0, 0.25, 0.5, 0.85, 1.0])
    ap.add_argument("--outdir", default="results_timing")
    a = ap.parse_args()
    os.makedirs(a.outdir, exist_ok=True)

    um, rm, ru = parse_abac_file(a.policy)
    ru_all = patched_manager(ru)
    ru_aff = patched_manager(ru, set(AFFECTED))
    same, cross = build_pools(um, rm)
    print(f"same={len(same)} cross={len(cross)} total={len(same)+len(cross)}", flush=True)

    rng = random.Random(0)
    rows = []
    # natural workload: same order as benchmark.py (user, doc, action)
    natural = []
    for un in range(500):
        uid = f"user{un}"
        if not um.get_user(uid):
            continue
        for dn in range(300):
            rid = f"doc{dn}"
            if not rm.get_resource(rid):
                continue
            for act in ACTIONS:
                natural.append((uid, rid, act))
    time_one("natural", round(len(cross) / len(natural), 4), natural, um, rm, ru, ru_all, ru_aff, a.runs, rng, rows)

    for seed in a.seeds:                                   # balanced: exact construction of benchmark_balanced.py
        s_list, c_list = list(same), list(cross)
        random.seed(seed)
        random.shuffle(s_list)
        random.shuffle(c_list)
        n = min(len(s_list), len(c_list))
        bal = []
        for si, ci in zip(s_list[:n], c_list[:n]):
            bal.append(si)
            bal.append(ci)
        random.shuffle(bal)
        time_one(f"balanced_seed{seed}", 0.5, bal, um, rm, ru, ru_all, ru_aff, a.runs, rng, rows)

    n = len(same)                                          # sweep at fixed size
    for ratio in a.ratios:
        r = random.Random(42)
        nc = round(n * ratio)
        w = r.sample(same, n - nc) + r.sample(cross, nc)
        r.shuffle(w)
        time_one(f"sweep_{int(ratio*100)}pct_cross", ratio, w, um, rm, ru, ru_all, ru_aff, a.runs, rng, rows)

    with open(os.path.join(a.outdir, "timing_results.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    cpu = "unknown"
    try:
        cpu = [l.split(":", 1)[1].strip() for l in open("/proc/cpuinfo") if l.startswith("model name")][0]
    except Exception:
        pass
    mem = None
    try:
        mem = round(int([l for l in open("/proc/meminfo") if l.startswith("MemTotal")][0].split()[1]) / 1048576, 2)
    except Exception:
        pass
    env = {"python": sys.version.split()[0], "platform": platform.platform(), "cpu_model": cpu,
           "logical_cpus": os.cpu_count(), "ram_gb": mem, "runs": a.runs, "seeds": a.seeds, "ratios": a.ratios}
    json.dump(env, open(os.path.join(a.outdir, "environment.json"), "w"), indent=2)
    print("done", env, flush=True)


if __name__ == "__main__":
    main()
