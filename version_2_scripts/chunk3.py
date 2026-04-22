# Apply comprehensive data augmentation
print("Applying data augmentation to base cohort...")
augmented_base = augmentation_engine.augment_dataset(base_cohort)

# Combine with TCGA-like expansion for final dataset
print("Integrating augmented base cohort with TCGA expansion...")
final_dataset = pd.concat([augmented_base, tcga_expanded], ignore_index=True)
final_dataset = final_dataset.drop_duplicates(subset=['patient_id'], keep='first')

print(f"\nFinal Integrated Dataset Summary:")
print(f"Total patients: {len(final_dataset)}")
print(f"Cancer types: {len(final_dataset['cancer_type'].unique())}")
print(f"Gene features: {len([col for col in final_dataset.columns if col.startswith('gene_')])}")
print(f"Overall response rate: {final_dataset['drug_response'].mean():.2%}")

# Data quality assessment
def assess_data_quality(df):
    """Comprehensive data quality assessment"""
    
    quality_metrics = {}
    
    # Missing data analysis
    missing_data = df.isnull().sum()
    quality_metrics['missing_data_percentage'] = (missing_data.sum() / (len(df) * len(df.columns))) * 100
    
    # Class balance
    response_rate = df['drug_response'].mean()
    quality_metrics['class_balance'] = min(response_rate, 1-response_rate)
    
    # Cancer type distribution
    cancer_counts = df['cancer_type'].value_counts()
    quality_metrics['min_samples_per_type'] = cancer_counts.min()
    quality_metrics['max_samples_per_type'] = cancer_counts.max()
    quality_metrics['type_distribution_cv'] = cancer_counts.std() / cancer_counts.mean()
    
    # Gene expression quality
    gene_cols = [col for col in df.columns if col.startswith('gene_')]
    gene_data = df[gene_cols]
    quality_metrics['gene_expression_range'] = gene_data.max().max() - gene_data.min().min()
    quality_metrics['avg_gene_cv'] = (gene_data.std() / gene_data.mean()).mean()
    
    return quality_metrics

quality_assessment = assess_data_quality(final_dataset)

print("\nData Quality Assessment:")
for metric, value in quality_assessment.items():
    if isinstance(value, float):
        print(f"  {metric}: {value:.3f}")
    else:
        print(f"  {metric}: {value}")

# Visualize augmentation impact
fig, axes = plt.subplots(2, 3, figsize=(18, 12))

# Dataset size comparison
datasets = ['Base Cohort', 'Augmented Base', 'TCGA Expansion', 'Final Integrated']
sizes = [len(base_cohort), len(augmented_base), len(tcga_expanded), len(final_dataset)]
colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4']

axes[0,0].bar(datasets, sizes, color=colors)
axes[0,0].set_title('Dataset Size Progression', fontsize=14, fontweight='bold')
axes[0,0].set_ylabel('Number of Patients')
axes[0,0].tick_params(axis='x', rotation=45)

# Augmentation method distribution (for augmented patients only)
if 'augmentation_method' in augmented_base.columns:
    aug_methods = augmented_base['augmentation_method'].value_counts()
    axes[0,1].pie(aug_methods.values, labels=aug_methods.index, autopct='%1.1f%%')
    axes[0,1].set_title('Augmentation Methods Distribution', fontsize=14, fontweight='bold')

# Cancer type coverage
type_coverage_base = base_cohort['cancer_type'].nunique()
type_coverage_final = final_dataset['cancer_type'].nunique()

axes[0,2].bar(['Base Cohort', 'Final Dataset'], [type_coverage_base, type_coverage_final], 
              color=['#FF6B6B', '#96CEB4'])
axes[0,2].set_title('Cancer Type Coverage', fontsize=14, fontweight='bold')
axes[0,2].set_ylabel('Number of Cancer Types')

# Gene expression distribution comparison
gene_cols = [col for col in final_dataset.columns if col.startswith('gene_')][:10]  # First 10 genes
base_genes = base_cohort[gene_cols].mean()
final_genes = final_dataset[gene_cols].mean()

x_pos = np.arange(len(gene_cols))
width = 0.35

axes[1,0].bar(x_pos - width/2, base_genes, width, label='Base Cohort', color='#FF6B6B', alpha=0.7)
axes[1,0].bar(x_pos + width/2, final_genes, width, label='Final Dataset', color='#96CEB4', alpha=0.7)
axes[1,0].set_title('Gene Expression Comparison', fontsize=14, fontweight='bold')
axes[1,0].set_xlabel('Gene Features')
axes[1,0].set_ylabel('Mean Expression')
axes[1,0].set_xticks(x_pos)
axes[1,0].set_xticklabels([f'G{i+1}' for i in range(len(gene_cols))], rotation=45)
axes[1,0].legend()

# Response rate by dataset source
response_rates = []
dataset_labels = []

if 'augmentation_method' in final_dataset.columns:
    # Base patients
    base_response = base_cohort['drug_response'].mean()
    response_rates.append(base_response)
    dataset_labels.append('Base Cohort')
    
    # Augmented patients
    aug_patients = final_dataset[final_dataset['augmentation_method'].notna()]
    if len(aug_patients) > 0:
        aug_response = aug_patients['drug_response'].mean()
        response_rates.append(aug_response)
        dataset_labels.append('Augmented')
    
    # TCGA patients  
    tcga_patients = final_dataset[final_dataset['patient_id'].str.contains('TCGA_')]
    tcga_response = tcga_patients['drug_response'].mean()
    response_rates.append(tcga_response)
    dataset_labels.append('TCGA-like')

axes[1,1].bar(dataset_labels, response_rates, color=['#FF6B6B', '#4ECDC4', '#45B7D1'])
axes[1,1].set_title('Response Rate by Data Source', fontsize=14, fontweight='bold')
axes[1,1].set_ylabel('Drug Response Rate')
axes[1,1].tick_params(axis='x', rotation=45)

# Age distribution comparison
axes[1,2].hist([base_cohort['age'], final_dataset['age']], bins=20, alpha=0.7, 
               color=['#FF6B6B', '#96CEB4'], label=['Base Cohort', 'Final Dataset'])
axes[1,2].set_title('Age Distribution Comparison', fontsize=14, fontweight='bold')
axes[1,2].set_xlabel('Age (years)')
axes[1,2].set_ylabel('Frequency')
axes[1,2].legend()

plt.tight_layout()
plt.show()

# Data integration validation
print("\nValidating data integration...")

# Check for data consistency
gene_cols = [col for col in final_dataset.columns if col.startswith('gene_')]
consistency_check = {
    'negative_expressions': (final_dataset[gene_cols] < 0).sum().sum(),
    'extreme_expressions': (final_dataset[gene_cols] > 100).sum().sum(),
    'missing_responses': final_dataset['drug_response'].isnull().sum(),
    'invalid_ages': ((final_dataset['age'] < 0) | (final_dataset['age'] > 120)).sum()
}

print("Data Consistency Check:")
for check, count in consistency_check.items():
    status = "PASS" if count == 0 else f"FAIL ({count} issues)"
    print(f"  {check}: {status}")

# Save processed datasets
print("\nSaving processed datasets...")
base_cohort.to_csv('base_cohort.csv', index=False)
tcga_expanded.to_csv('tcga_expanded.csv', index=False)
final_dataset.to_csv('final_integrated_dataset.csv', index=False)

print("Data augmentation and integration completed successfully")
print(f"Final dataset ready for validation: {len(final_dataset)} patients")
