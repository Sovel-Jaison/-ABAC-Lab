import os
import sys
import pprint
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from core.myabac import parse_abac_file, process_request, generate_bar_data, generate_heatmap_data

def test_hc_cases():
    abac_file_path = os.path.join('abac-files', 'healthcare.abac')
    solution_file_path = os.path.join('tests', 'eval-test-cases', 'healthcare-test-cases-solution.txt')
    request_file_path = os.path.join('tests', 'eval-test-cases', 'healthcare-test-cases.txt')

    with open(solution_file_path, "r", encoding="UTF-8") as hc_solutions:
        user_mgr, res_mgr, rule_mgr = parse_abac_file(abac_file_path)

        # Process requests
        with open(request_file_path, 'r', encoding="UTF-8") as request_file:
            for line_number, (request_line, solution_line) in enumerate(zip(request_file, hc_solutions), start=1):
                request_line = request_line.strip()
                solution_line = solution_line.strip()

                decision = process_request(request_line, user_mgr, res_mgr, rule_mgr)
                assert decision.lower() == solution_line.lower(), f"Assertion failed at line {line_number} for request: {request_line}. Expected: {solution_line}, Got: {decision}"

def test_uni_cases():
    abac_file_path = os.path.join('abac-files', 'university.abac')
    solution_file_path = os.path.join('tests', 'eval-test-cases', 'university-test-cases-solution.txt')
    request_file_path = os.path.join('tests', 'eval-test-cases', 'university-test-cases.txt')

    with open(solution_file_path, "r", encoding="UTF-8") as uni_solutions:
        user_mgr, res_mgr, rule_mgr = parse_abac_file(abac_file_path)

        # Process requests
        with open(request_file_path, 'r', encoding="UTF-8") as request_file:
            for line_number, (request_line, solution_line) in enumerate(zip(request_file, uni_solutions), start=1):
                request_line = request_line.strip()
                solution_line = solution_line.strip()

                decision = process_request(request_line, user_mgr, res_mgr, rule_mgr)
                assert decision.lower() == solution_line.lower(), f"Assertion failed at line {line_number} for request: {request_line}. Expected: {solution_line}, Got: {decision}"

def test_bar():
    abac_file_path = os.path.join('abac-files', 'bar-test.abac')
    top10_file_path = os.path.join('tests', 'eval-test-cases', 'bar-top-10-solution.txt')
    least10_file_path = os.path.join('tests', 'eval-test-cases', 'bar-least-10-solution.txt')

    with open(top10_file_path, "r", encoding="UTF-8") as top_10_solutions, open(least10_file_path, "r", encoding="UTF-8") as least_10_solutions:
        user_mgr, res_mgr, rule_mgr = parse_abac_file(abac_file_path)
        top_10, least_10 = generate_bar_data(user_mgr, res_mgr, rule_mgr)

        # conversion required to test against tuple generated from generate_bar_data()
        top_10_solutions = [tuple(line.strip().split(', ')) for line in top_10_solutions]
        least_10_solutions = [tuple(line.strip().split(', ')) for line in least_10_solutions]
        top_10_solutions = [(resource, int(count)) for resource, count in top_10_solutions]
        least_10_solutions = [(resource, int(count)) for resource, count in least_10_solutions]
        
        assert top_10 == top_10_solutions, f"Top 10 resources do not match. Expected: {top_10_solutions}, Got: {top_10}"
        assert least_10 == least_10_solutions, f"Least 10 resources do not match. Expected: {least_10_solutions}, Got: {least_10}"

def test_heatmap():
    abac_file_path = os.path.join('abac-files', 'bar-test.abac')
    expected_heatmap_path = os.path.join('tests', 'eval-test-cases', 'heatmap-solution.txt')

    # Load the expected heatmap results
    expected_heatmap = {}
    with open(expected_heatmap_path, "r", encoding="UTF-8") as file:
        for line in file:
            rule_idx, counts = line.strip().split('{')
            rule_idx = int(rule_idx)
            counts = int(counts.rstrip('}'))
            expected_heatmap[rule_idx] = counts

    # Parse the ABAC file and generate the heatmap
    user_mgr, res_mgr, rule_mgr = parse_abac_file(abac_file_path)
    heatmap = generate_heatmap_data(user_mgr, res_mgr, rule_mgr)

    for rule_idx, expected_count in expected_heatmap.items():
        actual_count = sum(heatmap[rule_idx].values())/len(heatmap[rule_idx])
        assert actual_count == expected_count, f"Count for rule {rule_idx} does not match. Expected: {expected_count}, Got: {actual_count}"

# Run pytest with the -s option to see print statements
