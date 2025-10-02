"""
Model training module for Qlib Crypto Trading
Handles model training, validation, and saving
"""
import qlib
from qlib.config import REG_CN
from qlib.model.trainer import task_train
from qlib.workflow import R
from qlib.utils import init_instance_by_config
from qlib.data.dataset import DatasetH
from qlib.contrib.model.gbdt import LGBModel
from qlib.contrib.strategy import TopkDropoutStrategy
from qlib.contrib.backtest import backtest
from qlib.contrib.ana import risk_analysis
import pandas as pd
import numpy as np
import yaml
import argparse
from loguru import logger
import os


def load_config(config_path: str):
    """
    Load configuration from YAML file
    
    Args:
        config_path: Path to the configuration file
        
    Returns:
        Configuration dictionary
    """
    with open(config_path, 'r') as file:
        config = yaml.safe_load(file)
    return config


def train_model(config: dict):
    """
    Train a model using Qlib
    
    Args:
        config: Configuration dictionary
        
    Returns:
        Trained model and recorder
    """
    # Extract model and dataset configs
    model_config = config['trading']['model']
    dataset_config = config['trading']['dataset']
    
    # Initialize dataset
    dataset = init_instance_by_config(dataset_config)
    
    # Initialize model
    model = init_instance_by_config(model_config)
    
    # Start experiment
    with R.experiment(experiment_name="crypto_model_training"):
        # Fit the model
        model.fit(dataset)
        
        # Log model parameters
        R.log_params(**model_config['kwargs'])
        
        # Get predictions
        preds = model.predict(dataset)
        
        # Log metrics
        R.log_metrics(mse=np.mean(np.square(preds - dataset.prepare("test")['label'].values)))
        
        # Save the model
        R.save_objects(**{"model": model})
        
        # Get recorder for future use
        recorder = R.get_recorder()
        
        return model, recorder


def run_backtest(config: dict, recorder):
    """
    Run backtest using trained model
    
    Args:
        config: Configuration dictionary
        recorder: Trained model recorder
        
    Returns:
        Backtest results
    """
    # Extract backtest config
    backtest_config = config['trading']['backtest']
    strategy_config = config['trading']['strategy']
    
    # Get the trained model
    artifacts = recorder.load_objects()
    model = artifacts["model"]
    
    # Get the dataset
    dataset_config = config['trading']['dataset']
    dataset = init_instance_by_config(dataset_config)
    
    # Get predictions for the test period
    pred_score = model.predict(dataset)
    
    # Initialize strategy
    strategy = init_instance_by_config(strategy_config)
    
    # Run backtest
    report_normal, positions_normal = backtest(
        pred_score,
        strategy,
        backtest_config
    )
    
    return report_normal, positions_normal


def evaluate_model(report_normal: pd.DataFrame):
    """
    Evaluate model performance
    
    Args:
        report_normal: Backtest report
        
    Returns:
        Performance metrics
    """
    # Calculate performance metrics
    excess_return_without_cost = report_normal['return'] - report_normal['bench']
    excess_return_with_cost = report_normal['return'] - report_normal['bench'] - report_normal['cost']
    
    # Calculate Sharpe ratio (annualized)
    sharpe_ratio = np.sqrt(252) * excess_return_without_cost.mean() / excess_return_without_cost.std()
    sharpe_ratio_with_cost = np.sqrt(252) * excess_return_with_cost.mean() / excess_return_with_cost.std()
    
    # Calculate maximum drawdown
    cum_return = (1 + excess_return_without_cost).cumprod()
    rolling_max = cum_return.expanding().max()
    drawdown = (cum_return - rolling_max) / rolling_max
    max_drawdown = drawdown.min()
    
    # Total return
    total_return = cum_return.iloc[-1] - 1
    
    metrics = {
        "sharpe_ratio": sharpe_ratio,
        "sharpe_ratio_with_cost": sharpe_ratio_with_cost,
        "max_drawdown": max_drawdown,
        "total_return": total_return,
        "annual_return": excess_return_without_cost.mean() * 252,
        "volatility": excess_return_without_cost.std() * np.sqrt(252)
    }
    
    return metrics


def main(config_path: str):
    """
    Main training function
    
    Args:
        config_path: Path to the configuration file
    """
    logger.info("Loading configuration...")
    config = load_config(config_path)
    
    # Initialize Qlib
    qlib_dir = os.path.expanduser("~/.qlib/qlib_data/cryptocurrency")
    qlib.init(provider_uri=qlib_dir, region='crypto', freq='1min')
    
    logger.info("Starting model training...")
    model, recorder = train_model(config)
    
    logger.info("Running backtest...")
    report_normal, positions_normal = run_backtest(config, recorder)
    
    logger.info("Evaluating model performance...")
    metrics = evaluate_model(report_normal)
    
    logger.info("Performance Metrics:")
    for metric, value in metrics.items():
        logger.info(f"{metric}: {value}")
    
    logger.info("Model training and evaluation completed!")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train a model for crypto trading with Qlib")
    parser.add_argument("--config", type=str, required=True, help="Path to configuration file")
    
    args = parser.parse_args()
    
    main(args.config)