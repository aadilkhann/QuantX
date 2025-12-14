"""
Deep Learning Models for Time-Series Prediction.

This module implements LSTM and GRU models for sequential data prediction
in trading applications.
"""

from typing import Dict, Any, Optional, Tuple, List
import numpy as np
import pandas as pd
from pathlib import Path
from loguru import logger

try:
    import torch
    import torch.nn as nn
    import torch.optim as optim
    from torch.utils.data import Dataset, DataLoader
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False
    logger.warning("PyTorch not available. Deep learning models will not work.")

from quantx.ml.models.base import BaseModel, ModelMetadata


class SequenceDataset(Dataset):
    """Dataset for sequence data."""
    
    def __init__(self, X: np.ndarray, y: np.ndarray):
        """
        Initialize dataset.
        
        Args:
            X: Input sequences (samples, sequence_length, features)
            y: Target values (samples,)
        """
        self.X = torch.FloatTensor(X)
        self.y = torch.FloatTensor(y)
    
    def __len__(self) -> int:
        return len(self.X)
    
    def __getitem__(self, idx: int) -> Tuple[torch.Tensor, torch.Tensor]:
        return self.X[idx], self.y[idx]


class LSTMNetwork(nn.Module):
    """LSTM neural network."""
    
    def __init__(
        self,
        input_size: int,
        hidden_size: int = 64,
        num_layers: int = 2,
        dropout: float = 0.2,
        bidirectional: bool = False,
        output_size: int = 1
    ):
        """
        Initialize LSTM network.
        
        Args:
            input_size: Number of input features
            hidden_size: Number of hidden units
            num_layers: Number of LSTM layers
            dropout: Dropout rate
            bidirectional: Use bidirectional LSTM
            output_size: Number of output units
        """
        super().__init__()
        
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        self.bidirectional = bidirectional
        
        # LSTM layer
        self.lstm = nn.LSTM(
            input_size=input_size,
            hidden_size=hidden_size,
            num_layers=num_layers,
            dropout=dropout if num_layers > 1 else 0,
            bidirectional=bidirectional,
            batch_first=True
        )
        
        # Output layer
        lstm_output_size = hidden_size * 2 if bidirectional else hidden_size
        self.fc = nn.Linear(lstm_output_size, output_size)
        self.dropout = nn.Dropout(dropout)
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Forward pass.
        
        Args:
            x: Input tensor (batch, sequence, features)
            
        Returns:
            Output tensor (batch, output_size)
        """
        # LSTM forward
        lstm_out, _ = self.lstm(x)
        
        # Take last output
        last_output = lstm_out[:, -1, :]
        
        # Dropout and fully connected
        out = self.dropout(last_output)
        out = self.fc(out)
        
        return out


class GRUNetwork(nn.Module):
    """GRU neural network."""
    
    def __init__(
        self,
        input_size: int,
        hidden_size: int = 64,
        num_layers: int = 2,
        dropout: float = 0.2,
        bidirectional: bool = False,
        output_size: int = 1
    ):
        """
        Initialize GRU network.
        
        Args:
            input_size: Number of input features
            hidden_size: Number of hidden units
            num_layers: Number of GRU layers
            dropout: Dropout rate
            bidirectional: Use bidirectional GRU
            output_size: Number of output units
        """
        super().__init__()
        
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        self.bidirectional = bidirectional
        
        # GRU layer
        self.gru = nn.GRU(
            input_size=input_size,
            hidden_size=hidden_size,
            num_layers=num_layers,
            dropout=dropout if num_layers > 1 else 0,
            bidirectional=bidirectional,
            batch_first=True
        )
        
        # Output layer
        gru_output_size = hidden_size * 2 if bidirectional else hidden_size
        self.fc = nn.Linear(gru_output_size, output_size)
        self.dropout = nn.Dropout(dropout)
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Forward pass.
        
        Args:
            x: Input tensor (batch, sequence, features)
            
        Returns:
            Output tensor (batch, output_size)
        """
        # GRU forward
        gru_out, _ = self.gru(x)
        
        # Take last output
        last_output = gru_out[:, -1, :]
        
        # Dropout and fully connected
        out = self.dropout(last_output)
        out = self.fc(out)
        
        return out


class LSTMModel(BaseModel):
    """
    LSTM model for time-series prediction.
    
    Example:
        >>> model = LSTMModel(
        ...     sequence_length=20,
        ...     hidden_size=64,
        ...     num_layers=2
        ... )
        >>> model.fit(X_train, y_train)
        >>> predictions = model.predict(X_test)
    """
    
    def __init__(
        self,
        sequence_length: int = 20,
        hidden_size: int = 64,
        num_layers: int = 2,
        dropout: float = 0.2,
        bidirectional: bool = False,
        learning_rate: float = 0.001,
        batch_size: int = 32,
        epochs: int = 100,
        early_stopping_patience: int = 10,
        device: Optional[str] = None,
        **kwargs
    ):
        """
        Initialize LSTM model.
        
        Args:
            sequence_length: Length of input sequences
            hidden_size: Number of hidden units
            num_layers: Number of LSTM layers
            dropout: Dropout rate
            bidirectional: Use bidirectional LSTM
            learning_rate: Learning rate
            batch_size: Batch size for training
            epochs: Maximum number of epochs
            early_stopping_patience: Patience for early stopping
            device: Device to use (cuda/cpu)
            **kwargs: Additional parameters
        """
        if not TORCH_AVAILABLE:
            raise ImportError("PyTorch is required for LSTM model")
        
        super().__init__(**kwargs)
        
        self.sequence_length = sequence_length
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        self.dropout = dropout
        self.bidirectional = bidirectional
        self.learning_rate = learning_rate
        self.batch_size = batch_size
        self.epochs = epochs
        self.early_stopping_patience = early_stopping_patience
        
        # Device
        if device is None:
            self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        else:
            self.device = torch.device(device)
        
        # Model
        self.network: Optional[LSTMNetwork] = None
        self.optimizer: Optional[optim.Optimizer] = None
        self.criterion: Optional[nn.Module] = None
        
        # Training history
        self.train_losses: List[float] = []
        self.val_losses: List[float] = []
        
        # Metadata
        self.metadata = ModelMetadata(
            model_type="lstm",
            framework="pytorch",
            version="1.0.0"
        )
        
        logger.info(f"Initialized LSTM model on device: {self.device}")
    
    def _prepare_sequences(
        self,
        X: pd.DataFrame,
        y: Optional[pd.Series] = None
    ) -> Tuple[np.ndarray, Optional[np.ndarray]]:
        """
        Prepare sequences from data.
        
        Args:
            X: Input features
            y: Target values (optional)
            
        Returns:
            Tuple of (X_sequences, y_sequences)
        """
        X_array = X.values if isinstance(X, pd.DataFrame) else X
        
        # Create sequences
        X_sequences = []
        y_sequences = [] if y is not None else None
        
        for i in range(len(X_array) - self.sequence_length):
            X_sequences.append(X_array[i:i + self.sequence_length])
            if y is not None:
                y_array = y.values if isinstance(y, pd.Series) else y
                y_sequences.append(y_array[i + self.sequence_length])
        
        X_sequences = np.array(X_sequences)
        if y_sequences is not None:
            y_sequences = np.array(y_sequences)
        
        return X_sequences, y_sequences
    
    def fit(
        self,
        X: pd.DataFrame,
        y: pd.Series,
        X_val: Optional[pd.DataFrame] = None,
        y_val: Optional[pd.Series] = None
    ) -> "LSTMModel":
        """
        Train the LSTM model.
        
        Args:
            X: Training features
            y: Training targets
            X_val: Validation features (optional)
            y_val: Validation targets (optional)
            
        Returns:
            Self
        """
        # Prepare sequences
        X_seq, y_seq = self._prepare_sequences(X, y)
        
        # Initialize network
        input_size = X_seq.shape[2]
        output_size = 1 if len(y_seq.shape) == 1 else y_seq.shape[1]
        
        self.network = LSTMNetwork(
            input_size=input_size,
            hidden_size=self.hidden_size,
            num_layers=self.num_layers,
            dropout=self.dropout,
            bidirectional=self.bidirectional,
            output_size=output_size
        ).to(self.device)
        
        # Optimizer and loss
        self.optimizer = optim.Adam(self.network.parameters(), lr=self.learning_rate)
        self.criterion = nn.MSELoss()
        
        # Create dataset and dataloader
        train_dataset = SequenceDataset(X_seq, y_seq)
        train_loader = DataLoader(
            train_dataset,
            batch_size=self.batch_size,
            shuffle=True
        )
        
        # Validation data
        val_loader = None
        if X_val is not None and y_val is not None:
            X_val_seq, y_val_seq = self._prepare_sequences(X_val, y_val)
            val_dataset = SequenceDataset(X_val_seq, y_val_seq)
            val_loader = DataLoader(val_dataset, batch_size=self.batch_size)
        
        # Training loop
        best_val_loss = float('inf')
        patience_counter = 0
        
        for epoch in range(self.epochs):
            # Training
            self.network.train()
            train_loss = 0.0
            
            for batch_X, batch_y in train_loader:
                batch_X = batch_X.to(self.device)
                batch_y = batch_y.to(self.device)
                
                # Forward pass
                self.optimizer.zero_grad()
                outputs = self.network(batch_X)
                loss = self.criterion(outputs.squeeze(), batch_y)
                
                # Backward pass
                loss.backward()
                self.optimizer.step()
                
                train_loss += loss.item()
            
            train_loss /= len(train_loader)
            self.train_losses.append(train_loss)
            
            # Validation
            if val_loader is not None:
                self.network.eval()
                val_loss = 0.0
                
                with torch.no_grad():
                    for batch_X, batch_y in val_loader:
                        batch_X = batch_X.to(self.device)
                        batch_y = batch_y.to(self.device)
                        
                        outputs = self.network(batch_X)
                        loss = self.criterion(outputs.squeeze(), batch_y)
                        val_loss += loss.item()
                
                val_loss /= len(val_loader)
                self.val_losses.append(val_loss)
                
                # Early stopping
                if val_loss < best_val_loss:
                    best_val_loss = val_loss
                    patience_counter = 0
                else:
                    patience_counter += 1
                
                if patience_counter >= self.early_stopping_patience:
                    logger.info(f"Early stopping at epoch {epoch + 1}")
                    break
                
                if (epoch + 1) % 10 == 0:
                    logger.info(
                        f"Epoch {epoch + 1}/{self.epochs} - "
                        f"Train Loss: {train_loss:.4f}, Val Loss: {val_loss:.4f}"
                    )
            else:
                if (epoch + 1) % 10 == 0:
                    logger.info(
                        f"Epoch {epoch + 1}/{self.epochs} - Train Loss: {train_loss:.4f}"
                    )
        
        self.is_fitted = True
        logger.info("LSTM model training complete")
        return self
    
    def predict(self, X: pd.DataFrame) -> np.ndarray:
        """
        Make predictions.
        
        Args:
            X: Input features
            
        Returns:
            Predictions
        """
        if not self.is_fitted or self.network is None:
            raise ValueError("Model not fitted")
        
        # Prepare sequences
        X_seq, _ = self._prepare_sequences(X)
        
        # Predict
        self.network.eval()
        with torch.no_grad():
            X_tensor = torch.FloatTensor(X_seq).to(self.device)
            predictions = self.network(X_tensor)
            predictions = predictions.cpu().numpy().squeeze()
        
        return predictions
    
    def save(self, path: str) -> None:
        """Save model to disk."""
        if self.network is None:
            raise ValueError("No model to save")
        
        save_dict = {
            'network_state': self.network.state_dict(),
            'sequence_length': self.sequence_length,
            'hidden_size': self.hidden_size,
            'num_layers': self.num_layers,
            'dropout': self.dropout,
            'bidirectional': self.bidirectional,
            'train_losses': self.train_losses,
            'val_losses': self.val_losses,
            'metadata': self.metadata.__dict__
        }
        
        torch.save(save_dict, path)
        logger.info(f"Saved LSTM model to {path}")
    
    @classmethod
    def load(cls, path: str) -> "LSTMModel":
        """Load model from disk."""
        if not TORCH_AVAILABLE:
            raise ImportError("PyTorch is required")
        
        checkpoint = torch.load(path)
        
        model = cls(
            sequence_length=checkpoint['sequence_length'],
            hidden_size=checkpoint['hidden_size'],
            num_layers=checkpoint['num_layers'],
            dropout=checkpoint['dropout'],
            bidirectional=checkpoint['bidirectional']
        )
        
        # Reconstruct network (need input size from state dict)
        state_dict = checkpoint['network_state']
        input_size = state_dict['lstm.weight_ih_l0'].shape[1]
        
        model.network = LSTMNetwork(
            input_size=input_size,
            hidden_size=model.hidden_size,
            num_layers=model.num_layers,
            dropout=model.dropout,
            bidirectional=model.bidirectional
        ).to(model.device)
        
        model.network.load_state_dict(state_dict)
        model.train_losses = checkpoint.get('train_losses', [])
        model.val_losses = checkpoint.get('val_losses', [])
        model.is_fitted = True
        
        logger.info(f"Loaded LSTM model from {path}")
        return model


class GRUModel(LSTMModel):
    """
    GRU model for time-series prediction.
    
    Similar to LSTM but uses GRU cells which are faster to train.
    """
    
    def __init__(self, **kwargs):
        """Initialize GRU model with same parameters as LSTM."""
        super().__init__(**kwargs)
        self.metadata.model_type = "gru"
    
    def fit(
        self,
        X: pd.DataFrame,
        y: pd.Series,
        X_val: Optional[pd.DataFrame] = None,
        y_val: Optional[pd.Series] = None
    ) -> "GRUModel":
        """Train the GRU model."""
        # Prepare sequences
        X_seq, y_seq = self._prepare_sequences(X, y)
        
        # Initialize network with GRU
        input_size = X_seq.shape[2]
        output_size = 1 if len(y_seq.shape) == 1 else y_seq.shape[1]
        
        self.network = GRUNetwork(
            input_size=input_size,
            hidden_size=self.hidden_size,
            num_layers=self.num_layers,
            dropout=self.dropout,
            bidirectional=self.bidirectional,
            output_size=output_size
        ).to(self.device)
        
        # Rest is same as LSTM
        return super(LSTMModel, self).fit(X, y, X_val, y_val)
