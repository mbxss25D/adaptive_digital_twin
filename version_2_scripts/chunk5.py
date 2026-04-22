class ComprehensiveCrossValidation:
    def __init__(self, n_folds=5, random_state=42):
        self.n_folds = n_folds
        self.random_state = random_state
        self.cv_results = {}
        self.detailed_results = {}
        
    def calculate_metrics(self, y_true, y_pred, y_proba):
        """Calculate comprehensive evaluation metrics"""
        metrics = {
            'accuracy': accuracy_score(y_true, y_pred),
            'precision': precision_score(y_true, y_pred, average='weighted', zero_division=0),
            'recall': recall_score(y_true, y_pred, average='weighted', zero_division=0),
            'f1_score': f1_score(y_true, y_pred, average='weighted', zero_division=0),
            'specificity': precision_score(y_true, y_pred, pos_label=0, average='binary', zero_division=0),
            'sensitivity': recall_score(y_true, y_pred, pos_label=1, average='binary', zero_division=0)
        }
        
        if y_proba is not None and len(np.unique(y_true)) == 2:
            metrics['auc_roc'] = roc_auc_score(y_true, y_proba[:, 1])
        else:
            metrics['auc_roc'] = 0.0
            
        return metrics
    
    def stratified_cv_by_cancer_type(self, data, target_col='drug_response'):
        """Perform stratified cross-validation across cancer types"""
        print(f"Performing {self.n_folds}-fold cross-validation by cancer type...")
        
        cancer_types = data['cancer_type'].unique()
        all_results = {}
        
        for cancer_type in cancer_types:
            print(f"\n  Analyzing {cancer_type}...")
            
            # Filter data for this cancer type
            cancer_data = data[data['cancer_type'] == cancer_type].copy()
            
            if len(cancer_data) < 20:
                print(f"    Skipping {cancer_type}: insufficient samples ({len(cancer_data)})")
                continue
            
            # Prepare features and target
            X_cancer = cancer_data.drop(['drug_response', 'patient_id'], axis=1, errors='ignore')
            y_cancer = cancer_data[target_col]
            
            # Check class distribution
            if len(np.unique(y_cancer)) < 2:
                print(f"    Skipping {cancer_type}: insufficient class diversity")
                continue
            
            # Perform stratified k-fold CV
            n_folds_cancer = min(self.n_folds, len(cancer_data) // 10)
            if n_folds_cancer < 2:
                n_folds_cancer = 2
                
            skf = StratifiedKFold(n_splits=n_folds_cancer, shuffle=True, random_state=self.random_state)
            
            cancer_results = self._evaluate_models_cv(X_cancer, y_cancer, skf, cancer_type)
            all_results[cancer_type] = cancer_results
        
        self.cv_results = all_results
        return all_results
    
    def _evaluate_models_cv(self, X, y, cv_splitter, cancer_type):
        """Evaluate all models using cross-validation"""
        
        fold_results = []
        
        for fold, (train_idx, val_idx) in enumerate(cv_splitter.split(X, y)):
            print(f"    Fold {fold + 1}/{cv_splitter.n_splits}")
            
            X_train_fold = X.iloc[train_idx]
            X_val_fold = X.iloc[val_idx]
            y_train_fold = y.iloc[train_idx]
            y_val_fold = y.iloc[val_idx]
            
            fold_metrics = {}
            
            # Digital Twin evaluation
            try:
                dt_model = AdaptiveDigitalTwin()
                dt_model.fit(X_train_fold, y_train_fold)
                
                dt_pred = dt_model.predict(X_val_fold)
                dt_proba = dt_model.predict_proba(X_val_fold)
                dt_confidence = dt_model.get_confidence_scores(X_val_fold)
                
                dt_metrics = self.calculate_metrics(y_val_fold, dt_pred, dt_proba)
                dt_metrics['avg_confidence'] = np.mean(dt_confidence)
                dt_metrics['high_conf_coverage'] = np.mean(dt_confidence >= 0.7)
                
                fold_metrics['Digital_Twin'] = dt_metrics
                
            except Exception as e:
                print(f"      Digital Twin failed: {str(e)}")
                continue
            
            # Baseline models evaluation
            try:
                baseline_models = BaselineModelSuite()
                baseline_models.train_all_models(X_train_fold, y_train_fold)
                
                baseline_preds = baseline_models.predict_all(X_val_fold)
                baseline_probas = baseline_models.predict_proba_all(X_val_fold)
                
                for model_name in baseline_preds.keys():
                    if model_name in baseline_probas:
                        baseline_metrics = self.calculate_metrics(
                            y_val_fold, 
                            baseline_preds[model_name], 
                            baseline_probas[model_name]
                        )
                        fold_metrics[model_name] = baseline_metrics
                
            except Exception as e:
                print(f"      Baseline models failed: {str(e)}")
            
            fold_results.append(fold_metrics)
        
        # Aggregate results across folds
        return self._aggregate_fold_results(fold_results)
    
    def _aggregate_fold_results(self, fold_results):
        """Aggregate metrics across CV folds"""
        if not fold_results:
            return {}
        
        aggregated = {}
        all_models = set()
        for fold in fold_results:
            all_models.update(fold.keys())
        
        for model_name in all_models:
            model_metrics = {}
            metric_names = set()
            
            # Collect all metric names
            for fold in fold_results:
                if model_name in fold:
                    metric_names.update(fold[model_name].keys())
            
            # Aggregate each metric
            for metric_name in metric_names:
                values = []
                for fold in fold_results:
                    if model_name in fold and metric_name in fold[model_name]:
                        values.append(fold[model_name][metric_name])
                
                if values:
                    model_metrics[f'{metric_name}_mean'] = np.mean(values)
                    model_metrics[f'{metric_name}_std'] = np.std(values)
                    model_metrics[f'{metric_name}_values'] = values
            
            aggregated[model_name] = model_metrics
        
        return aggregated
    
    def generate_cv_summary(self):
        """Generate comprehensive CV summary"""
        if not self.cv_results:
            return "No cross-validation results available"
        
        summary = []
        
        for cancer_type, results in self.cv_results.items():
            for model_name, metrics in results.items():
                if 'accuracy_mean' in metrics:
                    summary.append({
                        'Cancer_Type': cancer_type,
                        'Model': model_name,
                        'Accuracy': f"{metrics['accuracy_mean']:.3f} ± {metrics['accuracy_std']:.3f}",
                        'AUC': f"{metrics['auc_roc_mean']:.3f} ± {metrics['auc_roc_std']:.3f}",
                        'F1_Score': f"{metrics['f1_score_mean']:.3f} ± {metrics['f1_score_std']:.3f}",
                        'Sensitivity': f"{metrics['sensitivity_mean']:.3f} ± {metrics['sensitivity_std']:.3f}",
                        'Specificity': f"{metrics['specificity_mean']:.3f} ± {metrics['specificity_std']:.3f}"
                    })
        
        return pd.DataFrame(summary)

# Execute cross-validation
print("Initializing comprehensive cross-validation framework...")
cv_framework = ComprehensiveCrossValidation(n_folds=5)

# Perform cross-validation by cancer type
cv_results = cv_framework.stratified_cv_by_cancer_type(final_dataset)

# Generate and display summary
cv_summary = cv_framework.generate_cv_summary()
print("\nCross-Validation Results Summary:")
print("=" * 80)

if not cv_summary.empty:
    # Display results by cancer type
    for cancer_type in cv_summary['Cancer_Type'].unique():
        print(f"\n{cancer_type} Results:")
        cancer_results = cv_summary[cv_summary['Cancer_Type'] == cancer_type]
        cancer_results_display = cancer_results.drop('Cancer_Type', axis=1)
        print(cancer_results_display.to_string(index=False))
    
    # Create comprehensive visualization
    fig, axes = plt.subplots(2, 3, figsize=(20, 12))
    
    # 1. Accuracy by cancer type and model
    accuracy_data = []
    for _, row in cv_summary.iterrows():
        acc_mean = float(row['Accuracy'].split(' ±')[0])
        accuracy_data.append({
            'Cancer_Type': row['Cancer_Type'],
            'Model': row['Model'],
            'Accuracy': acc_mean
        })
    
    acc_df = pd.DataFrame(accuracy_data)
    acc_pivot = acc_df.pivot(index='Cancer_Type', columns='Model', values='Accuracy')
    
    sns.heatmap(acc_pivot, annot=True, cmap='RdYlBu_r', fmt='.3f', ax=axes[0,0])
    axes[0,0].set_title('Accuracy Heatmap by Cancer Type', fontsize=14, fontweight='bold')
    axes[0,0].set_xlabel('Model')
    axes[0,0].set_ylabel('Cancer Type')
    
    # 2. AUC comparison
    auc_data = []
    for _, row in cv_summary.iterrows():
        auc_mean = float(row['AUC'].split(' ±')[0])
        auc_data.append({
            'Cancer_Type': row['Cancer_Type'],
            'Model': row['Model'],
            'AUC': auc_mean
        })
    
    auc_df = pd.DataFrame(auc_data)
    model_auc_means = auc_df.groupby('Model')['AUC'].mean().sort_values(ascending=False)
    
    colors = ['#FF6B6B' if model == 'Digital_Twin' else '#4ECDC4' for model in model_auc_means.index]
    bars = axes[0,1].bar(model_auc_means.index, model_auc_means.values, color=colors)
    axes[0,1].set_title('Average AUC by Model', fontsize=14, fontweight='bold')
    axes[0,1].set_xlabel('Model')
    axes[0,1].set_ylabel('Average AUC')
    axes[0,1].tick_params(axis='x', rotation=45)
    
    # Add value labels
    for bar, auc in zip(bars, model_auc_means.values):
        axes[0,1].text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01, 
                      f'{auc:.3f}', ha='center', va='bottom', fontweight='bold')
    
    # 3. F1-Score distribution
    f1_data = []
    for _, row in cv_summary.iterrows():
        f1_mean = float(row['F1_Score'].split(' ±')[0])
        f1_data.append({
            'Model': row['Model'],
            'F1_Score': f1_mean
        })
    
    f1_df = pd.DataFrame(f1_data)
    models_for_box = f1_df['Model'].unique()
    
    for i, model in enumerate(models_for_box):
        model_f1s = f1_df[f1_df['Model'] == model]['F1_Score']
        axes[0,2].scatter([i] * len(model_f1s), model_f1s, alpha=0.6, s=50)
    
    axes[0,2].set_xticks(range(len(models_for_box)))
    axes[0,2].set_xticklabels(models_for_box, rotation=45)
    axes[0,2].set_title('F1-Score Distribution', fontsize=14, fontweight='bold')
    axes[0,2].set_ylabel('F1-Score')
    
    # 4. Sensitivity vs Specificity
    sens_spec_data = []
    for _, row in cv_summary.iterrows():
        sens_mean = float(row['Sensitivity'].split(' ±')[0])
        spec_mean = float(row['Specificity'].split(' ±')[0])
        sens_spec_data.append({
            'Model': row['Model'],
            'Sensitivity': sens_mean,
            'Specificity': spec_mean
        })
    
    sens_spec_df = pd.DataFrame(sens_spec_data)
    
    for model in sens_spec_df['Model'].unique():
        model_data = sens_spec_df[sens_spec_df['Model'] == model]
        color = '#FF6B6B' if model == 'Digital_Twin' else '#4ECDC4'
        axes[1,0].scatter(model_data['Specificity'], model_data['Sensitivity'], 
                         label=model, alpha=0.7, s=60, color=color)
    
    axes[1,0].plot([0, 1], [0, 1], 'k--', alpha=0.5)
    axes[1,0].set_xlabel('Specificity')
    axes[1,0].set_ylabel('Sensitivity')
    axes[1,0].set_title('Sensitivity vs Specificity', fontsize=14, fontweight='bold')
    axes[1,0].legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    
    # 5. Performance variation across cancer types
    digital_twin_results = cv_summary[cv_summary['Model'] == 'Digital_Twin']
    if not digital_twin_results.empty:
        dt_acc = [float(acc.split(' ±')[0]) for acc in digital_twin_results['Accuracy']]
        dt_auc = [float(auc.split(' ±')[0]) for auc in digital_twin_results['AUC']]
        cancer_types_dt = digital_twin_results['Cancer_Type'].tolist()
        
        x_pos = np.arange(len(cancer_types_dt))
        width = 0.35
        
        bars1 = axes[1,1].bar(x_pos - width/2, dt_acc, width, label='Accuracy', color='lightblue', alpha=0.8)
        bars2 = axes[1,1].bar(x_pos + width/2, dt_auc, width, label='AUC', color='lightcoral', alpha=0.8)
        
        axes[1,1].set_xlabel('Cancer Type')
        axes[1,1].set_ylabel('Performance Score')
        axes[1,1].set_title('Digital Twin Performance by Cancer Type', fontsize=14, fontweight='bold')
        axes[1,1].set_xticks(x_pos)
        axes[1,1].set_xticklabels(cancer_types_dt, rotation=45)
        axes[1,1].legend()
        
        # Add value labels
        for bar, value in zip(bars1, dt_acc):
            axes[1,1].text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01, 
                          f'{value:.2f}', ha='center', va='bottom', fontsize=8)
        for bar, value in zip(bars2, dt_auc):
            axes[1,1].text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01, 
                          f'{value:.2f}', ha='center', va='bottom', fontsize=8)
    
    # 6. Model ranking analysis
    model_rankings = []
    for cancer_type in cv_summary['Cancer_Type'].unique():
        type_results = cv_summary[cv_summary['Cancer_Type'] == cancer_type]
        type_results_sorted = type_results.copy()
        type_results_sorted['Accuracy_Numeric'] = type_results_sorted['Accuracy'].apply(
            lambda x: float(x.split(' ±')[0]))
        type_results_sorted = type_results_sorted.sort_values('Accuracy_Numeric', ascending=False)
        
        for rank, (_, row) in enumerate(type_results_sorted.iterrows()):
            model_rankings.append({
                'Cancer_Type': cancer_type,
                'Model': row['Model'],
                'Rank': rank + 1,
                'Accuracy': row['Accuracy_Numeric']
            })
    
    ranking_df = pd.DataFrame(model_rankings)
    avg_rankings = ranking_df.groupby('Model')['Rank'].mean().sort_values()
    
    colors = ['#FF6B6B' if model == 'Digital_Twin' else '#4ECDC4' for model in avg_rankings.index]
    bars = axes[1,2].barh(avg_rankings.index, avg_rankings.values, color=colors)
    axes[1,2].set_xlabel('Average Rank (1=Best)')
    axes[1,2].set_title('Average Model Ranking Across Cancer Types', fontsize=14, fontweight='bold')
    axes[1,2].invert_yaxis()
    
    # Add value labels
    for bar, rank in zip(bars, avg_rankings.values):
        axes[1,2].text(bar.get_width() + 0.05, bar.get_y() + bar.get_height()/2, 
                      f'{rank:.1f}', ha='left', va='center', fontweight='bold')
    
    plt.tight_layout()
    plt.show()
    
    # Calculate overall performance metrics
    print("\nOVERALL PERFORMANCE SUMMARY:")
    print("=" * 50)
    
    # Digital Twin overall performance
    dt_results = cv_summary[cv_summary['Model'] == 'Digital_Twin']
    if not dt_results.empty:
        dt_accuracies = [float(acc.split(' ±')[0]) for acc in dt_results['Accuracy']]
        dt_aucs = [float(auc.split(' ±')[0]) for auc in dt_results['AUC']]
        
        print(f"Digital Twin Performance:")
        print(f"  Average Accuracy: {np.mean(dt_accuracies):.3f} ± {np.std(dt_accuracies):.3f}")
        print(f"  Average AUC: {np.mean(dt_aucs):.3f} ± {np.std(dt_aucs):.3f}")
        print(f"  Cancer Types Evaluated: {len(dt_results)}")
        print(f"  Best Cancer Type (Accuracy): {dt_results.iloc[np.argmax(dt_accuracies)]['Cancer_Type']} ({max(dt_accuracies):.3f})")
    
    # Best performing baseline
    baseline_results = cv_summary[cv_summary['Model'] != 'Digital_Twin']
    if not baseline_results.empty:
        baseline_accs = {}
        for model in baseline_results['Model'].unique():
            model_results = baseline_results[baseline_results['Model'] == model]
            model_accs = [float(acc.split(' ±')[0]) for acc in model_results['Accuracy']]
            baseline_accs[model] = np.mean(model_accs)
        
        best_baseline = max(baseline_accs.keys(), key=lambda k: baseline_accs[k])
        print(f"\nBest Baseline Model: {best_baseline}")
        print(f"  Average Accuracy: {baseline_accs[best_baseline]:.3f}")
    
else:
    print("No cross-validation results to display")

# Save detailed results
print("\nSaving cross-validation results...")
with open('cv_detailed_results.json', 'w') as f:
    # Convert numpy arrays to lists for JSON serialization
    json_results = {}
    for cancer_type, results in cv_results.items():
        json_results[cancer_type] = {}
        for model_name, metrics in results.items():
            json_results[cancer_type][model_name] = {}
            for metric_name, value in metrics.items():
                if isinstance(value, np.ndarray):
                    json_results[cancer_type][model_name][metric_name] = value.tolist()
                elif isinstance(value, (np.floating, np.integer)):
                    json_results[cancer_type][model_name][metric_name] = float(value)
                else:
                    json_results[cancer_type][model_name][metric_name] = value
    
    json.dump(json_results, f, indent=2)

if not cv_summary.empty:
    cv_summary.to_csv('cv_summary_results.csv', index=False)

print("Cross-validation analysis completed successfully")
