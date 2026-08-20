"""
Main application entry point for Ayushman Bharat Fraud Detection System
"""
import sys
from pathlib import Path
import argparse

# Add project root to path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

from config import DataConfig, ModelConfig, SystemConfig
from data.data_generator import SyntheticDataGenerator
from models.feature_engineering import FeatureEngineer
from models.fraud_model import FraudDetectionModel
from utils.logger import setup_logging
from utils.validators import DataValidator
from utils.exceptions import FraudDetectionError


class FraudDetectionPipeline:
    """Main pipeline for fraud detection system"""
    
    def __init__(self, data_config: DataConfig = None, model_config: ModelConfig = None):
        self.data_config = data_config or DataConfig()
        self.model_config = model_config or ModelConfig()
        self.logger = setup_logging()
        
        # Initialize components
        self.data_generator = SyntheticDataGenerator(self.data_config)
        self.feature_engineer = FeatureEngineer()
        self.model = FraudDetectionModel(self.model_config)
        self.validator = DataValidator()
        
    def run_full_pipeline(self, n_rows: int = None, save_results: bool = True) -> dict:
        """
        Run the complete fraud detection pipeline
        
        Args:
            n_rows: Number of rows to generate
            save_results: Whether to save results to CSV
            
        Returns:
            Dictionary with pipeline results
        """
        try:
            self.logger.info("🏥 Starting Ayushman Bharat Fraud Detection Pipeline")
            
            # Step 1: Generate synthetic data
            self.logger.info("📊 Generating synthetic dataset...")
            df = self.data_generator.generate_dataset(n_rows)
            
            # Step 2: Inject fraud patterns
            self.logger.info("🚨 Injecting fraud patterns...")
            df = self.data_generator.inject_fraud_patterns(df)
            
            # Step 3: Validate data
            self.logger.info("✅ Validating dataset...")
            self.validator.validate_dataframe(df)
            
            # Step 4: Feature engineering
            self.logger.info("🔧 Creating engineered features...")
            features_df = self.feature_engineer.create_features(df, is_training=True)
            
            # Step 5: Prepare training data
            X = self.feature_engineer.get_feature_matrix(features_df)
            y = features_df['fraud_label']
            
            # Step 6: Train model
            self.logger.info("🤖 Training fraud detection model...")
            training_metrics = self.model.train(X, y, perform_cv=True)
            
            # Step 7: Generate predictions
            self.logger.info("📈 Generating fraud risk scores...")
            risk_scores = self.model.calculate_risk_scores(X)
            
            # Step 8: Prepare results
            result_df = df.copy()
            result_df['fraud_risk_score'] = risk_scores
            
            # Step 9: Save results
            if save_results:
                output_file = self.data_config.output_file
                result_df.to_csv(output_file, index=False)
                self.logger.info(f"💾 Results saved to {output_file}")
                
                # Save model and encoders
                self.model.save_model(self.data_config.model_file)
                self.feature_engineer.save_encoders(self.data_config.encoders_file)
            
            # Step 10: Generate summary
            summary = self._generate_summary(result_df, training_metrics)
            self._print_summary(summary)
            
            return {
                'data': result_df,
                'model': self.model,
                'feature_engineer': self.feature_engineer,
                'summary': summary,
                'training_metrics': training_metrics
            }
            
        except Exception as e:
            self.logger.error(f"Pipeline failed: {str(e)}")
            raise FraudDetectionError(f"Pipeline execution failed: {str(e)}")
    
    def _generate_summary(self, df, training_metrics) -> dict:
        """Generate pipeline summary statistics"""
        total_claims = len(df)
        fraud_claims = len(df[df['fraud_label'] == 1])
        legitimate_claims = total_claims - fraud_claims
        
        # Risk score analysis
        high_risk = len(df[df['fraud_risk_score'] > self.data_config.high_risk_threshold])
        medium_risk = len(df[
            (df['fraud_risk_score'] >= self.data_config.medium_risk_threshold) & 
            (df['fraud_risk_score'] <= self.data_config.high_risk_threshold)
        ])
        low_risk = total_claims - high_risk - medium_risk
        
        # Calculate potential savings (assuming high-risk claims are investigated)
        high_risk_claims = df[df['fraud_risk_score'] > self.data_config.high_risk_threshold]
        potential_savings = high_risk_claims['claim_amount'].sum()
        
        return {
            'total_claims': total_claims,
            'fraud_claims': fraud_claims,
            'legitimate_claims': legitimate_claims,
            'fraud_percentage': (fraud_claims / total_claims) * 100,
            'high_risk_claims': high_risk,
            'medium_risk_claims': medium_risk,
            'low_risk_claims': low_risk,
            'potential_savings': potential_savings,
            'avg_risk_score': df['fraud_risk_score'].mean(),
            'model_accuracy': training_metrics.get('test_accuracy', 0) * 100,
            'model_auc': training_metrics.get('test_auc', 0)
        }
    
    def _print_summary(self, summary: dict):
        """Print formatted summary to console"""
        self.logger.info("\n" + "="*60)
        self.logger.info("📋 FRAUD DETECTION PIPELINE SUMMARY")
        self.logger.info("="*60)
        
        self.logger.info(f"📊 Dataset Statistics:")
        self.logger.info(f"   • Total Claims: {summary['total_claims']:,}")
        self.logger.info(f"   • Fraudulent Claims: {summary['fraud_claims']:,} ({summary['fraud_percentage']:.1f}%)")
        self.logger.info(f"   • Legitimate Claims: {summary['legitimate_claims']:,}")
        
        self.logger.info(f"\n🎯 Risk Score Distribution:")
        self.logger.info(f"   • High Risk (>70): {summary['high_risk_claims']:,}")
        self.logger.info(f"   • Medium Risk (30-70): {summary['medium_risk_claims']:,}")
        self.logger.info(f"   • Low Risk (<30): {summary['low_risk_claims']:,}")
        self.logger.info(f"   • Average Risk Score: {summary['avg_risk_score']:.2f}")
        
        self.logger.info(f"\n🤖 Model Performance:")
        self.logger.info(f"   • Accuracy: {summary['model_accuracy']:.2f}%")
        self.logger.info(f"   • AUC Score: {summary['model_auc']:.4f}")
        
        self.logger.info(f"\n💰 Financial Impact:")
        self.logger.info(f"   • Potential Savings: ₹{summary['potential_savings']:,.0f}")
        
        self.logger.info("="*60)


def main():
    """Main application entry point"""
    parser = argparse.ArgumentParser(description='Ayushman Bharat Fraud Detection System')
    parser.add_argument('--rows', type=int, default=500, help='Number of rows to generate')
    parser.add_argument('--no-save', action='store_true', help='Skip saving results to file')
    parser.add_argument('--tune-hyperparameters', action='store_true', help='Perform hyperparameter tuning')
    parser.add_argument('--log-level', default='INFO', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'])
    
    args = parser.parse_args()
    
    try:
        # Initialize configurations
        system_config = SystemConfig.from_env()
        data_config = DataConfig()
        model_config = ModelConfig()
        
        # Setup logging
        setup_logging(level=args.log_level)
        
        # Initialize and run pipeline
        pipeline = FraudDetectionPipeline(data_config, model_config)
        results = pipeline.run_full_pipeline(
            n_rows=args.rows,
            save_results=not args.no_save
        )
        
        print(f"\n✅ Pipeline completed successfully!")
        print(f"📁 Results saved to: {data_config.output_file}")
        print(f"🌐 Open dashboard/index.html to view the interactive dashboard")
        
        return 0
        
    except Exception as e:
        print(f"❌ Pipeline failed: {str(e)}")
        return 1


if __name__ == "__main__":
    sys.exit(main())