#!/usr/bin/env python3
"""
Simple model optimization benchmark without unicode issues
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import time
import torch
import psutil
import gc

os.environ['USE_OPTIMIZED_MODELS'] = 'true'

from llm.models.cross_encoder_model import CrossEncoderModel
from llm.models.optimized_cross_encoder_model import OptimizedCrossEncoderModel

def clear_gpu_memory():
    """Clear GPU memory"""
    gc.collect()
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
        torch.cuda.synchronize()

def get_gpu_memory_mb():
    """Get GPU memory usage in MB"""
    if torch.cuda.is_available():
        return torch.cuda.memory_allocated() / 1024**2
    return 0.0

def test_cross_encoder_performance():
    """Test cross-encoder model performance accurately"""
    print("=== Cross-Encoder Performance Test ===")
    
    test_query = "Real estate sales contract termination"
    test_documents = [
        "Real estate sales contract drafting and review",
        "Rental contract dispute resolution methods", 
        "Contract termination damage liability cases",
        "Real estate brokerage fee regulations",
        "Payment and ownership transfer procedures",
        "Property registration and title transfer",
        "Mortgage loan agreement terms",
        "Real estate tax obligations",
        "Construction contract disputes",
        "Commercial lease agreements"
    ]
    
    # Test Original Model
    print("\n--- Original Cross-Encoder Model ---")
    clear_gpu_memory()
    
    # Measure memory before loading
    gpu_before = get_gpu_memory_mb()
    
    # Load original model
    original_model = CrossEncoderModel()
    
    # Measure memory after loading
    gpu_after_load = get_gpu_memory_mb()
    original_memory = gpu_after_load - gpu_before
    
    # Warmup
    _ = original_model.get_cross_encoder_scores(test_query, test_documents[:2])
    
    # Actual performance test
    start_time = time.time()
    original_scores = original_model.get_cross_encoder_scores(test_query, test_documents)
    original_time = time.time() - start_time
    
    print(f"Memory usage: {original_memory:.1f} MB")
    print(f"Processing time: {original_time:.3f} seconds")
    print(f"Throughput: {len(test_documents)/original_time:.1f} docs/sec")
    print(f"Scores sample: {original_scores[:3]}")
    
    # Clean up
    del original_model
    clear_gpu_memory()
    time.sleep(1)
    
    # Test Optimized Model
    print("\n--- Optimized Cross-Encoder Model ---")
    
    # Measure memory before loading
    gpu_before = get_gpu_memory_mb()
    
    # Load optimized model
    optimized_model = OptimizedCrossEncoderModel(enable_quantization=True)
    
    # Measure memory after loading
    gpu_after_load = get_gpu_memory_mb()
    optimized_memory = gpu_after_load - gpu_before
    
    # Warmup
    _ = optimized_model.get_cross_encoder_scores(test_query, test_documents[:2])
    
    # Actual performance test
    start_time = time.time()
    optimized_scores = optimized_model.get_cross_encoder_scores(test_query, test_documents)
    optimized_time = time.time() - start_time
    
    print(f"Memory usage: {optimized_memory:.1f} MB")
    print(f"Processing time: {optimized_time:.3f} seconds")
    print(f"Throughput: {len(test_documents)/optimized_time:.1f} docs/sec")
    print(f"Scores sample: {optimized_scores[:3]}")
    
    # Performance comparison
    print("\n=== Performance Improvement ===")
    
    if original_memory > 0 and optimized_memory > 0:
        memory_reduction = ((original_memory - optimized_memory) / original_memory) * 100
        print(f"Memory reduction: {memory_reduction:.1f}%")
    
    if original_time > 0 and optimized_time > 0:
        speed_improvement = ((original_time - optimized_time) / original_time) * 100
        print(f"Speed improvement: {speed_improvement:.1f}%")
        
        throughput_improvement = ((len(test_documents)/optimized_time - len(test_documents)/original_time) / (len(test_documents)/original_time)) * 100
        print(f"Throughput improvement: {throughput_improvement:.1f}%")
    
    # Accuracy comparison (cosine similarity between score arrays)
    if len(original_scores) == len(optimized_scores):
        import numpy as np
        orig_array = np.array(original_scores)
        opt_array = np.array(optimized_scores)
        
        # Normalize arrays
        orig_norm = orig_array / np.linalg.norm(orig_array)
        opt_norm = opt_array / np.linalg.norm(opt_array)
        
        # Calculate cosine similarity
        cosine_sim = np.dot(orig_norm, opt_norm)
        print(f"Score correlation (cosine similarity): {cosine_sim:.3f}")
        print(f"Accuracy maintained: {'YES' if cosine_sim > 0.95 else 'NO'}")
    
    del optimized_model
    clear_gpu_memory()
    
    return {
        'original_memory_mb': original_memory,
        'original_time_sec': original_time,
        'optimized_memory_mb': optimized_memory,
        'optimized_time_sec': optimized_time,
        'memory_reduction_percent': memory_reduction if 'memory_reduction' in locals() else 0,
        'speed_improvement_percent': speed_improvement if 'speed_improvement' in locals() else 0,
        'cosine_similarity': cosine_sim if 'cosine_sim' in locals() else 0
    }

def main():
    """Main execution"""
    print("Model Optimization Benchmark")
    print("=" * 40)
    
    # System info
    print(f"CPU: {psutil.cpu_count()} cores")
    print(f"Memory: {psutil.virtual_memory().total / 1024**3:.1f} GB")
    if torch.cuda.is_available():
        print(f"GPU: {torch.cuda.get_device_name(0)}")
        print(f"GPU Memory: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.1f} GB")
    
    # Run benchmark
    results = test_cross_encoder_performance()
    
    # Summary
    print("\n" + "=" * 40)
    print("BENCHMARK SUMMARY")
    print("=" * 40)
    print(f"Memory reduction: {results['memory_reduction_percent']:.1f}%")
    print(f"Speed improvement: {results['speed_improvement_percent']:.1f}%") 
    print(f"Accuracy maintained: {'YES' if results['cosine_similarity'] > 0.95 else 'NO'}")
    print("\nBenchmark completed successfully!")
    
    return results

if __name__ == "__main__":
    results = main()