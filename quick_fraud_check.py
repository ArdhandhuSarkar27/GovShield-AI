"""
Quick Fraud Check - Super Simple Version
=======================================
The easiest way to check a single claim for fraud.
Just run this script and enter basic details.

Usage: python quick_fraud_check.py
"""
from simple_fraud_checker import check_claim_fraud, print_result


def quick_check():
    """
    Super simple fraud check with professional demo-ready output
    """
    print("╔" + "═" * 58 + "╗")
    print("║" + "🏥 GOVSHIELD QUICK FRAUD DETECTION SYSTEM 🏥".center(58) + "║")
    print("╚" + "═" * 58 + "╝")
    print("\n📝 Enter basic claim details for instant fraud analysis:\n")
    
    try:
        # Get essential information with better prompts
        print("👤 PATIENT INFORMATION:")
        name = input("   Patient Name: ").strip() or "John Doe"
        
        age_input = input("   Age (18-100): ").strip()
        age = int(age_input) if age_input else 45
        
        print("\n🏥 MEDICAL INFORMATION:")
        procedure = input("   Procedure (e.g., Cardiac Bypass, Appendectomy): ").strip() or "Cardiac Bypass"
        
        amount_input = input("   Claim Amount (₹): ").strip()
        amount = int(amount_input) if amount_input else 300000
        
        print(f"\n{'─' * 60}")
        print("🔍 ANALYZING CLAIM FOR FRAUD PATTERNS...")
        print("🤖 Processing through AI fraud detection model...")
        print("📊 Calculating risk score and recommendations...")
        print(f"{'─' * 60}")
        
        # Check the claim
        result = check_claim_fraud(
            patient_name=name,
            age=age,
            procedure=procedure,
            amount=amount
        )
        
        # Show results with enhanced formatting
        print_result(result)
        
        # Demo summary
        status = result['status']
        risk_score = result['risk_score']
        
        print(f"\n{'═' * 70}")
        print("🎯 DEMO PRESENTATION SUMMARY")
        print(f"{'═' * 70}")
        
        if status == "FLAGGED":
            print("🚨 OUTCOME: This claim would be IMMEDIATELY BLOCKED")
            print(f"📊 Risk Level: {risk_score:.1f}% - CRITICAL FRAUD RISK")
            print("👮 Next Step: Assign to fraud investigation team")
            print("💰 Impact: Prevents potential fraudulent payment")
        elif status == "REVIEW":
            print("⚠️ OUTCOME: This claim would be sent for HUMAN REVIEW")
            print(f"📊 Risk Level: {risk_score:.1f}% - MODERATE FRAUD RISK")
            print("👤 Next Step: Manual verification by claims officer")
            print("⏱️ Timeline: Review within 48 hours")
        else:
            print("✅ OUTCOME: This claim would be APPROVED for processing")
            print(f"📊 Risk Level: {risk_score:.1f}% - LOW FRAUD RISK")
            print("🚀 Next Step: Standard payment processing")
            print("⚡ Timeline: Immediate approval")
        
        print(f"{'═' * 70}")
        
        return result
        
    except ValueError:
        print("\n❌ INPUT ERROR")
        print("Please enter valid numbers for age and claim amount.")
        print("Example: Age = 45, Amount = 300000")
        return None
    except KeyboardInterrupt:
        print(f"\n\n{'═' * 40}")
        print("👋 Thank you for using GovShield!")
        print("🏥 Protecting healthcare resources with AI")
        print(f"{'═' * 40}")
        return None


if __name__ == "__main__":
    import os
    
    # Check if model exists
    if not os.path.exists("models/fraud_detection_model.pkl"):
        print("❌ Model not found! Please run 'python main_simple.py' first.")
    else:
        quick_check()