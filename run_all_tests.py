#!/usr/bin/env python3
"""Master test runner for all monitoring modules."""
import subprocess
import sys
from pathlib import Path


def run_tests(module_name: str, test_path: Path) -> bool:
    """Run tests for a specific module.
    
    Args:
        module_name: Name of the module
        test_path: Path to the test directory
        
    Returns:
        True if tests passed, False otherwise
    """
    print(f"\n{'='*70}")
    print(f"Running tests for: {module_name}")
    print(f"{'='*70}\n")
    
    if not test_path.exists():
        print(f"⚠️  Test directory not found: {test_path}")
        return True  # Skip if no tests
    
    try:
        result = subprocess.run(
            [sys.executable, '-m', 'pytest', str(test_path), '-v', '--tb=short'],
            cwd=Path.cwd(),
            check=False
        )
        
        if result.returncode == 0:
            print(f"\n✅ {module_name} tests PASSED")
            return True
        else:
            print(f"\n❌ {module_name} tests FAILED")
            return False
            
    except Exception as e:
        print(f"\n❌ Error running {module_name} tests: {e}")
        return False


def main():
    """Run all module tests."""
    project_root = Path(__file__).parent
    
    # Define test modules
    test_modules = [
        ('Crypto Price Monitor', project_root / 'crypto_price_monitor' / 'tests'),
        ('Crypto News Monitor', project_root / 'crypto_news_monitor' / 'tests'),
        ('Crypto Orderbook Monitor', project_root / 'crypto_orderbook_monitor' / 'tests'),
        ('Crypto Futures Monitor', project_root / 'crypto_futures_monitor' / 'tests'),
        ('Core Strategies', project_root / 'tests'),
    ]
    
    print("="*70)
    print("CRYPTO AI TRADER - TEST SUITE")
    print("="*70)
    
    results = {}
    for module_name, test_path in test_modules:
        results[module_name] = run_tests(module_name, test_path)
    
    # Print summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    
    passed = sum(1 for v in results.values() if v)
    failed = len(results) - passed
    
    for module_name, passed_test in results.items():
        status = "✅ PASSED" if passed_test else "❌ FAILED"
        print(f"{module_name:.<50} {status}")
    
    print(f"\nTotal: {passed}/{len(results)} modules passed")
    
    # Exit with appropriate code
    sys.exit(0 if failed == 0 else 1)


if __name__ == '__main__':
    main()
