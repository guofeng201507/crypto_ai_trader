"""
Data preprocessing and feature engineering module.
"""
import pandas as pd
import numpy as np
from ta import add_all_ta_features
from ta.utils import dropna
from loguru import logger
from typing import List, Tuple


class DataPreprocessor:
    """Preprocesses cryptocurrency data for machine learning models."""
    
    def __init__(self):
        """Initialize the DataPreprocessor."""
        pass
    
    def clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Clean the data by removing NaN values and outliers.
        
        Args:
            df: Raw data DataFrame
            
        Returns:
            Cleaned DataFrame
        """
        # Remove NaN values
        if df is not None and not df.empty:
            df = dropna(df)
        else:
            raise ValueError("DataFrame is None or empty")
        
        # TODO: Add outlier detection and removal
        
        return df
    
    def add_technical_indicators(self, df: pd.DataFrame, symbol: str = 'BTC/USDT') -> pd.DataFrame:
        """
        Add technical indicators to the data.
        
        Args:
            df: Cleaned data DataFrame
            symbol: Symbol name for column naming
            
        Returns:
            DataFrame with technical indicators
        """
        try:
            # Add all technical analysis features
            df_with_ta = add_all_ta_features(
                df, open="open", high="high", low="low", close="close", volume="volume"
            )
            return df_with_ta
        except Exception as e:
            logger.error(f"Failed to add technical indicators: {e}")
            return df
    
    def create_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Create additional features for ML models.
        
        Args:
            df: DataFrame with technical indicators
            
        Returns:
            DataFrame with additional features
        """
        # Make a copy to avoid modifying the original DataFrame
        df = df.copy()
        
        # Price change features
        df['price_change'] = df['close'].pct_change()
        df['volatility'] = df['price_change'].rolling(window=24).std()
        
        # Volume features
        df['volume_change'] = df['volume'].pct_change()
        
        # Moving averages
        df['ma_7'] = df['close'].rolling(window=7).mean()
        df['ma_25'] = df['close'].rolling(window=25).mean()
        df['ma_99'] = df['close'].rolling(window=99).mean()
        
        # RSI
        df['rsi'] = self._calculate_rsi(df['close'])
        
        return df
    
    def _calculate_rsi(self, prices: pd.Series, window: int = 14) -> pd.Series:
        """
        Calculate Relative Strength Index.
        
        Args:
            prices: Price series
            window: RSI window
            
        Returns:
            RSI series
        """
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def prepare_data_for_training(self, df: pd.DataFrame, 
                                target_column: str = 'close',
                                sequence_length: int = 60) -> Tuple[np.ndarray, np.ndarray]:
        """
        Prepare data for training LSTM models.
        
        Args:
            df: Processed DataFrame
            target_column: Column to predict
            sequence_length: Number of time steps to look back
            
        Returns:
            Tuple of (features, targets)
        """
        # Select numeric columns only
        df_numeric = df.select_dtypes(include=[np.number])
        
        # Normalize the data
        from sklearn.preprocessing import MinMaxScaler
        scaler = MinMaxScaler()
        scaled_data = scaler.fit_transform(df_numeric)
        
        # Create sequences
        X, y = [], []
        for i in range(sequence_length, len(scaled_data)):
            X.append(scaled_data[i-sequence_length:i])
            # Target is the next value of target_column
            target_idx = df_numeric.columns.get_loc(target_column)
            y.append(scaled_data[i, target_idx])
        
        return np.array(X), np.array(y)


def main():
    """Example usage of the DataPreprocessor."""
    # Create sample data
    dates = pd.date_range('2023-01-01', periods=100, freq='H')
    sample_data = pd.DataFrame({
        'open': np.random.rand(100) * 50000 + 20000,
        'high': np.random.rand(100) * 50000 + 20100,
        'low': np.random.rand(100) * 50000 + 19900,
        'close': np.random.rand(100) * 50000 + 20000,
        'volume': np.random.rand(100) * 1000 + 100
    }, index=dates)
    
    preprocessor = DataPreprocessor()
    cleaned_data = preprocessor.clean_data(sample_data)
    print("Cleaned data shape:", cleaned_data.shape)
    
    # Add technical indicators (this would normally work with real data)
    # data_with_indicators = preprocessor.add_technical_indicators(cleaned_data)
    # For sample data, we'll skip this step
    
    # Create features
    data_with_features = preprocessor.create_features(cleaned_data)
    print("Data with features shape:", data_with_features.shape)
    print(data_with_features.head())


if __name__ == "__main__":
    main()