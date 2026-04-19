"""
Testing Script - Verify all components work correctly
"""

import numpy as np
from pipeline import AttackDetectionPipeline
from device_simulator import DeviceSimulator


def test_pipeline():
    """Test the prediction pipeline"""
    print("\n" + "="*70)
    print("Testing Prediction Pipeline")
    print("="*70)
    
    pipeline = AttackDetectionPipeline()
    
    if pipeline.model is None:
        print("✗ Pipeline test FAILED - Model not loaded")
        return False
    
    print("✓ Model loaded successfully")
    
    # Get model info
    info = pipeline.get_model_info()
    if info:
        print(f"  • Model Type: {info.get('model_type')}")
        print(f"  • Classes: {info.get('num_classes')}")
        print(f"  • Train Accuracy: {info.get('train_accuracy'):.4f}")
        print(f"  • Test Accuracy: {info.get('test_accuracy'):.4f}")
    
    # Test single prediction
    n_features = info['n_features'] if info else 100
    test_sample = np.random.randn(n_features).astype('float32')
    
    result = pipeline.predict_single(test_sample)
    
    print(f"\n✓ Single prediction test passed:")
    print(f"  • Prediction: {result['prediction']}")
    print(f"  • Confidence: {result['confidence']*100:.2f}%")
    
    # Test batch prediction
    test_batch = np.random.randn(10, n_features).astype('float32')
    results = pipeline.predict(test_batch)
    
    print(f"\n✓ Batch prediction test passed:")
    print(f"  • Predictions shape: {results['pred_labels'].shape}")
    print(f"  • Mean confidence: {np.mean(results['probabilities'].max(axis=1))*100:.2f}%")
    
    return True


def test_simulator():
    """Test the device simulator"""
    print("\n" + "="*70)
    print("Testing Device Simulator")
    print("="*70)
    
    simulator = DeviceSimulator(n_features=100)
    
    print("✓ Simulator initialized")
    
    # Test traffic generation
    attack_types = ['Normal', 'DDoS_HTTP_Flood_attack', 'Port_Scanning_attack']
    
    for attack in attack_types:
        features, src_ip = simulator.generate_traffic(attack, n_samples=3)
        if features is not None:
            print(f"✓ Generated {attack}:")
            print(f"  • Shape: {features.shape}")
            print(f"  • Source IP: {src_ip}")
        else:
            print(f"✗ Failed to generate {attack}")
            return False
    
    # Test IP blocking
    print("\n✓ Testing IP blocking:")
    test_ip = "192.168.1.100"
    
    simulator.block_ip(test_ip)
    if test_ip in simulator.get_blocked_ips():
        print(f"  • Successfully blocked {test_ip}")
    else:
        print(f"✗ Failed to block {test_ip}")
        return False
    
    # Try to generate traffic from blocked IP
    features, src_ip = simulator.generate_traffic("Normal", src_ip=test_ip)
    if features is None:
        print(f"  • Correctly rejected traffic from blocked IP")
    else:
        print(f"✗ Should have rejected blocked IP")
        return False
    
    # Unblock and retry
    simulator.unblock_ip(test_ip)
    features, src_ip = simulator.generate_traffic("Normal", src_ip=test_ip)
    if features is not None:
        print(f"  • Successfully allowed traffic after unblocking")
    else:
        print(f"✗ Failed to allow traffic after unblocking")
        return False
    
    return True


def test_integration():
    """Test pipeline + simulator integration"""
    print("\n" + "="*70)
    print("Integration Test - Pipeline + Simulator")
    print("="*70)
    
    pipeline = AttackDetectionPipeline()
    simulator = DeviceSimulator(n_features=pipeline.model_info['n_features'])
    
    print("✓ Both components loaded")
    
    # Simulate attack and detect
    attack_types = ['Normal', 'DDoS_HTTP_Flood_attack', 'SQL_injection_attack']
    
    results = []
    for attack in attack_types:
        features, src_ip = simulator.generate_traffic(attack, n_samples=1)
        
        if features is not None:
            is_attack, pred = pipeline.is_attack(features[0])
            
            status = "ATTACK" if is_attack else "NORMAL"
            results.append({
                'expected': attack,
                'predicted': pred['prediction'],
                'confidence': pred['confidence'],
                'correct': (attack != 'Normal') == is_attack
            })
            
            print(f"\n{attack}:")
            print(f"  • Expected: {'Attack' if attack != 'Normal' else 'Normal'}")
            print(f"  • Predicted: {pred['prediction']}")
            print(f"  • Confidence: {pred['confidence']*100:.2f}%")
            print(f"  • Status: {'✓ Correct' if (attack != 'Normal') == is_attack else '✗ Incorrect'}")
    
    # Summary
    correct_predictions = sum(1 for r in results if r['correct'])
    accuracy = correct_predictions / len(results) * 100
    
    print(f"\n✓ Integration test accuracy: {accuracy:.1f}% ({correct_predictions}/{len(results)})")
    
    return accuracy >= 0


def main():
    """Run all tests"""
    print("\n" + "="*70)
    print("🧪 ATTACK DETECTION SYSTEM - TEST SUITE")
    print("="*70)
    
    tests = [
        ("Pipeline", test_pipeline),
        ("Simulator", test_simulator),
        ("Integration", test_integration)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"\n✗ {test_name} test FAILED with error:")
            print(f"  {str(e)}")
            results[test_name] = False
    
    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    
    for test_name, passed in results.items():
        status = "✓ PASSED" if passed else "✗ FAILED"
        print(f"{test_name:20s}: {status}")
    
    total_passed = sum(1 for v in results.values() if v)
    total_tests = len(results)
    
    print(f"\nTotal: {total_passed}/{total_tests} tests passed")
    
    if total_passed == total_tests:
        print("\n✅ ALL TESTS PASSED - System ready for use!")
        return 0
    else:
        print("\n⚠️  Some tests failed - check configuration")
        return 1


if __name__ == "__main__":
    exit(main())
