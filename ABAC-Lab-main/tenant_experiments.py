#!/usr/bin/env python3
"""
tenant_experiments.py  --  extra experiments for the tenant-boundary paper.

Place next to myabac.py (needs the `core` package: core.user, core.res, core.rule).

Usage
-----
  python tenant_experiments.py edocument.abac --users employees --runs 15
  python tenant_experiments.py edocument.abac --users all       --runs 15
  python tenant_experiments.py edocument.abac --skip-timing     # security/analysis only

What it produces (all in --outdir, default ./results)
-----------------------------------------------------
  security_summary.json    E1 / E2 / E3 permits, Eq.(4) check, E2-vs-E3 equivalence,
                           tenant-attribute sanity checks              -> Sec. IX-C, new IX-E
  rule_attribution.csv     per-rule cross-tenant counts, FIRST-MATCH and ALL-MATCH
                           (first-match sums to the unique permit count) -> Table IV
  recipients_summary.json  how many cross-tenant permits look like legitimate
                           sharing (requester / requester's tenant is a recipient)
                                                                       -> new IX-F, Limitations
  timing_results.csv       mean/SD/median over repeated runs, natural, balanced
                           (several seeds) and a cross-tenant-ratio sweep -> Sec. X
  ratio_sweep.png          (only if matplotlib is installed)

Configurations
--------------
  E1       original ABAC evaluator (first match wins)
  E2       tenant check (fail-closed on missing tenant) + E1
  E3_all   policy rewritten: constraint  tenant = tenant  appended to ALL rules
  E3_aff   same, but only to rules that produce >=1 cross-tenant permit in E1

Timed region = decision loop only (user/resource objects already retrieved; request
string parsing is excluded for ALL configurations). State this in Sec. VII-E.
"""
import argparse
import csv
import gc
import json
import os
import random
import re
import statistics
import time

from core.user import UserManager
from core.res import ResourceManager
from core.rule import Rule, RuleManager

TENANT = "tenant"


# ----------------------------------------------------------------------------- loading
def load_policy(path):
    um, rm, ru = UserManager(), ResourceManager(), RuleManager()
    with open(path, "r", encoding="UTF-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if line.startswith("userAttrib"):
                um.parse_user_attrib(line)
            elif line.startswith("resourceAttrib"):
                rm.parse_resource_attrib(line)
            elif line.startswith("rule"):
                ru.parse_rule(line)
    return um, rm, ru


def scan_file(path):
    """Regex scan (same patterns as check_shared.py / find_unknown.py)."""
    user_tenant, res_recipients = {}, {}
    with open(path, "r", encoding="UTF-8") as f:
        for line in f:
            if line.startswith("userAttrib("):
                m = re.match(r"userAttrib\(([^,]+)", line)
                t = re.search(r"(?:^|,\s*)tenant=([^,\s]+)", line)
                if m and t:
                    user_tenant[m.group(1).strip()] = t.group(1)
            elif line.startswith("resourceAttrib("):
                m = re.match(r"resourceAttrib\(([^,]+)", line)
                rec = re.search(r"recipients=\{([^}]*)\}", line)
                if m:
                    ids = (re.findall(r"\b(?:user|admin|cstmr|hdop)\d+\b", rec.group(1))
                           if rec else None)
                    res_recipients[m.group(1).strip()] = ids
    return user_tenant, res_recipients


def natural_key(s):
    return [int(t) if t.isdigit() else t for t in re.split(r"(\d+)", str(s))]


def select_users(um, mode):
    ids = list(um.users.keys())
    if mode == "employees":
        # employees = users whose role attribute is 'employee' (400 in E-Document)
        ids = [u for u in ids if um.users[u].get_attribute("role") == "employee"]
    return sorted(ids, key=natural_key)


# ----------------------------------------------------------------------------- decisions
def e1(u, r, a, rules):
    for rule in rules:
        if rule.evaluate(u, r, a):
            return True
    return False


def e2(u, r, a, rules):
    tu, tr = u.get_attribute(TENANT), r.get_attribute(TENANT)
    if tu is None or tr is None or tu != tr:      # fail closed
        return False
    return e1(u, r, a, rules)


def first_match(u, r, a, rules):
    for i, rule in enumerate(rules, 1):
        if rule.evaluate(u, r, a):
            return i
    return 0


def patch_rules(rules, indices_1based=None):
    """Return a NEW rule list with `tenant = tenant` appended to selected rules."""
    out = []
    for i, rule in enumerate(rules, 1):
        if indices_1based is None or i in indices_1based:
            out.append(Rule(rule.sub_cond, rule.res_cond, rule.acts,
                            list(rule.cons) + [(TENANT, "=", TENANT)]))
        else:
            out.append(rule)
    return out


# ----------------------------------------------------------------------------- requests
def build_requests(um, rm, rules, user_ids):
    acts = sorted({a for r in rules for a in r.acts})
    res_ids = sorted(rm.resources.keys(), key=natural_key)
    reqs = []   # (uid, rid, user, res, act, same_tenant)
    for uid in user_ids:
        u = um.users[uid]
        tu = u.get_attribute(TENANT)
        for rid in res_ids:
            r = rm.resources[rid]
            tr = r.get_attribute(TENANT)
            same = tu is not None and tu == tr
            for a in acts:
                reqs.append((uid, rid, u, r, a, same))
    return reqs, acts


def tenant_sanity(um, rm, user_ids):
    def bad(obj):
        v = obj.get_attribute(TENANT)
        return v is None or isinstance(v, (set, list, tuple))
    return {
        "users_checked": len(user_ids),
        "users_without_single_tenant": sum(bad(um.users[u]) for u in user_ids),
        "resources_checked": len(rm.resources),
        "resources_without_single_tenant": sum(bad(r) for r in rm.resources.values()),
    }


# ----------------------------------------------------------------------------- audit
def audit(reqs, rules, outdir):
    n = len(reqs)
    same_n = sum(1 for q in reqs if q[5])
    cross_n = n - same_n

    fm = [first_match(q[2], q[3], q[4], rules) for q in reqs]
    p1 = [m > 0 for m in fm]
    p1_same = sum(1 for p, q in zip(p1, reqs) if p and q[5])
    p1_cross = sum(1 for p, q in zip(p1, reqs) if p and not q[5])

    # real E2 implementation, compared against Eq.(4): Pi2 = Pi1 AND Qs
    p2 = [e2(q[2], q[3], q[4], rules) for q in reqs]
    eq4_violations = sum(1 for a, b, q in zip(p1, p2, reqs) if b != (a and q[5]))
    p2_same = sum(1 for p, q in zip(p2, reqs) if p and q[5])
    p2_cross = sum(1 for p, q in zip(p2, reqs) if p and not q[5])

    # rule-level attribution on cross-tenant permits of E1
    first_ct = {}
    all_ct = {}
    for (uid, rid, u, r, a, same), m in zip(reqs, fm):
        if same or m == 0:
            continue
        first_ct[m] = first_ct.get(m, 0) + 1
        for i, rule in enumerate(rules, 1):
            if rule.evaluate(u, r, a):
                all_ct[i] = all_ct.get(i, 0) + 1
    affected = sorted(all_ct)

    with open(os.path.join(outdir, "rule_attribution.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["rule", "first_match_cross_tenant", "all_match_cross_tenant"])
        for i in sorted(set(first_ct) | set(all_ct)):
            w.writerow([i, first_ct.get(i, 0), all_ct.get(i, 0)])
        w.writerow(["SUM", sum(first_ct.values()), sum(all_ct.values())])

    # E3 baselines (policy rewritten instead of external check)
    rules_all = patch_rules(rules)
    rules_aff = patch_rules(rules, set(affected))
    p3a = [e1(q[2], q[3], q[4], rules_all) for q in reqs]
    p3f = [e1(q[2], q[3], q[4], rules_aff) for q in reqs]

    summary = {
        "requests": n, "same_tenant_requests": same_n, "cross_tenant_requests": cross_n,
        "E1": {"permits": p1_same + p1_cross, "same": p1_same, "cross": p1_cross,
               "cross_permit_rate_pct": round(100 * p1_cross / cross_n, 4) if cross_n else None,
               "cross_share_of_permits_pct":
                   round(100 * p1_cross / (p1_same + p1_cross), 4) if (p1_same + p1_cross) else None},
        "E2": {"permits": p2_same + p2_cross, "same": p2_same, "cross": p2_cross},
        "eq4_violations": eq4_violations,
        "E3_all": {"rules_edited": len(rules), "permits": sum(p3a),
                   "decision_mismatches_vs_E2": sum(a != b for a, b in zip(p3a, p2))},
        "E3_affected": {"rules_edited": len(affected), "edited_rules": affected,
                        "permits": sum(p3f),
                        "decision_mismatches_vs_E2": sum(a != b for a, b in zip(p3f, p2))},
        "unique_cross_tenant_permits_first_match_sum": sum(first_ct.values()),
        "all_match_sum": sum(all_ct.values()),
    }
    return summary, fm, affected, rules_all, rules_aff


# ----------------------------------------------------------------------------- recipients
def recipients_analysis(reqs, fm, user_tenant, res_recipients, outdir):
    cats = {"no_recipients_attribute": 0, "requester_is_recipient": 0,
            "requester_tenant_is_recipient_tenant": 0,
            "only_unknown_recipients": 0, "recipients_in_other_tenants_only": 0}
    total = 0
    for (uid, rid, u, r, a, same), m in zip(reqs, fm):
        if same or m == 0:
            continue
        total += 1
        recs = res_recipients.get(rid)
        if not recs:
            cats["no_recipients_attribute"] += 1
            continue
        if uid in recs:
            cats["requester_is_recipient"] += 1
            continue
        known = [user_tenant[x] for x in recs if x in user_tenant]
        if not known:
            cats["only_unknown_recipients"] += 1
        elif u.get_attribute(TENANT) in known:
            cats["requester_tenant_is_recipient_tenant"] += 1
        else:
            cats["recipients_in_other_tenants_only"] += 1
    out = {"cross_tenant_permits_in_E1": total, **cats}
    with open(os.path.join(outdir, "recipients_summary.json"), "w") as f:
        json.dump(out, f, indent=2)
    return out


# ----------------------------------------------------------------------------- timing
def run_e1(w, rules):
    n = 0
    for u, r, a in w:
        for rule in rules:
            if rule.evaluate(u, r, a):
                n += 1
                break
    return n


def run_e2(w, rules):
    n = 0
    for u, r, a in w:
        tu, tr = u.get_attribute(TENANT), r.get_attribute(TENANT)
        if tu is None or tr is None or tu != tr:
            continue
        for rule in rules:
            if rule.evaluate(u, r, a):
                n += 1
                break
    return n


def time_workload(name, ratio, workload, configs, runs, rng, rows):
    """configs: {name: (runner, rules)}. Order is shuffled every run to avoid drift bias."""
    for runner, rules in configs.values():                       # warm-up
        runner(workload[: min(5000, len(workload))], rules)
    samples = {k: [] for k in configs}
    permits = {}
    gc.disable()
    try:
        for _ in range(runs):
            order = list(configs)
            rng.shuffle(order)
            for k in order:
                runner, rules = configs[k]
                t0 = time.perf_counter()
                p = runner(workload, rules)
                samples[k].append(time.perf_counter() - t0)
                permits[k] = p
    finally:
        gc.enable()
    base = statistics.mean(samples["E1"])
    for k, s in samples.items():
        mean = statistics.mean(s)
        rows.append({
            "workload": name, "cross_ratio": ratio, "requests": len(workload),
            "config": k, "runs": runs, "mean_s": round(mean, 6),
            "sd_s": round(statistics.stdev(s), 6) if runs > 1 else 0.0,
            "median_s": round(statistics.median(s), 6),
            "us_per_request": round(1e6 * mean / len(workload), 4),
            "permits": permits[k],
            "change_vs_E1_pct": round(100 * (mean - base) / base, 3),
        })


def timing_suite(reqs, rules, rules_all, rules_aff, runs, seeds, ratios, outdir):
    same = [(q[2], q[3], q[4]) for q in reqs if q[5]]
    cross = [(q[2], q[3], q[4]) for q in reqs if not q[5]]
    configs = {"E1": (run_e1, rules), "E2": (run_e2, rules),
               "E3_all": (run_e1, rules_all), "E3_aff": (run_e1, rules_aff)}
    rows = []
    rng = random.Random(0)

    time_workload("natural", round(len(cross) / len(reqs), 4), same + cross,
                  configs, runs, rng, rows)

    for s in seeds:                                   # balanced, one sample per seed
        r = random.Random(s)
        w = same + r.sample(cross, len(same))
        r.shuffle(w)
        time_workload(f"balanced_seed{s}", 0.5, w, configs, runs, rng, rows)

    n = len(same)                                     # ratio sweep, fixed size
    for ratio in ratios:
        r = random.Random(42)
        nc = round(n * ratio)
        w = r.sample(same, n - nc) + r.sample(cross, nc)
        r.shuffle(w)
        time_workload(f"sweep_{int(ratio * 100)}pct_cross", ratio, w,
                      configs, runs, rng, rows)

    path = os.path.join(outdir, "timing_results.csv")
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)

    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        plt.figure(figsize=(5, 3.4))
        for k in configs:
            pts = [(x["cross_ratio"] * 100, x["us_per_request"]) for x in rows
                   if x["workload"].startswith("sweep_") and x["config"] == k]
            plt.plot(*zip(*sorted(pts)), marker="o", label=k)
        plt.xlabel("Cross-tenant share of workload (%)")
        plt.ylabel("Avg. time per request (µs)")
        plt.legend()
        plt.grid(alpha=.3)
        plt.tight_layout()
        plt.savefig(os.path.join(outdir, "ratio_sweep.png"), dpi=300)
    except ImportError:
        pass
    return rows


# ----------------------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("abac")
    ap.add_argument("--users", choices=["employees", "all"], default="employees")
    ap.add_argument("--runs", type=int, default=15)
    ap.add_argument("--seeds", type=int, nargs="+", default=[42, 43, 44, 45, 46])
    ap.add_argument("--ratios", type=float, nargs="+",
                    default=[0.0, 0.1, 0.25, 0.5, 0.75, 0.85])
    ap.add_argument("--outdir", default="results")
    ap.add_argument("--skip-timing", action="store_true")
    args = ap.parse_args()
    os.makedirs(args.outdir, exist_ok=True)

    um, rm, ru = load_policy(args.abac)
    rules = ru.rules
    user_ids = select_users(um, args.users)
    user_tenant, res_recipients = scan_file(args.abac)
    print(f"users evaluated: {len(user_ids)}  resources: {len(rm.resources)}  rules: {len(rules)}")

    reqs, acts = build_requests(um, rm, rules, user_ids)
    print(f"requests: {len(reqs)}  actions: {acts}")

    summary, fm, affected, rules_all, rules_aff = audit(reqs, rules, args.outdir)
    summary["tenant_attribute_sanity"] = tenant_sanity(um, rm, user_ids)
    summary["users_mode"] = args.users
    with open(os.path.join(args.outdir, "security_summary.json"), "w") as f:
        json.dump(summary, f, indent=2)
    print(json.dumps(summary, indent=2))

    rec = recipients_analysis(reqs, fm, user_tenant, res_recipients, args.outdir)
    print("recipients analysis:", json.dumps(rec, indent=2))

    if not args.skip_timing:
        rows = timing_suite(reqs, rules, rules_all, rules_aff, args.runs,
                            args.seeds, args.ratios, args.outdir)
        for x in rows:
            print(f"{x['workload']:<26}{x['config']:<8}{x['mean_s']:>10.4f}s "
                  f"±{x['sd_s']:.4f}  {x['us_per_request']:>8.3f} µs/req  "
                  f"permits={x['permits']}  vs E1 {x['change_vs_E1_pct']:+.1f}%")
    print(f"\nresults written to {args.outdir}/")


if __name__ == "__main__":
    main()
