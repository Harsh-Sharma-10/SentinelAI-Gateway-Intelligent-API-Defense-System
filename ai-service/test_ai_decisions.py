"""
Comprehensive AI Service Testing Suite
Tests all AI decision scenarios
"""
import sys
print(sys.executable)
import requests
import json
from datetime import datetime
from typing import Dict, Any

# AI Service URL
BASE_URL = "http://localhost:8000"

# Color codes for terminal output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    END = '\033[0m'
    BOLD = '\033[1m'

def print_header(text: str):
    """Print section header"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}{text}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.END}\n")

def print_test(test_name: str, passed: bool, details: str = ""):
    """Print test result"""
    status = f"{Colors.GREEN}✅ PASS{Colors.END}" if passed else f"{Colors.RED}❌ FAIL{Colors.END}"
    print(f"{status} | {test_name}")
    if details:
        print(f"     └─ {details}")

def create_request(ip: str, user_agent: str, method: str, endpoint: str,
                   request_count: int) -> Dict[str, Any]:
    """Helper to create request payload"""
    return {
        "ipAddress": ip,
        "userAgent": user_agent,
        "method": method,
        "endpoint": endpoint,
        "requestPath": endpoint,
        "requestCount": request_count,
        "timestamp": datetime.now().isoformat()
    }

def test_ai_decision(test_name: str, payload: Dict, expected_action: str,
                     expected_threat: str = None) -> bool:
    """Test AI decision endpoint"""
    try:
        response = requests.post(f"{BASE_URL}/predict", json=payload)

        if response.status_code != 200:
            print_test(test_name, False, f"HTTP {response.status_code}")
            return False

        result = response.json()

        # Check action
        action_match = result['action'] == expected_action

        # Check threat level if specified
        threat_match = True
        if expected_threat:
            threat_match = result['threat_level'] == expected_threat

        passed = action_match and threat_match

        details = (f"Action: {result['action']}, "
                   f"Threat: {result['threat_level']}, "
                   f"Confidence: {result['confidence']:.2f}, "
                   f"Reason: {result['reason'][:50]}...")

        print_test(test_name, passed, details)

        return passed

    except Exception as e:
        print_test(test_name, False, f"Error: {str(e)}")
        return False

def run_all_tests():
    """Run comprehensive test suite"""

    print_header("🧪 AI SERVICE COMPREHENSIVE TEST SUITE")

    total_tests = 0
    passed_tests = 0

    # ═══════════════════════════════════════════════════════════
    # CATEGORY 1: NORMAL BEHAVIOR (Should ALLOW)
    # ═══════════════════════════════════════════════════════════
    print_header("📊 Category 1: Normal User Behavior (Should ALLOW)")

    tests = [
        ("Normal browsing - Low frequency",
         create_request("192.168.1.100", "Mozilla/5.0 (Windows NT 10.0)",
                        "GET", "/api/products", 5),
         "ALLOW", "LOW"),

        ("Normal browsing - Medium frequency",
         create_request("192.168.1.101", "Mozilla/5.0 (iPhone; CPU iPhone)",
                        "GET", "/api/users", 15),
         "ALLOW", "LOW"),

        ("Legitimate mobile app",
         create_request("192.168.1.102", "MyApp/1.0 (Android 12)",
                        "POST", "/api/checkout", 10),
         "ALLOW", "LOW"),

        ("Normal API consumer",
         create_request("192.168.1.103", "Mozilla/5.0 (Macintosh; Intel Mac)",
                        "GET", "/api/products", 20),
         "ALLOW", None),
    ]

    for test in tests:
        total_tests += 1
        if test_ai_decision(*test):
            passed_tests += 1

    # ═══════════════════════════════════════════════════════════
    # CATEGORY 2: SUSPICIOUS FREQUENCY (Should BLOCK)
    # ═══════════════════════════════════════════════════════════
    print_header("📊 Category 2: Suspicious Request Frequency (Should BLOCK)")

    tests = [
        ("High frequency - 60 req/min",
         create_request("45.123.67.200", "Mozilla/5.0",
                        "GET", "/api/products", 60),
         "BLOCK", "HIGH"),

        ("Very high frequency - 90 req/min",
         create_request("45.123.67.201", "Mozilla/5.0",
                        "GET", "/api/products", 90),
         "BLOCK", "CRITICAL"),

        ("Burst pattern - 100 req/min",
         create_request("45.123.67.202", "Mozilla/5.0",
                        "GET", "/api/products", 100),
         "BLOCK", "CRITICAL"),

        ("Extreme frequency - 200 req/min",
         create_request("45.123.67.203", "Mozilla/5.0",
                        "GET", "/api/products", 200),
         "BLOCK", "CRITICAL"),
    ]

    for test in tests:
        total_tests += 1
        if test_ai_decision(*test):
            passed_tests += 1

    # ═══════════════════════════════════════════════════════════
    # CATEGORY 3: BOT USER AGENTS (Should BLOCK)
    # ═══════════════════════════════════════════════════════════
    print_header("📊 Category 3: Bot Detection via User Agent (Should BLOCK)")

    tests = [
        ("Python requests bot",
         create_request("192.168.1.200", "python-requests/2.28.1",
                        "GET", "/api/products", 5),
         "BLOCK", "HIGH"),

        ("Scrapy bot",
         create_request("192.168.1.201", "Scrapy/2.11.0",
                        "GET", "/api/products", 5),
         "BLOCK", "HIGH"),

        ("Generic crawler",
         create_request("192.168.1.202", "Mozilla/5.0 (compatible; Googlebot/2.1)",
                        "GET", "/api/products", 5),
         "BLOCK", "HIGH"),

        ("Wget bot",
         create_request("192.168.1.203", "Wget/1.21.3",
                        "GET", "/api/products", 5),
         "BLOCK", "HIGH"),

        ("Curl bot",
         create_request("192.168.1.204", "curl/7.88.1",
                        "GET", "/api/products", 5),
         "BLOCK", "HIGH"),

        ("Headless Chrome",
         create_request("192.168.1.205", "HeadlessChrome/120.0.0.0",
                        "GET", "/api/products", 5),
         "BLOCK", "HIGH"),
    ]

    for test in tests:
        total_tests += 1
        if test_ai_decision(*test):
            passed_tests += 1

    # ═══════════════════════════════════════════════════════════
    # CATEGORY 4: INVALID USER AGENTS (Should BLOCK)
    # ═══════════════════════════════════════════════════════════
    print_header("📊 Category 4: Invalid/Missing User Agents (Should BLOCK)")

    tests = [
        ("Missing user agent",
         create_request("192.168.1.210", "",
                        "GET", "/api/products", 5),
         "BLOCK", "MEDIUM"),

        ("Unknown user agent",
         create_request("192.168.1.211", "Unknown",
                        "GET", "/api/products", 5),
         "BLOCK", "MEDIUM"),

        ("Very short user agent",
         create_request("192.168.1.212", "App",
                        "GET", "/api/products", 5),
         "BLOCK", "MEDIUM"),
    ]

    for test in tests:
        total_tests += 1
        if test_ai_decision(*test):
            passed_tests += 1

    # ═══════════════════════════════════════════════════════════
    # CATEGORY 5: SENSITIVE ENDPOINTS (Should BLOCK with high frequency)
    # ═══════════════════════════════════════════════════════════
    print_header("📊 Category 5: Sensitive Endpoint Access (Should BLOCK)")

    tests = [
        ("Admin endpoint - High frequency",
         create_request("192.168.1.220", "Mozilla/5.0",
                        "GET", "/admin/users", 10),
         "BLOCK", "CRITICAL"),

        ("API admin - Medium frequency",
         create_request("192.168.1.221", "Mozilla/5.0",
                        "GET", "/api/admin/settings", 7),
         "BLOCK", "CRITICAL"),

        ("System endpoint",
         create_request("192.168.1.222", "Mozilla/5.0",
                        "GET", "/system/config", 6),
         "BLOCK", "CRITICAL"),
    ]

    for test in tests:
        total_tests += 1
        if test_ai_decision(*test):
            passed_tests += 1

    # ═══════════════════════════════════════════════════════════
    # CATEGORY 6: SCRAPING PATTERNS (Should BLOCK)
    # ═══════════════════════════════════════════════════════════
    print_header("📊 Category 6: Scraping Pattern Detection (Should BLOCK)")

    tests = [
        ("Sequential page access",
         create_request("192.168.1.230", "Mozilla/5.0",
                        "GET", "/api/products?page=247", 25),
         "BLOCK", "MEDIUM"),

        ("Sequential ID access",
         create_request("192.168.1.231", "Mozilla/5.0",
                        "GET", "/api/users/12345", 30),
         "BLOCK", "MEDIUM"),

        ("High freq + sequential",
         create_request("192.168.1.232", "Mozilla/5.0",
                        "GET", "/api/products?id=999", 50),
         "BLOCK", "HIGH"),
    ]

    for test in tests:
        total_tests += 1
        if test_ai_decision(*test):
            passed_tests += 1

    # ═══════════════════════════════════════════════════════════
    # CATEGORY 7: EDGE CASES
    # ═══════════════════════════════════════════════════════════
    print_header("📊 Category 7: Edge Cases and Boundary Conditions")

    tests = [
        ("Exactly at threshold - 29 req/min",
         create_request("192.168.1.240", "Mozilla/5.0",
                        "GET", "/api/products", 29),
         "ALLOW", "LOW"),

        ("Just over threshold - 31 req/min",
         create_request("192.168.1.241", "Mozilla/5.0",
                        "GET", "/api/products", 31),
         "ALLOW", "MEDIUM"),

        ("Exactly at suspicious - 50 req/min",
         create_request("192.168.1.242", "Mozilla/5.0",
                        "GET", "/api/products", 50),
         "BLOCK", "HIGH"),

        ("Very long user agent (legitimate)",
         create_request("192.168.1.243",
                        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                        "GET", "/api/products", 10),
         "ALLOW", "LOW"),
    ]

    for test in tests:
        total_tests += 1
        if test_ai_decision(*test):
            passed_tests += 1

    # ═══════════════════════════════════════════════════════════
    # CATEGORY 8: COMBINED THREAT FACTORS
    # ═══════════════════════════════════════════════════════════
    print_header("📊 Category 8: Multiple Threat Factors (Should BLOCK)")

    tests = [
        ("Bot + High frequency",
         create_request("192.168.1.250", "python-requests/2.28.1",
                        "GET", "/api/products", 60),
         "BLOCK", "CRITICAL"),

        ("Bot + Admin endpoint",
         create_request("192.168.1.251", "Scrapy/2.11.0",
                        "GET", "/admin/users", 5),
         "BLOCK", "CRITICAL"),

        ("High freq + Scraping pattern",
         create_request("192.168.1.252", "Mozilla/5.0",
                        "GET", "/api/products?page=500", 70),
         "BLOCK", "CRITICAL"),
    ]

    for test in tests:
        total_tests += 1
        if test_ai_decision(*test):
            passed_tests += 1

    # ═══════════════════════════════════════════════════════════
    # SUMMARY
    # ═══════════════════════════════════════════════════════════
    print_header("📊 TEST SUMMARY")

    success_rate = (passed_tests / total_tests) * 100

    print(f"{Colors.BOLD}Total Tests:{Colors.END} {total_tests}")
    print(f"{Colors.GREEN}Passed:{Colors.END} {passed_tests}")
    print(f"{Colors.RED}Failed:{Colors.END} {total_tests - passed_tests}")
    print(f"{Colors.CYAN}Success Rate:{Colors.END} {success_rate:.1f}%")

    if success_rate == 100:
        print(f"\n{Colors.GREEN}{Colors.BOLD}🎉 ALL TESTS PASSED! AI Service is working perfectly!{Colors.END}")
    elif success_rate >= 80:
        print(f"\n{Colors.YELLOW}{Colors.BOLD}⚠️  Most tests passed, but some improvements needed.{Colors.END}")
    else:
        print(f"\n{Colors.RED}{Colors.BOLD}❌ Many tests failed. AI Service needs attention!{Colors.END}")

    print()

if __name__ == "__main__":
    print(f"\n{Colors.BOLD}{Colors.CYAN}Starting AI Service Test Suite...{Colors.END}\n")
    print(f"{Colors.YELLOW}Make sure AI service is running on http://localhost:8000{Colors.END}\n")

    try:
        # Test if service is running
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print(f"{Colors.GREEN}✓ AI Service is running{Colors.END}\n")
            run_all_tests()
        else:
            print(f"{Colors.RED}✗ AI Service health check failed{Colors.END}")
    except requests.exceptions.ConnectionError:
        print(f"{Colors.RED}✗ Cannot connect to AI Service at {BASE_URL}{Colors.END}")
        print(f"{Colors.YELLOW}Please start the AI service first: python -m app.main{Colors.END}")