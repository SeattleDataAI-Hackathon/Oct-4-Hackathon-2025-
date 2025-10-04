#!/usr/bin/env python3
"""
Test script to verify the analysis router is properly included
"""

import requests
import json

def test_analysis_router_inclusion():
    """Test that the analysis router is properly included in the main app"""
    
    print("Testing Analysis Router Inclusion")
    print("=" * 50)
    
    base_url = "http://localhost:8000"
    
    # Test the health endpoint from the analysis router
    health_endpoint = f"{base_url}/api/analysis/health"
    
    try:
        response = requests.get(health_endpoint, timeout=5)
        
        if response.status_code == 200:
            result = response.json()
            print("✓ Analysis router health endpoint is accessible")
            print(f"  Status: {result.get('status', 'N/A')}")
            print(f"  Alzheimer's Predictor: {result.get('alzheimers_predictor', 'N/A')}")
            print(f"  LLM Configured: {result.get('llm_configured', 'N/A')}")
            print(f"  LLM Provider: {result.get('llm_provider', 'N/A')}")
            return True
        else:
            print(f"✗ Health endpoint failed: {response.status_code}")
            print(f"  Response: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("✗ Connection Error: Make sure the API server is running")
        return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def test_direct_analysis_endpoint():
    """Test the direct analysis endpoint from the analysis router"""
    
    print("\nTesting Direct Analysis Endpoint from Analysis Router")
    print("=" * 50)
    
    base_url = "http://localhost:8000"
    endpoint = f"{base_url}/api/analysis/direct"
    
    # Sample patient data
    sample_data = {
        "Age": 70,
        "Gender": 1,
        "MMSE": 24,
        "ADL": 80,
        "FamilyHistoryAlzheimers": 0,
        "MemoryComplaints": 0,
        "Forgetfulness": 0
    }
    
    payload = {
        "patient_data": sample_data
    }
    
    try:
        response = requests.post(
            endpoint,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✓ Direct analysis endpoint is accessible from analysis router")
            print(f"  Analysis Method: {result.get('analysis_method', 'N/A')}")
            print(f"  Risk Level: {result.get('diagnosis_analysis', {}).get('risk_level', 'N/A')}")
            print(f"  Treatment Actions: {len(result.get('treatment_plan', {}).get('immediate_actions', []))}")
            return True
        else:
            print(f"✗ Direct analysis endpoint failed: {response.status_code}")
            print(f"  Response: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("✗ Connection Error: Make sure the API server is running")
        return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def test_api_health():
    """Test main API health"""
    
    base_url = "http://localhost:8000"
    
    try:
        response = requests.get(f"{base_url}/", timeout=5)
        if response.status_code == 200:
            health = response.json()
            print("Main API Health Check:")
            print(f"  Service: {health.get('service', 'Unknown')}")
            print(f"  Alzheimer's Predictor: {health.get('alzheimers_predictor', 'Unknown')}")
            print(f"  LLM Configured: {health.get('llm_configured', 'Unknown')}")
            return True
        else:
            print(f"✗ Main API Health Check Failed: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("✗ API not running. Start with: uvicorn app:app --reload")
        return False
    except Exception as e:
        print(f"✗ Health check error: {e}")
        return False

if __name__ == "__main__":
    print("CognifyCare Analysis Router Test")
    print("=" * 50)
    
    # Check main API health
    if not test_api_health():
        print("\nPlease start the API server first:")
        print("  uvicorn app:app --reload")
        exit(1)
    
    print()
    
    # Test analysis router health
    router_health = test_analysis_router_inclusion()
    
    # Test direct analysis endpoint
    direct_analysis = test_direct_analysis_endpoint()
    
    print("\n" + "=" * 50)
    print("SUMMARY")
    print("=" * 50)
    print(f"  Analysis Router Health: {'✓ Working' if router_health else '✗ Failed'}")
    print(f"  Direct Analysis Endpoint: {'✓ Working' if direct_analysis else '✗ Failed'}")
    
    if router_health and direct_analysis:
        print("\n🎉 Analysis router is properly included and working!")
        print("   All analysis endpoints are accessible through the main API")
    else:
        print("\n⚠️  Analysis router may not be properly included")
        print("   Check the router inclusion in app.py")
    
    print("\n" + "=" * 50)
    print("ENDPOINTS AVAILABLE:")
    print("=" * 50)
    print("  GET  /api/analysis/health - Analysis module health check")
    print("  POST /api/analysis/direct - Direct analysis using DiagnosisTreatmentPlanner")
    print("  POST /api/patient/{id}/intake/analyze - Intake analysis (existing)")
    print("  POST /api/admin/configure-llm - LLM configuration (existing)")
