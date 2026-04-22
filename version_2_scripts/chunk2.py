def create_base_patient_cohort():
    """Create the foundational 3-patient cohort with comprehensive profiles"""
    
    base_patients = []
    
    # Patient 1: High-risk breast cancer, poor drug response
    patient_1 = {
        'patient_id': 'BASE_001',
        'cancer_type': 'BRCA',
        'age': 67,
        'gender': 'F',
        'stage': 'III',
        'drug_response': 0,
        'survival_months': 8.5,
        'vital_status': 'Dead',
        'medical_history': 'diabetes,hypertension',
        'family_history': 'breast_cancer,ovarian_cancer',
        'lifestyle_smoking': 'former',
        'lifestyle_alcohol': 'moderate',
        'bmi': 28.3,
        'kps_score': 70,
        'previous_treatments': 'chemotherapy,radiation',
        'biomarker_her2': 'positive',
        'biomarker_er': 'negative',
        'biomarker_pr': 'negative'
    }
    
    # Patient 2: Moderate-risk lung adenocarcinoma, good drug response  
    patient_2 = {
        'patient_id': 'BASE_002',
        'cancer_type': 'LUAD',
        'age': 58,
        'gender': 'M',
        'stage': 'II',
        'drug_response': 1,
        'survival_months': 34.2,
        'vital_status': 'Alive',
        'medical_history': 'copd,heart_disease',
        'family_history': 'lung_cancer',
        'lifestyle_smoking': 'current',
        'lifestyle_alcohol': 'light',
        'bmi': 24.1,
        'kps_score': 85,
        'previous_treatments': 'surgery',
        'biomarker_egfr': 'mutation_positive',
        'biomarker_kras': 'wild_type',
        'biomarker_alk': 'negative'
    }
    
    # Patient 3: Low-risk colorectal cancer, excellent drug response
    patient_3 = {
        'patient_id': 'BASE_003', 
        'cancer_type': 'COAD',
        'age': 52,
        'gender': 'F',
        'stage': 'I',
        'drug_response': 1,
        'survival_months': 48.7,
        'vital_status': 'Alive',
        'medical_history': 'none',
        'family_history': 'colorectal_cancer',
        'lifestyle_smoking': 'never',
        'lifestyle_alcohol': 'none',
        'bmi': 22.8,
        'kps_score': 95,
        'previous_treatments': 'surgery_only',
        'biomarker_msi': 'stable',
        'biomarker_kras': 'wild_type',
        'biomarker_braf': 'wild_type'
    }
    
    # Generate realistic gene expression profiles for each patient
    np.random.seed(42)  # For reproducibility
    
    for i, patient in enumerate([patient_1, patient_2, patient_3]):
        # Create gene expression profile based on cancer type and response
        base_expression = np.random.lognormal(mean=4, sigma=1.5, size=100)
        
        # Modify expression based on drug response
        if patient['drug_response'] == 1:  # Good responders
            # Upregulate tumor suppressor genes (genes 1-20)
            base_expression[:20] *= np.random.uniform(1.2, 2.0, 20)
            # Downregulate oncogenes (genes 21-40)  
            base_expression[20:40] *= np.random.uniform(0.3, 0.8, 20)
        else:  # Poor responders
            # Opposite pattern
            base_expression[:20] *= np.random.uniform(0.4, 0.9, 20)
            base_expression[20:40] *= np.random.uniform(1.1, 1.8, 20)
        
        # Add cancer-type specific signatures
        if patient['cancer_type'] == 'BRCA':
            base_expression[40:50] *= np.random.uniform(1.5, 2.5, 10)  # Hormone receptors
        elif patient['cancer_type'] == 'LUAD':
            base_expression[50:60] *= np.random.uniform(1.3, 2.2, 10)  # Growth factors
        elif patient['cancer_type'] == 'COAD':
            base_expression[60:70] *= np.random.uniform(1.4, 2.1, 10)  # Wnt pathway
        
        # Add gene expression data to patient
        for j in range(100):
            patient[f'gene_{j+1}'] = base_expression[j]
        
        base_patients.append(patient)
    
    return pd.DataFrame(base_patients)

def create_tcga_like_expansion(base_df, target_patients_per_type=200):
    """Create TCGA-like expanded dataset maintaining realistic distributions"""
    
    cancer_types = ['BRCA', 'LUAD', 'COAD', 'PRAD', 'STAD', 'THCA', 'KIRC', 'LIHC', 'UCEC', 'HNSC']
    expanded_patients = []
    
    for cancer_type in cancer_types:
        print(f"Generating {target_patients_per_type} {cancer_type} patients...")
        
        # Use base patient of same type as template if available
        base_template = base_df[base_df['cancer_type'] == cancer_type]
        if base_template.empty:
            # Use random base patient as template
            base_template = base_df.sample(1)
        
        template = base_template.iloc[0]
        
        for i in range(target_patients_per_type):
            new_patient = template.to_dict().copy()
            
            # Modify patient characteristics
            new_patient['patient_id'] = f'TCGA_{cancer_type}_{i+1:03d}'
            new_patient['cancer_type'] = cancer_type
            new_patient['age'] = max(18, np.random.normal(65, 12))
            new_patient['gender'] = np.random.choice(['M', 'F'], p=[0.45, 0.55])
            new_patient['stage'] = np.random.choice(['I', 'II', 'III', 'IV'], p=[0.25, 0.35, 0.25, 0.15])
            
            # Drug response based on realistic clinical outcomes
            stage_response_prob = {'I': 0.85, 'II': 0.75, 'III': 0.60, 'IV': 0.40}
            response_prob = stage_response_prob[new_patient['stage']]
            new_patient['drug_response'] = np.random.binomial(1, response_prob)
            
            # Survival based on response and stage
            if new_patient['drug_response'] == 1:
                base_survival = {'I': 48, 'II': 36, 'III': 24, 'IV': 12}[new_patient['stage']]
                new_patient['survival_months'] = np.random.exponential(base_survival)
            else:
                base_survival = {'I': 24, 'II': 18, 'III': 12, 'IV': 6}[new_patient['stage']]
                new_patient['survival_months'] = np.random.exponential(base_survival)
            
            new_patient['vital_status'] = np.random.choice(['Alive', 'Dead'], 
                                                         p=[0.65, 0.35] if new_patient['drug_response'] else [0.35, 0.65])
            
            # Generate gene expression with cancer-type specific patterns
            base_expression = np.random.lognormal(mean=4.5, sigma=1.2, size=100)
            
            # Apply response-specific modifications
            if new_patient['drug_response'] == 1:
                # Good responder pattern
                base_expression[:25] *= np.random.uniform(1.1, 1.8, 25)  # Tumor suppressors
                base_expression[25:50] *= np.random.uniform(0.5, 0.9, 25)  # Oncogenes
            else:
                # Poor responder pattern  
                base_expression[:25] *= np.random.uniform(0.6, 1.0, 25)
                base_expression[25:50] *= np.random.uniform(1.0, 1.6, 25)
            
            # Cancer-type specific gene signatures
            type_signatures = {
                'BRCA': (70, 80), 'LUAD': (80, 90), 'COAD': (50, 60),
                'PRAD': (60, 70), 'STAD': (40, 50), 'THCA': (30, 40),
                'KIRC': (20, 30), 'LIHC': (10, 20), 'UCEC': (75, 85), 'HNSC': (85, 95)
            }
            
            start_idx, end_idx = type_signatures[cancer_type]
            base_expression[start_idx:end_idx] *= np.random.uniform(1.3, 2.2, end_idx - start_idx)
            
            # Add expression data
            for j in range(100):
                new_patient[f'gene_{j+1}'] = base_expression[j]
            
            expanded_patients.append(new_patient)
    
    return pd.DataFrame(expanded_patients)

# Execute data creation
print("Creating base patient cohort...")
base_cohort = create_base_patient_cohort()

print("\nBase Cohort Summary:")
print(f"Total patients: {len(base_cohort)}")
print(f"Cancer types: {base_cohort['cancer_type'].value_counts().to_dict()}")
print(f"Drug response rate: {base_cohort['drug_response'].mean():.2%}")

# Display base cohort characteristics
fig, axes = plt.subplots(2, 2, figsize=(15, 10))

# Age distribution
axes[0,0].bar(range(len(base_cohort)), base_cohort['age'], color=['#FF6B6B', '#4ECDC4', '#45B7D1'])
axes[0,0].set_title('Age Distribution - Base Cohort', fontsize=14, fontweight='bold')
axes[0,0].set_xlabel('Patient')
axes[0,0].set_ylabel('Age (years)')
axes[0,0].set_xticks(range(len(base_cohort)))
axes[0,0].set_xticklabels(base_cohort['patient_id'], rotation=45)

# Cancer stage distribution
stage_counts = base_cohort['stage'].value_counts()
axes[0,1].pie(stage_counts.values, labels=stage_counts.index, autopct='%1.0f%%', 
              colors=['#FF9F43', '#10AC84', '#EE5A24', '#0984e3'])
axes[0,1].set_title('Cancer Stage Distribution', fontsize=14, fontweight='bold')

# Drug response
response_counts = base_cohort['drug_response'].value_counts()
response_labels = ['Non-Responder', 'Responder']
axes[1,0].bar(response_labels, [response_counts[0], response_counts[1]], 
              color=['#E74C3C', '#27AE60'])
axes[1,0].set_title('Drug Response Distribution', fontsize=14, fontweight='bold')
axes[1,0].set_ylabel('Number of Patients')

# Survival months
axes[1,1].bar(range(len(base_cohort)), base_cohort['survival_months'], 
              color=['#E74C3C' if x == 0 else '#27AE60' for x in base_cohort['drug_response']])
axes[1,1].set_title('Survival by Drug Response', fontsize=14, fontweight='bold')
axes[1,1].set_xlabel('Patient')
axes[1,1].set_ylabel('Survival (months)')
axes[1,1].set_xticks(range(len(base_cohort)))
axes[1,1].set_xticklabels(base_cohort['patient_id'], rotation=45)

plt.tight_layout()
plt.show()

# Create expanded TCGA-like dataset
print("\nCreating TCGA-like expanded dataset...")
tcga_expanded = create_tcga_like_expansion(base_cohort, target_patients_per_type=100)

print(f"\nTCGA Expanded Dataset Summary:")
print(f"Total patients: {len(tcga_expanded)}")
print(f"Cancer types: {len(tcga_expanded['cancer_type'].unique())}")
print(f"Overall response rate: {tcga_expanded['drug_response'].mean():.2%}")

# Visualize expanded dataset
fig, axes = plt.subplots(2, 2, figsize=(16, 12))

# Cancer type distribution
cancer_counts = tcga_expanded['cancer_type'].value_counts()
axes[0,0].barh(cancer_counts.index, cancer_counts.values, color='skyblue')
axes[0,0].set_title('Patient Distribution by Cancer Type', fontsize=14, fontweight='bold')
axes[0,0].set_xlabel('Number of Patients')

# Age distribution by cancer type
tcga_expanded.boxplot(column='age', by='cancer_type', ax=axes[0,1], rot=45)
axes[0,1].set_title('Age Distribution by Cancer Type', fontsize=14, fontweight='bold')
axes[0,1].set_xlabel('Cancer Type')
axes[0,1].set_ylabel('Age (years)')

# Response rate by cancer type
response_by_type = tcga_expanded.groupby('cancer_type')['drug_response'].mean().sort_values(ascending=False)
axes[1,0].bar(response_by_type.index, response_by_type.values, color='lightcoral')
axes[1,0].set_title('Drug Response Rate by Cancer Type', fontsize=14, fontweight='bold')
axes[1,0].set_xlabel('Cancer Type')
axes[1,0].set_ylabel('Response Rate')
axes[1,0].tick_params(axis='x', rotation=45)

# Survival distribution
survival_responders = tcga_expanded[tcga_expanded['drug_response']==1]['survival_months']
survival_non_responders = tcga_expanded[tcga_expanded['drug_response']==0]['survival_months']

axes[1,1].hist([survival_responders, survival_non_responders], bins=30, alpha=0.7, 
               label=['Responders', 'Non-Responders'], color=['green', 'red'])
axes[1,1].set_title('Survival Distribution by Drug Response', fontsize=14, fontweight='bold')
axes[1,1].set_xlabel('Survival (months)')
axes[1,1].set_ylabel('Frequency')
axes[1,1].legend()

plt.tight_layout()
plt.show()

print("Base cohort and TCGA expansion completed successfully")
