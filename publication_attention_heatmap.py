import os
import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
import pandas as pd
from torch.utils.data import DataLoader, Dataset
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.colors import LinearSegmentedColormap
from tqdm.auto import tqdm
import h5py
import json
import cv2
import random
import warnings
warnings.filterwarnings('ignore')

# Set random seeds for reproducibility
def seed_everything(seed=42):
    random.seed(seed)
    os.environ['PYTHONHASHSEED'] = str(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed(seed)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False
    
seed_everything(42)

# Configuration - should match training config
class OptimizedConfig:
    # Data parameters
    FEATURE_DIM = 1024
    NUM_TILES = 16
    
    # Model parameters
    HIDDEN_DIM = 256
    OUTPUT_DIM = 2
    DROPOUT_RATE = 0.3
    FEATURE_DROPOUT = 0.15
    NUM_ATTENTION_HEADS = 4
    NUM_LAYERS = 2
    
    # Paths - UPDATE THESE TO MATCH YOUR TRAINING SETUP
    SAVE_DIR = "/kaggle/working/optimized_auto_selected_models"
    FEATURES_DIR = "/kaggle/working/train_auto_selected_preserved_test_features"
    IMAGES_DIR = "../input/4096-tiles-v4/train-4096-tiles-v4/4096-tiles-v4/"
    
    # Advanced settings
    USE_DUAL_BRANCH = True
    USE_MULTI_SAMPLE_DROPOUT = True
    MULTI_SAMPLE_DROPOUT_COUNT = 4

# Feature Transformer (same as training)
class FeatureTransformer:
    def __init__(self, method='power'):
        from sklearn.preprocessing import PowerTransformer, RobustScaler, StandardScaler
        self.method = method
        if method == 'power':
            self.transformer = PowerTransformer(method='yeo-johnson')
        elif method == 'robust':
            self.transformer = RobustScaler(quantile_range=(10, 90))
        else:
            self.transformer = StandardScaler()
        self.fitted = False
        
    def fit(self, features):
        if features.shape[0] > 0:
            if len(features.shape) > 2:
                flat_features = features.reshape(-1, features.shape[-1])
            else:
                flat_features = features
            self.transformer.fit(flat_features)
            self.fitted = True
        
    def transform(self, features):
        if not self.fitted:
            return features
        original_shape = features.shape
        if len(original_shape) > 2:
            flat_features = features.reshape(-1, original_shape[-1])
        else:
            flat_features = features
        transformed = self.transformer.transform(flat_features)
        if len(original_shape) > 2:
            transformed = transformed.reshape(original_shape)
        return transformed

# Dataset for auto-selected tiles (same as training)
class OptimizedDataset(Dataset):
    def __init__(self, df, data_dir, transformer=None, metadata_path=None):
        self.df = df
        self.data_dir = data_dir
        self.transformer = transformer
        self.tile_selections = {}
        
        # Load tile selection metadata
        if metadata_path is None:
            metadata_path = f"{data_dir}/tile_selections_metadata.json"
        
        if os.path.exists(metadata_path):
            try:
                with open(metadata_path, 'r') as f:
                    self.tile_selections = json.load(f)
                print(f"Loaded tile selections for {len(self.tile_selections)} images")
            except Exception as e:
                print(f"Error loading tile selections metadata: {e}")
                self.tile_selections = {}
        else:
            print("Warning: No tile selection metadata found")
    
    def __len__(self):
        return len(self.df)
        
    def __getitem__(self, index):
        image_id = self.df.iloc[index].image_id
        
        # Handle label extraction
        if 'label' in self.df.columns:
            label_value = self.df.iloc[index].label
            if isinstance(label_value, str):
                label = 0 if label_value == "CE" else 1
            else:
                label = label_value
        else:
            label = -1
            
        try:
            full_path = f"{self.data_dir}/{image_id}.h5"
            with h5py.File(full_path, 'r') as hdf5_file:
                # Get the selected tile indices for this image
                if image_id in self.tile_selections:
                    selected_indices = self.tile_selections[image_id][:16]
                else:
                    # Fallback: infer from H5 file keys
                    available_keys = list(hdf5_file.keys())
                    numeric_keys = []
                    for key in available_keys:
                        try:
                            if key != 'tile_selections_metadata':
                                numeric_keys.append(int(key))
                        except ValueError:
                            continue
                    
                    if len(numeric_keys) >= 16:
                        selected_indices = sorted(numeric_keys)[:16]
                    else:
                        selected_indices = sorted(numeric_keys)
                        while len(selected_indices) < 16:
                            selected_indices.append(selected_indices[0] if selected_indices else 0)
                
                # Load features for selected tiles
                tiles = []
                for i, tile_idx in enumerate(selected_indices):
                    if str(tile_idx) in hdf5_file:
                        feat = torch.tensor(hdf5_file[str(tile_idx)][:])
                        if len(feat.shape) > 1 and feat.shape[0] == 1:
                            feat = feat.squeeze(0)
                        tiles.append(feat)
                    else:
                        # Random noise for missing tiles
                        seed_val = hash(f"{image_id}_{tile_idx}") % 10000
                        torch.manual_seed(seed_val)
                        tiles.append(torch.zeros(OptimizedConfig.FEATURE_DIM) + 
                                   torch.randn(OptimizedConfig.FEATURE_DIM) * 0.01)
                
                # Ensure exactly 16 tiles
                while len(tiles) < 16:
                    tiles.append(torch.zeros(OptimizedConfig.FEATURE_DIM))
                tiles = tiles[:16]
                
                features = torch.stack(tiles, dim=0)
                
                # Apply feature transformation
                if self.transformer is not None and hasattr(self.transformer, 'transform'):
                    features_np = features.numpy()
                    features_np = self.transformer.transform(features_np)
                    features = torch.tensor(features_np, dtype=torch.float32)
                    
        except Exception as e:
            print(f"Error loading features for {image_id}: {str(e)}")
            torch.manual_seed(hash(image_id) % 10000)
            features = torch.zeros((OptimizedConfig.NUM_TILES, OptimizedConfig.FEATURE_DIM)) + \
                      torch.randn((OptimizedConfig.NUM_TILES, OptimizedConfig.FEATURE_DIM)) * 0.01
            
        return features, label, image_id

# Model architecture (same as training)
class TransformerEncoderBlock(nn.Module):
    def __init__(self, hidden_dim, num_heads, dropout_rate):
        super(TransformerEncoderBlock, self).__init__()
        
        self.norm1 = nn.LayerNorm(hidden_dim)
        self.self_attention = nn.MultiheadAttention(
            embed_dim=hidden_dim, 
            num_heads=num_heads,
            dropout=dropout_rate * 0.5,
            batch_first=True
        )
        self.dropout1 = nn.Dropout(dropout_rate)
        
        self.norm2 = nn.LayerNorm(hidden_dim)
        self.feed_forward = nn.Sequential(
            nn.Linear(hidden_dim, hidden_dim * 2),
            nn.GELU(),
            nn.Dropout(dropout_rate),
            nn.Linear(hidden_dim * 2, hidden_dim)
        )
        self.dropout2 = nn.Dropout(dropout_rate)
        
    def forward(self, x):
        normalized = self.norm1(x)
        attention_output, attention_weights = self.self_attention(normalized, normalized, normalized)
        x = x + self.dropout1(attention_output)
        
        normalized = self.norm2(x)
        ff_output = self.feed_forward(normalized)
        x = x + self.dropout2(ff_output)
        
        return x, attention_weights

class GlobalAttentionPool(nn.Module):
    def __init__(self, hidden_dim, dropout_rate):
        super(GlobalAttentionPool, self).__init__()
        
        self.attention = nn.Sequential(
            nn.Linear(hidden_dim, hidden_dim // 2),
            nn.LayerNorm(hidden_dim // 2),
            nn.GELU(),
            nn.Linear(hidden_dim // 2, 1)
        )
        self.dropout = nn.Dropout(dropout_rate)
        
    def forward(self, x):
        attention_weights = F.softmax(self.attention(x), dim=1)
        weighted_sum = torch.sum(x * attention_weights, dim=1)
        weighted_sum = self.dropout(weighted_sum)
        return weighted_sum, attention_weights

class OptimizedModel(nn.Module):
    def __init__(self, config):
        super(OptimizedModel, self).__init__()
        
        self.config = config
        input_dim = config.FEATURE_DIM
        hidden_dim = config.HIDDEN_DIM
        output_dim = config.OUTPUT_DIM
        dropout_rate = config.DROPOUT_RATE
        num_heads = config.NUM_ATTENTION_HEADS
        num_layers = config.NUM_LAYERS
        
        # Initial embedding with batch normalization
        self.embedding = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.BatchNorm1d(hidden_dim),
            nn.GELU(),
            nn.Dropout(dropout_rate * 0.5)
        )
        
        # Position embeddings
        self.position_embedding = nn.Parameter(torch.zeros(1, config.NUM_TILES, hidden_dim))
        nn.init.normal_(self.position_embedding, std=0.01)
        
        # Transformer encoder blocks
        self.encoder_blocks = nn.ModuleList([
            TransformerEncoderBlock(hidden_dim, num_heads, dropout_rate)
            for _ in range(num_layers)
        ])
        
        # Global attention pooling
        self.global_pool = GlobalAttentionPool(hidden_dim, dropout_rate)
        
        # Attention-based tile selection mechanism (from training)
        self.tile_attention = nn.Sequential(
            nn.Linear(hidden_dim, hidden_dim // 4),
            nn.Tanh(),
            nn.Linear(hidden_dim // 4, 1)
        )
        
        # Dual branch architecture
        if config.USE_DUAL_BRANCH:
            self.ce_branch = nn.Sequential(
                nn.Linear(hidden_dim, hidden_dim // 2),
                nn.GELU(),
                nn.Dropout(dropout_rate * 0.7),
                nn.Linear(hidden_dim // 2, hidden_dim // 2),
                nn.GELU()
            )
            
            self.laa_branch = nn.Sequential(
                nn.Linear(hidden_dim, hidden_dim // 2),
                nn.GELU(),
                nn.Dropout(dropout_rate * 1.3),
                nn.Linear(hidden_dim // 2, hidden_dim // 2),
                nn.GELU()
            )
            
            if config.USE_MULTI_SAMPLE_DROPOUT:
                self.multi_dropouts = nn.ModuleList([
                    nn.Dropout(0.1 + 0.1 * i) for i in range(config.MULTI_SAMPLE_DROPOUT_COUNT)
                ])
                self.classifiers = nn.ModuleList([
                    nn.Linear(hidden_dim, output_dim) for _ in range(config.MULTI_SAMPLE_DROPOUT_COUNT)
                ])
            else:
                self.classifier = nn.Linear(hidden_dim, output_dim)
        else:
            if config.USE_MULTI_SAMPLE_DROPOUT:
                self.multi_dropouts = nn.ModuleList([
                    nn.Dropout(0.1 + 0.1 * i) for i in range(config.MULTI_SAMPLE_DROPOUT_COUNT)
                ])
                self.classifiers = nn.ModuleList([
                    nn.Linear(hidden_dim, output_dim) for _ in range(config.MULTI_SAMPLE_DROPOUT_COUNT)
                ])
            else:
                self.classifier = nn.Sequential(
                    nn.Dropout(dropout_rate),
                    nn.Linear(hidden_dim, hidden_dim // 2),
                    nn.GELU(),
                    nn.Dropout(dropout_rate * 0.5),
                    nn.Linear(hidden_dim // 2, output_dim)
                )
        
    def _apply_embeddings(self, x):
        batch_size, num_tiles, feat_dim = x.shape
        x_flat = x.reshape(-1, feat_dim)
        embedded = self.embedding(x_flat)
        embedded = embedded.reshape(batch_size, num_tiles, -1)
        embedded = embedded + self.position_embedding[:, :num_tiles, :]
        return embedded
            
    def forward(self, x, return_attention=False):
        # Apply initial embedding
        x = self._apply_embeddings(x)
        
        # Apply transformer encoder blocks
        attention_weights_list = []
        for block in self.encoder_blocks:
            x, attention_weights = block(x)
            attention_weights_list.append(attention_weights)
        
        # Global attention pooling
        pooled, global_attention = self.global_pool(x)
        
        # Dual branch architecture
        if hasattr(self, 'ce_branch') and hasattr(self, 'laa_branch'):
            ce_features = self.ce_branch(pooled)
            laa_features = self.laa_branch(pooled)
            combined_features = torch.cat([ce_features, laa_features], dim=1)
            
            if hasattr(self, 'multi_dropouts'):
                logits = []
                for i, dropout in enumerate(self.multi_dropouts):
                    dropout_features = dropout(combined_features)
                    logits.append(self.classifiers[i](dropout_features))
                logits = torch.mean(torch.stack(logits), dim=0)
            else:
                logits = self.classifier(combined_features)
        else:
            if hasattr(self, 'multi_dropouts'):
                logits = []
                for i, dropout in enumerate(self.multi_dropouts):
                    dropout_features = dropout(pooled)
                    logits.append(self.classifiers[i](dropout_features))
                logits = torch.mean(torch.stack(logits), dim=0)
            else:
                logits = self.classifier(pooled)
        
        if return_attention:
            return logits, global_attention, attention_weights_list
        else:
            return logits

# Load trained model
def load_trained_model(model_path, config):
    """Load the trained model from checkpoint"""
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    
    print(f"Loading model from: {model_path}")
    checkpoint = torch.load(model_path, map_location=device)
    
    # Create model
    if checkpoint.get('is_swa', False):
        model = torch.optim.swa_utils.AveragedModel(OptimizedModel(config))
        model.to(device)
        model.load_state_dict(checkpoint['model_state_dict'])
    else:
        model = OptimizedModel(config).to(device)
        model.load_state_dict(checkpoint['model_state_dict'])
    
    # Load other components
    threshold = checkpoint.get('threshold', 0.5)
    temperature = checkpoint.get('temperature', 1.0)
    transformer = checkpoint.get('transformer', None)
    metrics = checkpoint.get('metrics', {})
    
    print(f"Model loaded successfully!")
    print(f"Threshold: {threshold:.4f}, Temperature: {temperature:.4f}")
    
    return model, threshold, temperature, transformer, metrics

# PUBLICATION-QUALITY HEATMAP FUNCTION
def create_publication_figure(attention, image_id, tile_selections_metadata, 
                             main_image_path, prediction_probs=None, true_label=None,
                             save_path=None, dpi=300):
    """
    Create publication-quality 3-panel figure without extra text
    
    Args:
        attention: (16,) attention weights from model
        image_id: Image identifier
        tile_selections_metadata: Dict with selected tile indices
        main_image_path: Path to main images
        prediction_probs: [CE_prob, LAA_prob] if available
        true_label: True label if available
        save_path: Path to save figure
        dpi: Resolution for saving
    """
    
    # Set publication parameters
    plt.rcParams['font.family'] = 'Arial'
    plt.rcParams['font.size'] = 14
    plt.rcParams['axes.linewidth'] = 2
    plt.rcParams['xtick.major.width'] = 2
    plt.rcParams['ytick.major.width'] = 2
    plt.rcParams['xtick.major.size'] = 6
    plt.rcParams['ytick.major.size'] = 6
    
    # Load main image
    try:
        main_img = cv2.imread(f"{main_image_path}/{image_id}.jpg")
        if main_img is not None:
            main_img = cv2.cvtColor(main_img, cv2.COLOR_BGR2RGB)
        else:
            main_img = np.ones((4096, 4096, 3), dtype=np.uint8) * 200
    except:
        main_img = np.ones((4096, 4096, 3), dtype=np.uint8) * 200
    
    # Get selected tile indices
    if image_id in tile_selections_metadata:
        selected_indices = tile_selections_metadata[image_id][:16]
    else:
        selected_indices = list(range(16))
    
    # Create 8x8 heatmap grid
    full_heatmap = np.zeros((8, 8))
    
    # Ensure attention is flat
    if len(attention.shape) > 1:
        attention_flat = attention.flatten()[:16]
    else:
        attention_flat = attention[:16]
    
    # Map attention to grid positions
    for i, original_tile_idx in enumerate(selected_indices):
        if i < len(attention_flat):
            row = original_tile_idx // 8
            col = original_tile_idx % 8
            if 0 <= row < 8 and 0 <= col < 8:
                full_heatmap[row, col] = attention_flat[i]
    
    # Create high-quality figure
    fig = plt.figure(figsize=(18, 6))
    
    # Panel 1: Selected tiles
    ax1 = plt.subplot(131)
    ax1.imshow(main_img)
    tile_size = 512
    
    # Draw selected tile boundaries
    for i, tile_idx in enumerate(selected_indices):
        row = tile_idx // 8
        col = tile_idx % 8
        x, y = col * tile_size, row * tile_size
        
        # Get attention value
        attention_val = attention_flat[i] if i < len(attention_flat) else 0
        
        # Create color gradient based on attention
        alpha = min(0.3 + attention_val * 0.7, 1.0)
        linewidth = 2 + attention_val * 3
        
        rect = patches.Rectangle((x, y), tile_size, tile_size, 
                                linewidth=linewidth, edgecolor='red',
                                facecolor='red', alpha=alpha*0.3, fill=True)
        ax1.add_patch(rect)
        
        rect_border = patches.Rectangle((x, y), tile_size, tile_size, 
                                       linewidth=linewidth, edgecolor='red',
                                       fill=False)
        ax1.add_patch(rect_border)
    
    ax1.set_xlim(0, 4096)
    ax1.set_ylim(4096, 0)
    ax1.axis('off')
    ax1.set_title('Selected Tiles', fontsize=16, fontweight='bold', pad=20)
    
    # Panel 2: Attention heatmap
    ax2 = plt.subplot(132)
    
    # Create custom colormap
    colors = ['#FFFFFF', '#FFE5E5', '#FFCCCC', '#FF9999', '#FF6666', '#FF3333', '#FF0000', '#CC0000']
    n_bins = 100
    cmap = LinearSegmentedColormap.from_list('attention', colors, N=n_bins)
    
    # Upsample heatmap for smoother visualization
    from scipy.ndimage import zoom
    upsampled_heatmap = zoom(full_heatmap, 64, order=3)  # Cubic interpolation
    
    im = ax2.imshow(upsampled_heatmap, cmap=cmap, vmin=0, vmax=np.max(attention_flat)*1.1,
                    interpolation='bilinear')
    
    # Add subtle grid
    for i in range(9):
        ax2.axhline(i*64, color='gray', linewidth=0.5, alpha=0.3)
        ax2.axvline(i*64, color='gray', linewidth=0.5, alpha=0.3)
    
    ax2.set_xlim(0, 512)
    ax2.set_ylim(512, 0)
    ax2.axis('off')
    ax2.set_title('Attention Map', fontsize=16, fontweight='bold', pad=20)
    
    # Add colorbar
    cbar = plt.colorbar(im, ax=ax2, fraction=0.046, pad=0.04)
    cbar.ax.tick_params(labelsize=12)
    
    # Panel 3: Overlay
    ax3 = plt.subplot(133)
    ax3.imshow(main_img)
    
    # Create smooth overlay
    overlay_heatmap = zoom(full_heatmap, 512, order=3)
    
    # Apply Gaussian smoothing for publication quality
    from scipy.ndimage import gaussian_filter
    overlay_heatmap = gaussian_filter(overlay_heatmap, sigma=20)
    
    # Normalize for better visibility
    if np.max(overlay_heatmap) > 0:
        overlay_heatmap = overlay_heatmap / np.max(overlay_heatmap)
    
    im3 = ax3.imshow(overlay_heatmap, cmap=cmap, alpha=0.5, 
                     vmin=0, vmax=1, interpolation='bilinear')
    
    ax3.set_xlim(0, 4096)
    ax3.set_ylim(4096, 0)
    ax3.axis('off')
    ax3.set_title('Attention Overlay', fontsize=16, fontweight='bold', pad=20)
    
    # Adjust layout
    plt.tight_layout()
    
    # Save if path provided
    if save_path:
        plt.savefig(save_path, dpi=dpi, bbox_inches='tight', 
                   facecolor='white', edgecolor='none')
        print(f"Figure saved to {save_path}")
    
    plt.show()
    
    return full_heatmap

# Generate predictions with attention
def predict_with_attention(model, dataloader, tile_selections_metadata, temperature=1.0):
    """Generate predictions along with attention weights"""
    model.eval()
    device = next(model.parameters()).device
    
    results = []
    
    with torch.no_grad():
        for features, labels, image_ids in tqdm(dataloader, desc="Generating predictions"):
            features = features.to(device)
            
            # Forward pass with attention
            logits, global_attention, transformer_attention = model(features, return_attention=True)
            
            # Apply temperature scaling
            scaled_logits = logits / temperature
            probs = F.softmax(scaled_logits, dim=1)
            
            # Process each sample
            for i in range(features.size(0)):
                image_id = image_ids[i]
                true_label = labels[i].item() if labels[i] != -1 else None
                
                # Get probabilities
                ce_prob = probs[i, 0].item()
                laa_prob = probs[i, 1].item()
                prediction_probs = [ce_prob, laa_prob]
                
                # Get attention weights
                attention_weights = global_attention[i].cpu().numpy().flatten()
                
                results.append({
                    'image_id': image_id,
                    'true_label': true_label,
                    'prediction_probs': prediction_probs,
                    'attention_weights': attention_weights,
                    'predicted_label': 1 if laa_prob > ce_prob else 0
                })
    
    return results

# Main function for generating publication figures
def generate_publication_figures(model_path, data_csv_path, config, num_samples=10, save_dir=None):
    """
    Generate publication-quality attention figures
    
    Args:
        model_path: Path to saved model
        data_csv_path: Path to CSV data
        config: Configuration object
        num_samples: Number of samples to visualize
        save_dir: Directory to save figures
    """
    
    # Create save directory if specified
    if save_dir:
        os.makedirs(save_dir, exist_ok=True)
    
    # Load data
    df = pd.read_csv(data_csv_path)
    
    # Ensure consistent label format
    if 'label' in df.columns and df['label'].dtype == 'object':
        label_map = {'CE': 0, 'LAA': 1}
        df['label'] = df['label'].map(label_map)
    
    print(f"Loaded {len(df)} samples")
    
    # Sample data
    if len(df) > num_samples:
        sample_df = df.sample(n=num_samples, random_state=42).reset_index(drop=True)
    else:
        sample_df = df.copy()
    
    print(f"Generating figures for {len(sample_df)} samples")
    
    # Load model
    model, threshold, temperature, transformer, metrics = load_trained_model(model_path, config)
    
    # Load tile selection metadata
    metadata_path = f"{config.FEATURES_DIR}/tile_selections_metadata.json"
    with open(metadata_path, 'r') as f:
        tile_selections_metadata = json.load(f)
    
    # Create dataset and dataloader
    dataset = OptimizedDataset(
        sample_df, 
        config.FEATURES_DIR,
        transformer=transformer,
        metadata_path=metadata_path
    )
    
    dataloader = DataLoader(dataset, batch_size=1, shuffle=False, num_workers=0)
    
    # Generate predictions
    print("\nGenerating predictions with attention...")
    results = predict_with_attention(model, dataloader, tile_selections_metadata, temperature)
    
    # Generate publication figures
    print(f"\nGenerating {len(results)} publication figures...")
    
    for i, result in enumerate(results):
        print(f"\nFigure {i+1}/{len(results)}: {result['image_id']}")
        
        # Determine save path
        if save_dir:
            save_path = os.path.join(save_dir, f"figure_{result['image_id']}.png")
        else:
            save_path = None
        
        # Generate figure
        heatmap = create_publication_figure(
            result['attention_weights'],
            result['image_id'],
            tile_selections_metadata,
            config.IMAGES_DIR,
            result['prediction_probs'],
            result['true_label'],
            save_path=save_path,
            dpi=300
        )
        
        # Print minimal statistics
        print(f"  Prediction: {'LAA' if result['predicted_label'] == 1 else 'CE'} "
              f"(confidence: {max(result['prediction_probs']):.2f})")
        if result['true_label'] is not None:
            print(f"  True label: {'LAA' if result['true_label'] == 1 else 'CE'}")
    
    print(f"\n✓ Completed {len(results)} figures")
    if save_dir:
        print(f"✓ Figures saved to {save_dir}")
    
    return results

# Main execution
def main():
    seed_everything(42)
    
    # Configuration
    config = OptimizedConfig()
    
    # Paths
    model_path = f"{config.SAVE_DIR}/best_model_auto_selected_fold_0.pth"
    data_csv_path = "../input/mayo-clinic-strip-ai/train.csv"
    save_dir = "./publication_figures"  # Directory to save figures
    
    # Validate paths
    if not os.path.exists(model_path):
        print(f"Error: Model not found at {model_path}")
        return
    
    if not os.path.exists(data_csv_path):
        print(f"Error: Data CSV not found at {data_csv_path}")
        return
    
    if not os.path.exists(config.FEATURES_DIR):
        print(f"Error: Features directory not found at {config.FEATURES_DIR}")
        return
    
    if not os.path.exists(config.IMAGES_DIR):
        print(f"Error: Images directory not found at {config.IMAGES_DIR}")
        return
    
    # Generate publication figures
    print("="*60)
    print("PUBLICATION FIGURE GENERATION")
    print("="*60)
    
    results = generate_publication_figures(
        model_path=model_path,
        data_csv_path=data_csv_path,
        config=config,
        num_samples=5,  # Number of figures to generate
        save_dir=save_dir  # Set to None to not save
    )
    
    print("="*60)
    print("COMPLETED")
    print("="*60)
    
    return results

if __name__ == "__main__":
    results = main()