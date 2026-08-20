"""
Production-ready Ayushman Bharat Fraud Detection System
"""
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, Any, Optional
import sys
import traceback

# Add project root to path
sys.path.append(str(Path(__file__).parent))

from config import DataConfig, ModelConfig, SystemConfig
from data.data_generator import SyntheticDataGenerator
from models.feature_engineering import FeatureEngineer
from models.fraud_model import FraudDetectionModel
from utils.logger import setup_logging, Logger
from utils.validators import DataValidator
from utils.exceptions import FraudDetectionError


class AyushmanBharatFraudDetectionSystem:
    """
    Production-ready fraud detection system for Ayushman Bharat claims
    
    This system provides:
    - Synthetic data generation with configurable fraud patterns
    - Advanced feature engineering
    - Machine learning-based fraud detection
    - Risk scoring and reporting
    - Model persistence and loading
    """
    
    def __init__(self, data_config: Optional[DataConfig] = None,
                 model_config: Optional[ModelConfig] = None,
                 system_config: Optional[SystemConfig] = None):
        """
        Initialize the fraud detection system
        
        Args:
            data_config: Data generation configuration
            model_config: Model training configuration  
            system_config: System-wide configuration
        """
        # Load configurations
        self.data_config = data_config or DataConfig()
        self.model_config = model_config or ModelConfig()
        self.system_config = system_config or SystemConfig.from_env()
        
        # Setup logging
        self.logger = setup_logging(
            level=self.system_config.log_level,
            log_file="logs/fraud_detection.log"
        )
        
        # Initialize components
        self.data_generator = SyntheticDataGenerator(self.data_config)
        self.feature_engineer = FeatureEngineer()
        self.model = FraudDetectionModel(self.model_config)
        self.validator = DataValidator()
        
        # State tracking
        self.dataset: Optional[pd.DataFrame] = None
        self.results: Optional[pd.DataFrame] = None
        
        self.logger.info("Fraud Detection System initialized")
    
    def generate_synthetic_data(self, n_rows: int = None, 
                              inject_fraud: bool = True,
                              fraud_percentage: float = None) -> pd.DataFrame:
        """
        Generate synthetic healthcare claims dataset
        
        Args:
            n_rows: Number of rows to generate
            inject_fraud: Whether to inject fraud patterns
            fraud_percentage: Percentage of fraudulent claims
            
        Returns:
            Generated dataset
        """
        try:
            self.logger.info("Starting synthetic data generation")
            
            # Generate base dataset
            n_rows = n_rows or self.data_config.default_rows
            dataset = self.data_generator.generate_dataset(n_rows)
            
            # Inject fraud patterns if requested
            if inject_fraud:
                fraud_pct = fraud_percentage or self.data_config.fraud_percentage
                dataset = self.data_generator.inject_fraud_patterns(dataset, fraud_pct)
            
            # Validate generated data
            self.validator.validate_dataframe(dataset)
            
            self.dataset = dataset
            self.logger.info(f"Generated dataset with {len(dataset)} records")
            
            # Log dataset statistics
            self._log_dataset_statistics(dataset)
            
            return dataset
            
        except Exception as e:
            self.logger.error(f"Data generation failed: {str(e)}")
            raise FraudDetectionError(f"Failed to generate synthetic data: {str(e)}")
    
    def train_fraud_detection_model(self, dataset: Optional[pd.DataFrame] = None,
                                  tune_hyperparameters: bool = False,
                                  perform_cv: bool = True) -> Dict[str, Any]:
        """
        Train the fraud detection model
        
        Args:
            dataset: Dataset to train on (uses generated dataset if None)
            tune_hyperparameters: Whether to perform hyperparameter tuning
            perform_cv: Whether to perform cross-validation
            
        Returns:
            Training metrics
        """
        try:
            self.logger.info("Starting model training")
            
            # Use provided dataset or generated one
            if dataset is None:
                if self.dataset is None:
                    raise FraudDetectionError("No dataset available. Generate data first.")
                dataset = self.dataset
            
            # Validate dataset
            self.validator.validate_dataframe(dataset)
            
            # Feature engineering
            self.logger.info("Performing feature engineering")
            features_df = self.feature_engineer.create_features(dataset, is_training=True)
            
            # Prepare training data
            X = self.feature_engineer.get_feature_matrix(features_df)
            y = features_df['fraud_label']
            
            self.logger.info(f"Training with {len(X)} samples and {len(X.columns)} features")
            
            # Train model
            metrics = self.model.train(
                X, y,
                perform_cv=perform_cv,
                tune_hyperparameters=tune_hyperparameters
            )
            
            self.logger.info("Model training completed successfully")
            return metrics
            
        except Exception as e:
            self.logger.error(f"Model training failed: {str(e)}")
            raise FraudDetectionError(f"Failed to train model: {str(e)}")
    
    def generate_fraud_risk_scores(self, dataset: Optional[pd.DataFrame] = None) -> pd.DataFrame:
        """
        Generate fraud risk scores for claims
        
        Args:
            dataset: Dataset to score (uses generated dataset if None)
            
        Returns:
            Dataset with fraud risk scores
        """
        try:
            self.logger.info("Generating fraud risk scores")
            
            # Use provided dataset or generated one
            if dataset is None:
                if self.dataset is None:
                    raise FraudDetectionError("No dataset available. Generate data first.")
                dataset = self.dataset
            
            # Check if model is trained
            if not self.model.is_trained:
                raise FraudDetectionError("Model is not trained. Train model first.")
            
            # Feature engineering
            features_df = self.feature_engineer.create_features(dataset, is_training=False)
            
            # Get feature matrix
            X = self.feature_engineer.get_feature_matrix(features_df)
            
            # Generate risk scores
            risk_scores = self.model.calculate_risk_scores(X)
            
            # Add risk scores to dataset
            result_df = dataset.copy()
            result_df['fraud_risk_score'] = risk_scores
            
            self.results = result_df
            self.logger.info("Fraud risk scores generated successfully")
            
            return result_df
            
        except Exception as e:
            self.logger.error(f"Risk score generation failed: {str(e)}")
            raise FraudDetectionError(f"Failed to generate risk scores: {str(e)}")
    
    def save_results(self, filepath: str = None, 
                    include_metadata: bool = True) -> str:
        """
        Save results to CSV file
        
        Args:
            filepath: Output file path
            include_metadata: Whether to include metadata in separate file
            
        Returns:
            Path to saved file
        """
        try:
            if self.results is None:
                raise FraudDetectionError("No results to save. Generate risk scores first.")
            
            # Use default filepath if not provided
            filepath = filepath or self.data_config.output_file
            
            # Save main results
            self.results.to_csv(filepath, index=False)
            self.logger.info(f"Results saved to {filepath}")
            
            # Save metadata if requested
            if include_metadata:
                metadata_path = filepath.replace('.csv', '_metadata.json')
                self._save_metadata(metadata_path)
            
            return filepath
            
        except Exception as e:
            self.logger.error(f"Failed to save results: {str(e)}")
            raise FraudDetectionError(f"Failed to save results: {str(e)}")
    
    def save_model(self, model_path: str = None, encoders_path: str = None) -> Dict[str, str]:
        """
        Save trained model and encoders
        
        Args:
            model_path: Path to save model
            encoders_path: Path to save encoders
            
        Returns:
            Dictionary with saved file paths
        """
        try:
            # Use default paths if not provided
            model_path = model_path or self.data_config.model_file
            encoders_path = encoders_path or self.data_config.encoders_file
            
            # Save model
            self.model.save_model(model_path)
            
            # Save encoders
            self.feature_engineer.save_encoders(encoders_path)
            
            paths = {
                'model': model_path,
                'encoders': encoders_path
            }
            
            self.logger.info(f"Model and encoders saved: {paths}")
            return paths
            
        except Exception as e:
            self.logger.error(f"Failed to save model: {str(e)}")
            raise FraudDetectionError(f"Failed to save model: {str(e)}")
    
    def load_model(self, model_path: str = None, encoders_path: str = None) -> None:
        """
        Load trained model and encoders
        
        Args:
            model_path: Path to model file
            encoders_path: Path to encoders file
        """
        try:
            # Use default paths if not provided
            model_path = model_path or self.data_config.model_file
            encoders_path = encoders_path or self.data_config.encoders_file
            
            # Load model
            self.model.load_model(model_path)
            
            # Load encoders
            self.feature_engineer.load_encoders(encoders_path)
            
            self.logger.info("Model and encoders loaded successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to load model: {str(e)}")
            raise FraudDetectionError(f"Failed to load model: {str(e)}")
    
    def get_system_summary(self) -> Dict[str, Any]:
        """Get comprehensive system summary"""
        summary = {
            'system_status': {
                'dataset_generated': self.dataset is not None,
                'model_trained': self.model.is_trained,
                'results_available': self.results is not None
            },
            'configuration': {
                'data_config': self.data_config.__dict__,
                'model_config': self.model_config.__dict__
            }
        }
        
        if self.dataset is not None:
            summary['dataset_info'] = {
                'total_records': len(self.dataset),
                'fraud_records': len(self.dataset[self.dataset['fraud_label'] == 1]),
                'legitimate_records': len(self.dataset[self.dataset['fraud_label'] == 0])
            }
        
        if self.model.is_trained:
            summary['model_info'] = self.model.get_model_info()
        
        if self.results is not None:
            summary['results_info'] = self._get_results_summary()
        
        return summary
    
    def _log_dataset_statistics(self, dataset: pd.DataFrame) -> None:
        """Log dataset statistics"""
        fraud_count = len(dataset[dataset['fraud_label'] == 1])
        legitimate_count = len(dataset[dataset['fraud_label'] == 0])
        
        self.logger.info(f"Dataset statistics:")
        self.logger.info(f"  - Total records: {len(dataset)}")
        self.logger.info(f"  - Fraudulent claims: {fraud_count} ({fraud_count/len(dataset)*100:.1f}%)")
        self.logger.info(f"  - Legitimate claims: {legitimate_count} ({legitimate_count/len(dataset)*100:.1f}%)")
    
    def _get_results_summary(self) -> Dict[str, Any]:
        """Get summary of results"""
        if self.results is None:
            return {}
        
        risk_scores = self.results['fraud_risk_score']
        
        return {
            'total_claims': len(self.results),
            'average_risk_score': float(risk_scores.mean()),
            'high_risk_claims': len(self.results[risk_scores > self.data_config.high_risk_threshold]),
            'medium_risk_claims': len(self.results[
                (risk_scores >= self.data_config.medium_risk_threshold) & 
                (risk_scores <= self.data_config.high_risk_threshold)
            ]),
            'low_risk_claims': len(self.results[risk_scores < self.data_config.medium_risk_threshold])
        }
    
    def _save_metadata(self, filepath: str) -> None:
        """Save system metadata"""
        import json
        
        metadata = {
            'system_summary': self.get_system_summary(),
            'generation_timestamp': pd.Timestamp.now().isoformat(),
            'version': '1.0.0'
        }
        
        with open(filepath, 'w') as f:
            json.dump(metadata, f, indent=2, default=str)
        
        self.logger.info(f"Metadata saved to {filepath}")


def main():
    """Main execution function"""
    try:
        print("🏥 Ayushman Bharat Fraud Detection System v1.0")
        print("=" * 60)
        
        # Initialize system
        fraud_system = AyushmanBharatFraudDetectionSystem()
        
        # Generate synthetic data
        print("\n📊 Generating synthetic dataset...")
        dataset = fraud_system.generate_synthetic_data(n_rows=500, inject_fraud=True)
        
        # Train model
        print("\n🤖 Training fraud detection model...")
        training_metrics = fraud_system.train_fraud_detection_model(
            tune_hyperparameters=False,
            perform_cv=True
        )
        
        # Generate risk scores
        print("\n📈 Generating fraud risk scores...")
        results = fraud_system.generate_fraud_risk_scores()
        
        # Save results
        print("\n💾 Saving results...")
        output_file = fraud_system.save_results(include_metadata=True)
        
        # Save model
        model_paths = fraud_system.save_model()
        
        # Display summary
        print("\n📋 System Summary:")
        summary = fraud_system.get_system_summary()
        
        dataset_info = summary['dataset_info']
        results_info = summary['results_info']
        model_info = summary['model_info']
        
        print(f"   Dataset: {dataset_info['total_records']} records")
        print(f"   Fraud rate: {dataset_info['fraud_records']/dataset_info['total_records']*100:.1f}%")
        print(f"   Model accuracy: {model_info['training_metrics']['test_accuracy']:.3f}")
        print(f"   Model AUC: {model_info['training_metrics']['test_auc']:.3f}")
        print(f"   Average risk score: {results_info['average_risk_score']:.1f}")
        print(f"   High-risk claims: {results_info['high_risk_claims']}")
        
        # Show top high-risk claims
        print(f"\n🔍 Top 5 High-Risk Claims:")
        high_risk_sample = results.nlargest(5, 'fraud_risk_score')[
            ['claim_id', 'patient_name', 'procedure_name', 'claim_amount', 
             'actual_market_rate', 'fraud_risk_score', 'fraud_label']
        ]
        print(high_risk_sample.to_string(index=False))
        
        print(f"\n✅ Results saved to: {output_file}")
        print(f"📁 Model saved to: {model_paths['model']}")
        
        return fraud_system
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        print(f"Traceback: {traceback.format_exc()}")
        raise


if __name__ == "__main__":
    system = main()