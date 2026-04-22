import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
from pathlib import Path
import pickle
from datetime import datetime
import json

from sklearn.model_selection import StratifiedKFold, cross_val_score, train_test_split
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.neural_network import MLPClassifier
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import (accuracy_score, precision_score, recall_score, f1_score,
                           roc_auc_score, classification_report, confusion_matrix,
                           roc_curve, precision_recall_curve)
from sklearn.pipeline import Pipeline

from scipy.stats import chi2_contingency, fisher_exact, ttest_ind, mannwhitneyu
from scipy.stats import pearsonr, spearmanr, multivariate_normal
import scipy.stats as stats

warnings.filterwarnings('ignore')

# Set matplotlib style (compatible with different versions)
try:
    plt.style.use('seaborn-v0_8')
except OSError:
    try:
        plt.style.use('seaborn')
    except OSError:
        plt.style.use('default')
        
sns.set_palette("husl")
plt.rcParams['figure.figsize'] = (10, 6)
plt.rcParams['font.size'] = 10

print("Environment initialized successfully")
print(f"Analysis started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

class DataAugmentationEngine:
    def __init__(self, base_patients=3, target_size=1000):
        self.base_patients = base_patients
        self.target_size = target_size
        self.augmentation_methods = {
            'gaussian_noise': self._add_gaussian_noise,
            'gene_expression_variation': self._vary_gene_expression,
            'synthetic_similarity': self._generate_similar_patients,
            'bootstrap_sampling': self._bootstrap_resample
        }
    
    def _add_gaussian_noise(self, patient_data, n_variants=50):
        variants = []
        gene_cols = [col for col in patient_data.columns if col.startswith('gene_')]
        
        for i in range(n_variants):
            variant = patient_data.copy()
            noise_scale = np.random.uniform(0.05, 0.15)
            
            for gene_col in gene_cols:
                original_value = variant[gene_col].iloc[0]
                noise = np.random.normal(0, original_value * noise_scale)
                variant[gene_col] = max(0.01, original_value + noise)
            
            variant['patient_id'] = f"{patient_data['patient_id'].iloc[0]}_noise_{i+1}"
            variant['augmentation_method'] = 'gaussian_noise'
            variants.append(variant)
        
        return pd.concat(variants, ignore_index=True)
    
    def _vary_gene_expression(self, patient_data, n_variants=50):
        variants = []
        gene_cols = [col for col in patient_data.columns if col.startswith('gene_')]
        
        for i in range(n_variants):
            variant = patient_data.copy()
            
            n_genes_to_modify = np.random.randint(5, 15)
            genes_to_modify = np.random.choice(gene_cols, n_genes_to_modify, replace=False)
            
            for gene_col in genes_to_modify:
                original_value = variant[gene_col].iloc[0]
                modification_factor = np.random.uniform(0.7, 1.3)
                variant[gene_col] = original_value * modification_factor
            
            variant['patient_id'] = f"{patient_data['patient_id'].iloc[0]}_genevar_{i+1}"
            variant['augmentation_method'] = 'gene_expression_variation'
            variants.append(variant)
        
        return pd.concat(variants, ignore_index=True)
    
    def _generate_similar_patients(self, patient_data, n_variants=50):
        variants = []
        gene_cols = [col for col in patient_data.columns if col.startswith('gene_')]
        
        gene_values = patient_data[gene_cols].values[0]
        cov_matrix = np.diag(gene_values * 0.1) ** 2
        
        for i in range(n_variants):
            similar_genes = multivariate_normal.rvs(mean=gene_values, cov=cov_matrix)
            similar_genes = np.maximum(similar_genes, 0.01)
            
            variant = patient_data.copy()
            for j, gene_col in enumerate(gene_cols):
                variant[gene_col] = similar_genes[j]
            
            age_variation = np.random.normal(0, 5)
            variant['age'] = max(18, patient_data['age'].iloc[0] + age_variation)
            
            variant['patient_id'] = f"{patient_data['patient_id'].iloc[0]}_similar_{i+1}"
            variant['augmentation_method'] = 'synthetic_similarity'
            variants.append(variant)
        
        return pd.concat(variants, ignore_index=True)
    
    def _bootstrap_resample(self, all_patients, n_variants=100):
        variants = []
        gene_cols = [col for col in all_patients.columns if col.startswith('gene_')]
        
        for i in range(n_variants):
            sampled_patients = all_patients.sample(n=min(3, len(all_patients)), replace=True)
            
            new_patient = sampled_patients.iloc[0].copy()
            
            for gene_col in gene_cols:
                gene_values = sampled_patients[gene_col].values
                new_patient[gene_col] = np.mean(gene_values) + np.random.normal(0, np.std(gene_values) * 0.2)
            
            new_patient['age'] = np.mean(sampled_patients['age']) + np.random.normal(0, 3)
            new_patient['patient_id'] = f"bootstrap_patient_{i+1}"
            new_patient['augmentation_method'] = 'bootstrap_sampling'
            variants.append(new_patient)
        
        return pd.DataFrame(variants)
    
    def augment_dataset(self, original_data):
        print(f"Starting data augmentation from {len(original_data)} patients to {self.target_size}")
        
        augmented_datasets = []
        patients_per_method = (self.target_size - len(original_data)) // len(self.augmentation_methods)
        
        for method_name, method_func in self.augmentation_methods.items():
            print(f"Applying {method_name} augmentation...")
            
            if method_name == 'bootstrap_sampling':
                augmented = method_func(original_data, patients_per_method)
            else:
                method_augmented = []
                variants_per_patient = patients_per_method // len(original_data)
                
                for idx, patient_row in original_data.iterrows():
                    patient_df = pd.DataFrame([patient_row])
                    variants = method_func(patient_df, variants_per_patient)
                    method_augmented.append(variants)
                
                augmented = pd.concat(method_augmented, ignore_index=True)
            
            augmented_datasets.append(augmented)
        
        final_dataset = pd.concat([original_data] + augmented_datasets, ignore_index=True)
        final_dataset = final_dataset.reset_index(drop=True)
        
        print(f"Data augmentation completed: {len(final_dataset)} total patients")
        return final_dataset

augmentation_engine = DataAugmentationEngine()
print("Data augmentation framework initialized")
