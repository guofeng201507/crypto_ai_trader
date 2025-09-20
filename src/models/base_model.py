"""
Base model class and LSTM implementation for cryptocurrency price prediction.
"""
import numpy as np
import pandas as pd
from tensorflow import keras
from tensorflow.keras import layers
from sklearn.metrics import mean_squared_error, mean_absolute_error
from loguru import logger
from typing import Tuple, Any


class BaseModel:
    """Base class for all ML models."""
    
    def __init__(self, name: str):
        """
        Initialize the base model.
        
        Args:
            name: Name of the model
        """
        self.name = name
        self.model = None
        self.is_trained = False
    
    def train(self, X: np.ndarray, y: np.ndarray) -> dict:
        """
        Train the model.
        
        Args:
            X: Training features
            y: Training targets
            
        Returns:
            Dictionary with training metrics
        """
        raise NotImplementedError("Subclasses must implement train method")
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        """
        Make predictions with the model.
        
        Args:
            X: Input features
            
        Returns:
            Predictions
        """
        if not self.is_trained:
            raise ValueError("Model must be trained before making predictions")
        raise NotImplementedError("Subclasses must implement predict method")
    
    def evaluate(self, X: np.ndarray, y: np.ndarray) -> dict:
        """
        Evaluate the model.
        
        Args:
            X: Test features
            y: Test targets
            
        Returns:
            Dictionary with evaluation metrics
        """
        predictions = self.predict(X)
        mse = mean_squared_error(y, predictions)
        mae = mean_absolute_error(y, predictions)
        
        return {
            'mse': mse,
            'mae': mae,
            'rmse': np.sqrt(mse)
        }
    
    def save_model(self, filepath: str):
        """
        Save the model to disk.
        
        Args:
            filepath: Path to save the model
        """
        raise NotImplementedError("Subclasses must implement save_model method")
    
    def load_model(self, filepath: str):
        """
        Load the model from disk.
        
        Args:
            filepath: Path to load the model from
        """
        raise NotImplementedError("Subclasses must implement load_model method")


class LSTMModel(BaseModel):
    """LSTM model for cryptocurrency price prediction."""
    
    def __init__(self, sequence_length: int = 60, features_count: int = 10):
        """
        Initialize the LSTM model.
        
        Args:
            sequence_length: Number of time steps to look back
            features_count: Number of features in the input data
        """
        super().__init__("LSTM")
        self.sequence_length = sequence_length
        self.features_count = features_count
        self.model = self._build_model()
    
    def _build_model(self) -> keras.Model:
        """Build the LSTM model architecture."""
        model = keras.Sequential([
            layers.LSTM(50, return_sequences=True, input_shape=(self.sequence_length, self.features_count)),
            layers.Dropout(0.2),
            layers.LSTM(50, return_sequences=True),
            layers.Dropout(0.2),
            layers.LSTM(50),
            layers.Dropout(0.2),
            layers.Dense(1)
        ])
        
        model.compile(optimizer='adam', loss='mean_squared_error')
        return model
    
    def train(self, X: np.ndarray, y: np.ndarray, epochs: int = 50, batch_size: int = 32,
              validation_split: float = 0.1) -> dict:
        """
        Train the LSTM model.
        
        Args:
            X: Training features
            y: Training targets
            epochs: Number of training epochs
            batch_size: Batch size for training
            validation_split: Fraction of data to use for validation
            
        Returns:
            Dictionary with training history
        """
        if X.shape[1] != self.sequence_length or X.shape[2] != self.features_count:
            raise ValueError(f"Input shape {X.shape} doesn't match expected shape "
                           f"({self.sequence_length}, {self.features_count})")
        
        history = self.model.fit(
            X, y,
            epochs=epochs,
            batch_size=batch_size,
            validation_split=validation_split,
            verbose=1
        )
        
        self.is_trained = True
        return history.history
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        """
        Make predictions with the LSTM model.
        
        Args:
            X: Input features
            
        Returns:
            Predictions
        """
        super().predict(X)
        return self.model.predict(X)
    
    def save_model(self, filepath: str):
        """Save the LSTM model to disk."""
        super().save_model(filepath)
        self.model.save(filepath)
        logger.info(f"Model saved to {filepath}")
    
    def load_model(self, filepath: str):
        """Load the LSTM model from disk."""
        super().load_model(filepath)
        self.model = keras.models.load_model(filepath)
        self.is_trained = True
        logger.info(f"Model loaded from {filepath}")


def main():
    """Example usage of the LSTMModel."""
    # Create sample data
    sequence_length = 60
    features_count = 10
    samples = 1000
    
    X = np.random.rand(samples, sequence_length, features_count)
    y = np.random.rand(samples)
    
    # Create and train model
    model = LSTMModel(sequence_length, features_count)
    print("Model created successfully")
    
    # For a quick test, we'll just run a few epochs
    # In practice, you'd want to train for more epochs
    try:
        history = model.train(X, y, epochs=2, batch_size=32)
        print("Model trained successfully")
        print(f"Training loss: {history['loss'][-1]:.4f}")
    except Exception as e:
        logger.error(f"Training failed: {e}")


if __name__ == "__main__":
    main()