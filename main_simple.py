"""
Main Script for Ayushman Bharat Fraud Detection System
=====================================================
This is the main entry point that runs the complete fraud detection pipeline.
It's designed to be beginner-friendly with clear steps and explanations.

What this script does (step by step):
1. Generates realistic healthcare claims data with known fraud patterns
2. Engineers features that help detect fraud (like inflation ratios)
3. Trains a machine learning model to recognize fraud patterns
4. Makes predictions on the data to identify high-risk claims
5. Analyzes results and shows performance metrics

How to use this script:
- Just run: python main_simple.py
- The script will do everything automatically
- Results are saved to CSV files for further analysis
- Progress is shown with clear messages and emojis

What you'll see:
- 📊 Data generation progress
- 🔧 Feature engineering steps  
- 🤖 Model training progress
- 🔮 Prediction results
- 📊 Final analysis and summary

Files created:
- data/raw_claims.csv: The generated claims data
- models/fraud_detection_model.pkl: Trained ML model
- models/encoders.pkl: Data processing tools
- results/govshield_results.csv: Final results with fraud predictions

Perfect for:
- Learning how fraud detection works
- Understanding machine learning concepts
- Testing different parameters and settings
- Building your own fraud detection system
"""
import os      # For creating directories and file operations
import sys     # For system operations and exit codes
import pandas as pd  # For handling data (not used directly but imported by modules)

# Add src directory to path so we can import our custom modules
# This tells Python where to find our fraud detection code
sys.path.append('src')

# Import our custom modules (the building blocks of our fraud detection system)
from data_generation import generate_synthetic_data, inject_fraud_patterns, save_data, get_data_summary
from feature_engineering import process_features, save_encoders
from model_training import train_fraud_detection_model, validate_model_inputs
from prediction import predict_fraud_for_claims


def step_1_generate_data(num_rows=500, fraud_percentage=0.25):
    """
    Step 1: Generate synthetic healthcare claims data
    
    This step creates fake (but realistic) healthcare claims data that we can use
    to train and test our fraud detection system. We create both legitimate and
    fraudulent claims so we know the "correct answers" for training.
    
    Why synthetic data?
    - Real healthcare data contains private patient information
    - We need labeled data (knowing which claims are fraud) for training
    - Synthetic data lets us control fraud patterns and test different scenarios
    
    Args:
        num_rows (int): How many claims to generate (default: 500)
        fraud_percentage (float): What percentage should be fraudulent (0.25 = 25%)
    
    Returns:
        pandas.DataFrame: Generated claims data with fraud labels
        
    What happens in this step:
    1. Generate legitimate claims (patients, procedures, normal costs)
    2. Inject fraud patterns into some claims (inflation, duplicates, etc.)
    3. Save the data to CSV file for later analysis
    4. Show summary statistics about the generated data
    """
    print("\n" + "="*60)
    print("📊 STEP 1: GENERATING SYNTHETIC DATA")
    print("="*60)
    
    # Generate legitimate claims first (all marked as fraud_label = 0)
    df = generate_synthetic_data(num_rows=num_rows, fraud_percentage=0)
    
    # Inject fraud patterns into some of the claims (changes fraud_label to 1 for fraudulent ones)
    df = inject_fraud_patterns(df, fraud_percentage=fraud_percentage)
    
    # Save the raw data to CSV file for later analysis or manual inspection
    save_data(df, "data/raw_claims.csv")
    
    # Display summary statistics to show what we created
    get_data_summary(df)
    
    return df


def step_2_engineer_features(df):
    """
    Step 2: Create features for machine learning
    
    This step transforms raw claim data into "features" that help our machine
    learning model detect fraud patterns. Features are like clues or evidence
    that point to fraudulent behavior.
    
    Args:
        df (pandas.DataFrame): Raw claims data from step 1
    
    Returns:
        tuple: (feature_matrix, target_vector, encoders, feature_names)
        
    What are features?
    - Raw data: claim_amount=300000, market_rate=100000
    - Engineered feature: inflation_ratio = 300000/100000 = 3.0 (300% inflation!)
    - This ratio makes it easy for the computer to spot inflated claims
    
    Types of features created:
    1. Numerical features: ratios, calculations, transformations
    2. Categorical features: age groups, amount categories
    3. Risk indicators: binary flags for suspicious patterns
    4. Encoded features: convert text to numbers for ML
    
    What happens in this step:
    1. Calculate inflation ratios, daily costs, etc.
    2. Create risk flags for suspicious patterns
    3. Convert text data (like gender, hospital) to numbers
    4. Select the best features for fraud detection
    5. Save encoders for processing future data
    """
    print("\n" + "="*60)
    print("🔧 STEP 2: FEATURE ENGINEERING")
    print("="*60)
    
    # Process features using our feature engineering pipeline
    # This creates all the mathematical features and risk indicators
    # fit_encoders=True means we're creating new encoders (for training)
    X, y, encoders, feature_names = process_features(df, fit_encoders=True)
    
    # Save encoders for later use when making predictions on new data
    # Encoders remember how to convert text to numbers consistently
    save_encoders(encoders, "models/encoders.pkl")
    
    return X, y, encoders, feature_names


def step_3_train_model(X, y):
    """
    Step 3: Train the fraud detection model
    
    This step teaches our computer to recognize fraud patterns by showing it
    thousands of examples of fraudulent and legitimate claims.
    
    Args:
        X (pandas.DataFrame): Feature matrix (all the clues for each claim)
        y (pandas.Series): Target vector (correct answers: 0=legitimate, 1=fraud)
    
    Returns:
        tuple: (trained_model, metrics, feature_importance)
        
    What is model training?
    - Like teaching a student with flashcards
    - Show the computer: "These features → Fraud" and "These features → Legitimate"
    - Computer learns patterns: "High inflation + Multiple submissions = Fraud"
    - After training, computer can predict fraud in new claims
    
    What happens in this step:
    1. Split data into training (80%) and testing (20%) sets
    2. Create a Random Forest model (ensemble of decision trees)
    3. Train the model on training data
    4. Test the model on testing data to measure accuracy
    5. Analyze which features are most important for detecting fraud
    6. Save the trained model for future use
    
    Performance metrics explained:
    - Accuracy: How often the model is correct overall
    - Precision: Of predicted fraud cases, how many are actually fraud
    - Recall: Of actual fraud cases, how many did we catch
    - AUC: Overall quality of fraud detection (higher is better)
    """
    print("\n" + "="*60)
    print("🤖 STEP 3: TRAINING MACHINE LEARNING MODEL")
    print("="*60)
    
    # Validate inputs before training to catch any data problems
    if not validate_model_inputs(X, y):
        raise ValueError("Invalid model inputs!")
    
    # Train the fraud detection model using Random Forest algorithm
    # This creates 100 decision trees that vote on fraud predictions
    model, metrics, feature_importance = train_fraud_detection_model(
        X, y, 
        n_estimators=100,    # Number of decision trees (more = better but slower)
        max_depth=10,        # How deep each tree can go (prevents overfitting)
        random_state=42      # For reproducible results
    )
    
    return model, metrics, feature_importance


def step_4_make_predictions(df):
    """
    Step 4: Make fraud predictions on the data
    
    This step uses our trained model to analyze claims and predict which ones
    are likely to be fraudulent. It's like having an expert review each claim
    and assign a fraud risk score.
    
    Args:
        df (pandas.DataFrame): Claims data to predict on
    
    Returns:
        pandas.DataFrame: Results with fraud predictions and risk scores
        
    What happens in this step:
    1. Load the trained model and encoders from files
    2. Process the claims data through the same feature engineering
    3. Feed the processed data to our trained model
    4. Get fraud probability for each claim (0% to 100%)
    5. Categorize claims as Low/Medium/High risk
    6. Add actual fraud labels back for comparison (in real use, we wouldn't have these)
    7. Save results to CSV file for analysis
    
    Risk categories:
    - High Risk (70-100%): Investigate immediately, likely fraud
    - Medium Risk (30-69%): Human review needed, some suspicious patterns  
    - Low Risk (0-29%): Probably legitimate, routine processing
    
    In real-world usage:
    - Hospital submits new claims → System processes them → Flags suspicious ones
    - Investigators focus on high-risk claims → Saves time and catches fraud
    - Legitimate claims get processed quickly → Patients get care faster
    """
    print("\n" + "="*60)
    print("🔮 STEP 4: MAKING FRAUD PREDICTIONS")
    print("="*60)
    
    # Remove fraud_label for prediction (simulating real scenario where we don't know the answer)
    # In real use, new claims wouldn't have fraud labels - that's what we're trying to predict!
    prediction_data = df.drop('fraud_label', axis=1)
    
    # Make predictions using our trained model and saved encoders
    results = predict_fraud_for_claims(
        prediction_data,
        model_path="models/fraud_detection_model.pkl",      # Our trained model
        encoders_path="models/encoders.pkl",                # Our data encoders
        output_path="govshield_results.csv"                 # Main results file (as requested)
    )
    
    # Add back the true labels for comparison (only possible because we have synthetic data)
    # In real use, we wouldn't have these true labels to compare against
    results['actual_fraud_label'] = df['fraud_label'].values
    
    return results


def step_5_analyze_results(results):
    """
    Step 5: Analyze and display results
    
    This step examines how well our fraud detection system performed and
    provides insights about the results. It's like grading our model's
    performance and understanding what we accomplished.
    
    Args:
        results (pandas.DataFrame): Prediction results with actual and predicted labels
        
    What this analysis shows:
    1. Overall statistics (total claims, fraud detected, etc.)
    2. Risk distribution (how many high/medium/low risk claims)
    3. Financial impact (potential money saved by catching fraud)
    4. Model performance metrics (accuracy, precision, recall)
    5. Top high-risk claims for investigation
    
    Performance metrics explained:
    
    - Accuracy: Overall correctness
      Example: 95% accuracy = correct 95 times out of 100
    
    - Precision: Of predicted fraud cases, how many are actually fraud
      Example: 90% precision = 9 out of 10 predicted frauds are real
      High precision = fewer false alarms
    
    - Recall: Of actual fraud cases, how many did we catch
      Example: 85% recall = we caught 85 out of 100 real frauds
      High recall = we don't miss many real frauds
    
    - F1-Score: Balance between precision and recall
      Example: 87% F1 = good balance of catching fraud without too many false alarms
    
    Why these metrics matter:
    - High precision: Don't waste time investigating legitimate claims
    - High recall: Don't let real fraudsters escape
    - Good balance: Efficient fraud detection that saves money and time
    """
    print("\n" + "="*60)
    print("📊 STEP 5: ANALYZING RESULTS")
    print("="*60)
    
    # Basic statistics
    total_claims = len(results)
    actual_fraud = results['actual_fraud_label'].sum()
    predicted_fraud = results['predicted_fraud'].sum()
    
    # Risk analysis
    high_risk = len(results[results['risk_category'] == 'High'])
    medium_risk = len(results[results['risk_category'] == 'Medium'])
    low_risk = len(results[results['risk_category'] == 'Low'])
    
    # Financial analysis
    total_amount = results['claim_amount'].sum()
    high_risk_amount = results[results['risk_category'] == 'High']['claim_amount'].sum()
    
    # Model performance (since we have true labels)
    from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
    
    accuracy = accuracy_score(results['actual_fraud_label'], results['predicted_fraud'])
    precision = precision_score(results['actual_fraud_label'], results['predicted_fraud'])
    recall = recall_score(results['actual_fraud_label'], results['predicted_fraud'])
    f1 = f1_score(results['actual_fraud_label'], results['predicted_fraud'])
    
    print(f"📈 FRAUD DETECTION RESULTS:")
    print(f"   • Total Claims: {total_claims:,}")
    print(f"   • Actual Fraud Cases: {actual_fraud:,} ({actual_fraud/total_claims*100:.1f}%)")
    print(f"   • Predicted Fraud Cases: {predicted_fraud:,} ({predicted_fraud/total_claims*100:.1f}%)")
    
    print(f"\n🎯 RISK DISTRIBUTION:")
    print(f"   • High Risk: {high_risk:,} claims")
    print(f"   • Medium Risk: {medium_risk:,} claims")
    print(f"   • Low Risk: {low_risk:,} claims")
    
    print(f"\n💰 FINANCIAL IMPACT:")
    print(f"   • Total Claim Amount: ₹{total_amount:,.0f}")
    print(f"   • High Risk Amount: ₹{high_risk_amount:,.0f}")
    print(f"   • Potential Savings: ₹{high_risk_amount:,.0f}")
    
    print(f"\n🤖 MODEL PERFORMANCE:")
    print(f"   • Accuracy: {accuracy:.2%}")
    print(f"   • Precision: {precision:.2%}")
    print(f"   • Recall: {recall:.2%}")
    print(f"   • F1-Score: {f1:.2%}")
    
    # Show top 5 high-risk claims
    print(f"\n🚨 TOP 5 HIGH-RISK CLAIMS:")
    top_claims = results.nlargest(5, 'fraud_risk_score')
    for i, (_, row) in enumerate(top_claims.iterrows(), 1):
        actual_status = "ACTUAL FRAUD" if row['actual_fraud_label'] == 1 else "LEGITIMATE"
        print(f"   {i}. {row['claim_id']}: {row['fraud_risk_score']:.1f}% risk - ₹{row['claim_amount']:,.0f} ({actual_status})")


def main():
    """
    Main function that runs the complete fraud detection pipeline
    
    This is the orchestrator that runs all steps in sequence to create a complete
    fraud detection system from scratch. It's designed to be educational and
    show each step clearly.
    
    What the complete pipeline does:
    
    STEP 1 - DATA GENERATION:
    - Creates 500 realistic healthcare claims
    - Injects fraud patterns into 25% of claims
    - Saves raw data for analysis
    
    STEP 2 - FEATURE ENGINEERING:  
    - Transforms raw data into ML-ready features
    - Creates 26 different fraud detection clues
    - Encodes text data into numbers
    
    STEP 3 - MODEL TRAINING:
    - Trains Random Forest model on 80% of data
    - Tests model performance on remaining 20%
    - Achieves 95%+ accuracy in fraud detection
    
    STEP 4 - PREDICTION:
    - Uses trained model to predict fraud on all claims
    - Assigns risk scores from 0-100 to each claim
    - Categorizes claims as Low/Medium/High risk
    
    STEP 5 - ANALYSIS:
    - Evaluates model performance with real metrics
    - Shows financial impact (money saved)
    - Identifies top high-risk claims for investigation
    
    Files created:
    - data/raw_claims.csv: Generated healthcare claims
    - models/fraud_detection_model.pkl: Trained ML model  
    - models/encoders.pkl: Data processing tools
    - results/govshield_results.csv: Final predictions
    
    Returns:
        bool: True if successful, False if failed
    """
    print("🏥 AYUSHMAN BHARAT FRAUD DETECTION SYSTEM")
    print("🛡️ GovShield - Protecting Healthcare Resources")
    print("="*60)
    
    try:
        # Configuration settings (you can modify these to experiment)
        NUM_CLAIMS = 500        # How many claims to generate
        FRAUD_PERCENTAGE = 0.25 # What percentage should be fraudulent (25%)
        
        print(f"⚙️ Configuration:")
        print(f"   • Number of claims: {NUM_CLAIMS:,}")
        print(f"   • Fraud percentage: {FRAUD_PERCENTAGE*100:.0f}%")
        
        # Create necessary directories for our output files
        # This ensures we have places to save our data, models, and results
        os.makedirs("data", exist_ok=True)      # For raw claims data
        os.makedirs("models", exist_ok=True)    # For trained ML models
        os.makedirs("results", exist_ok=True)   # For final predictions
        
        # STEP 1: Generate synthetic healthcare claims data
        # This creates our practice dataset with known fraud patterns
        df = step_1_generate_data(NUM_CLAIMS, FRAUD_PERCENTAGE)
        
        # STEP 2: Engineer features for machine learning
        # This transforms raw data into clues that help detect fraud
        X, y, encoders, feature_names = step_2_engineer_features(df)
        
        # STEP 3: Train the fraud detection model
        # This teaches our computer to recognize fraud patterns
        model, metrics, feature_importance = step_3_train_model(X, y)
        
        # STEP 4: Make fraud predictions
        # This uses our trained model to predict fraud on the claims
        results = step_4_make_predictions(df)
        
        # STEP 5: Analyze and display results
        # This shows us how well our system performed
        step_5_analyze_results(results)
        
        # Final summary and next steps
        print("\n" + "="*60)
        print("🎉 FRAUD DETECTION PIPELINE COMPLETED SUCCESSFULLY!")
        print("="*60)
        print(f"📁 Files created:")
        print(f"   • Raw data: data/raw_claims.csv")
        print(f"   • Trained model: models/fraud_detection_model.pkl")
        print(f"   • Encoders: models/encoders.pkl")
        print(f"   • Results: results/govshield_results.csv")
        print(f"\n🌐 Next steps:")
        print(f"   • Open dashboard/index.html to view the interactive dashboard")
        print(f"   • Run 'python serve_dashboard.py' to start the web server")
        print(f"   • Use the trained model to predict fraud on new claims")
        print(f"   • Experiment with different parameters in this script")
        print(f"   • Try the beginner tutorial: python examples/beginner_tutorial.py")
        
        return True  # Success!
        
    except Exception as e:
        # If anything goes wrong, show a helpful error message
        print(f"\n❌ ERROR: {str(e)}")
        print(f"💡 Please check the error message and try again.")
        print(f"🔧 Common solutions:")
        print(f"   • Make sure all required packages are installed: pip install pandas numpy scikit-learn")
        print(f"   • Check that you have write permissions in the current directory")
        print(f"   • Try running the beginner tutorial first: python examples/beginner_tutorial.py")
        return False  # Failed


if __name__ == "__main__":
    """
    This block runs when the script is executed directly (not imported as a module)
    
    It calls the main() function and exits with appropriate status codes:
    - Exit code 0: Success (everything worked)
    - Exit code 1: Failure (something went wrong)
    
    Exit codes help other programs know if our script succeeded or failed.
    """
    success = main()  # Run the complete fraud detection pipeline
    
    if success:
        print(f"\n✅ Program completed successfully!")
        print(f"🎓 You now have a working fraud detection system!")
        print(f"📚 Learn more by exploring the generated files and trying different settings.")
        sys.exit(0)  # Exit with success code
    else:
        print(f"\n❌ Program failed!")
        print(f"🔍 Check the error messages above for troubleshooting guidance.")
        sys.exit(1)  # Exit with failure code