#!/usr/bin/env python3
import unittest
import sys
import os


def run_tests():
    project_root = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, project_root)
    loader = unittest.TestLoader()
    start_dir = os.path.join(project_root, 'tests')
    suite = loader.discover(start_dir, pattern='test_*.py')
    runner = unittest.TextTestRunner(verbosity=2)
    
    print("🧪 Iniciando tests del proyecto...")
    print("=" * 50)
    result = runner.run(suite)
    print("=" * 50)
    print(f"📊 Resumen de tests:")
    print(f"   ✅ Tests ejecutados: {result.testsRun}")
    print(f"   ❌ Fallos: {len(result.failures)}")
    print(f"   ⚠️  Errores: {len(result.errors)}")
    
    if result.failures:
        print("\n❌ Tests que fallaron:")
        for test, traceback in result.failures:
            print(f"   - {test}: {traceback.split('AssertionError:')[-1].strip()}")
    
    if result.errors:
        print("\n⚠️  Tests con errores:")
        for test, traceback in result.errors:
            print(f"   - {test}: {traceback.split('Exception:')[-1].strip()}")
    
    return 0 if result.wasSuccessful() else 1

if __name__ == '__main__':
    exit_code = run_tests()
    sys.exit(exit_code)
