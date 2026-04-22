class StatisticalSignificanceTester:
    def __init__(self, alpha=0.05):
        self.alpha = alpha
        self.test_results = {}
        self.effect_sizes = {}
        
    def extract_performance_scores(self, cv_results):
        """Extract performance scores for statistical testing"""
        model_scores = {}
        
        for cancer_type, results in cv_results.items():
            for model_name, metrics in results.items():
                if 'accuracy_values' in metrics:
                    if model_name not in model_scores:
                        model_scores[model_name] = []
                    model_scores[model_name].extend(metrics['accuracy_values'])
        
        return model_scores
    
    def paired_t_test(self, scores1, scores2, model1_name, model2_name):
        """Perform paired t-test between two models"""
        if len(scores1) != len(scores2):
            # If unequal lengths, use minimum length
            min_len = min(len(scores1), len(scores2))
            scores1 = scores1[:min_len]
            scores2 = scores2[:min_len]
        
        if len(scores1) < 3:
            return None
        
        try:
            t_stat, p_value = ttest_ind(scores1, scores2)
            effect_size = (np.mean(scores1) - np.mean(scores2)) / np.sqrt((np.var(scores1) + np.var(scores2)) / 2)
            
            return {
                'test_type': 'Independent t-test',
                'statistic': t_stat,
                'p_value': p_value,
                'significant': p_value < self.alpha,
                'effect_size': effect_size,
                'model1_mean': np.mean(scores1),
                'model2_mean': np.mean(scores2),
                'model1_std': np.std(scores1),
                'model2_std': np.std(scores2),
                'sample_size': len(scores1)
            }
        except Exception as e:
            print(f"T-test failed for {model1_name} vs {model2_name}: {str(e)}")
            return None
    
    def mann_whitney_u_test(self, scores1, scores2, model1_name, model2_name):
        """Perform Mann-Whitney U test (non-parametric alternative)"""
        try:
            u_stat, p_value = mannwhitneyu(scores1, scores2, alternative='two-sided')
            
            # Calculate effect size (rank-biserial correlation)
            n1, n2 = len(scores1), len(scores2)
            effect_size = (2 * u_stat) / (n1 * n2) - 1
            
            return {
                'test_type': 'Mann-Whitney U test',
                'statistic': u_stat,
                'p_value': p_value,
                'significant': p_value < self.alpha,
                'effect_size': effect_size,
                'model1_median': np.median(scores1),
                'model2_median': np.median(scores2),
                'sample_size_1': n1,
                'sample_size_2': n2
            }
        except Exception as e:
            print(f"Mann-Whitney U test failed for {model1_name} vs {model2_name}: {str(e)}")
            return None
    
    def wilcoxon_signed_rank_test(self, scores1, scores2, model1_name, model2_name):
        """Perform Wilcoxon signed-rank test for paired samples"""
        from scipy.stats import wilcoxon
        
        if len(scores1) != len(scores2):
            min_len = min(len(scores1), len(scores2))
            scores1 = scores1[:min_len]
            scores2 = scores2[:min_len]
        
        if len(scores1) < 6:  # Minimum for Wilcoxon test
            return None
        
        try:
            differences = np.array(scores1) - np.array(scores2)
            # Remove zero differences
            differences = differences[differences != 0]
            
            if len(differences) < 3:
                return None
            
            w_stat, p_value = wilcoxon(differences)
            
            # Effect size (r = Z / sqrt(N))
            z_score = stats.norm.ppf(1 - p_value/2)  # Approximate Z-score
            effect_size = z_score / np.sqrt(len(differences))
            
            return {
                'test_type': 'Wilcoxon signed-rank test',
                'statistic': w_stat,
                'p_value': p_value,
                'significant': p_value < self.alpha,
                'effect_size': effect_size,
                'median_difference': np.median(differences),
                'sample_size': len(differences)
            }
        except Exception as e:
            print(f"Wilcoxon test failed for {model1_name} vs {model2_name}: {str(e)}")
            return None
    
    def bonferroni_correction(self, p_values):
        """Apply Bonferroni correction for multiple comparisons"""
        corrected_alpha = self.alpha / len(p_values)
        corrected_significant = [p < corrected_alpha for p in p_values]
        return corrected_alpha, corrected_significant
    
    def benjamini_hochberg_correction(self, p_values):
        """Apply Benjamini-Hochberg FDR correction"""
        sorted_indices = np.argsort(p_values)
        sorted_p_values = np.array(p_values)[sorted_indices]
        
        n = len(p_values)
        corrected_significant = np.zeros(n, dtype=bool)
        
        for i in range(n-1, -1, -1):
            critical_value = (i + 1) / n * self.alpha
            if sorted_p_values[i] <= critical_value:
                corrected_significant[sorted_indices[:(i+1)]] = True
                break
        
        return corrected_significant
    
    def comprehensive_model_comparison(self, cv_results):
        """Perform comprehensive statistical comparison of all models"""
        print("Performing comprehensive statistical significance testing...")
        
        model_scores = self.extract_performance_scores(cv_results)
        
        if not model_scores:
            print("No performance scores available for testing")
            return {}
        
        print(f"Available models: {list(model_scores.keys())}")
        
        # Pairwise comparisons
        comparison_results = {}
        p_values_collected = []
        
        model_names = list(model_scores.keys())
        
        for i, model1 in enumerate(model_names):
            comparison_results[model1] = {}
            
            for j, model2 in enumerate(model_names):
                if i < j:  # Avoid duplicate comparisons
                    scores1 = np.array(model_scores[model1])
                    scores2 = np.array(model_scores[model2])
                    
                    print(f"  Comparing {model1} vs {model2}...")
                    print(f"    Sample sizes: {len(scores1)} vs {len(scores2)}")
                    
                    # Perform multiple statistical tests
                    test_results = {}
                    
                    # T-test
                    t_result = self.paired_t_test(scores1, scores2, model1, model2)
                    if t_result:
                        test_results['t_test'] = t_result
                        p_values_collected.append(t_result['p_value'])
                    
                    # Mann-Whitney U test
                    mw_result = self.mann_whitney_u_test(scores1, scores2, model1, model2)
                    if mw_result:
                        test_results['mann_whitney'] = mw_result
                    
                    # Wilcoxon signed-rank (if applicable)
                    if len(scores1) == len(scores2):
                        wilcoxon_result = self.wilcoxon_signed_rank_test(scores1, scores2, model1, model2)
                        if wilcoxon_result:
                            test_results['wilcoxon'] = wilcoxon_result
                    
                    comparison_results[model1][model2] = test_results
                    comparison_results[model2] = comparison_results[model2] if model2 in comparison_results else {}
                    comparison_results[model2][model1] = test_results
        
        # Apply multiple comparison corrections
        if p_values_collected:
            print(f"\nApplying multiple comparison corrections to {len(p_values_collected)} p-values...")
            
            bonferroni_alpha, bonferroni_significant = self.bonferroni_correction(p_values_collected)
            fdr_significant = self.benjamini_hochberg_correction(p_values_collected)
            
            print(f"  Bonferroni corrected alpha: {bonferroni_alpha:.6f}")
            print(f"  Significant after Bonferroni: {sum(bonferroni_significant)}/{len(bonferroni_significant)}")
            print(f"  Significant after FDR: {sum(fdr_significant)}/{len(fdr_significant)}")
        
        self.test_results = comparison_results
        return comparison_results
    
    def generate_significance_report(self):
        """Generate comprehensive significance testing report"""
        if not self.test_results:
            return "No statistical tests have been performed"
        
        report = "STATISTICAL SIGNIFICANCE TESTING REPORT\n"
        report += "=" * 60 + "\n\n"
        
        # Focus on Digital Twin comparisons
        if 'Digital_Twin' in self.test_results:
            report += "🎯 DIGITAL TWIN vs BASELINE MODELS\n"
            report += "-" * 40 + "\n\n"
            
            dt_comparisons = self.test_results['Digital_Twin']
            
            for baseline_model, tests in dt_comparisons.items():
                if baseline_model == 'Digital_Twin':
                    continue
                    
                report += f"Digital Twin vs {baseline_model}:\n"
                
                for test_name, result in tests.items():
                    if result:
                        significance = "SIGNIFICANT" if result['significant'] else "NOT SIGNIFICANT"
                        report += f"  {result['test_type']}:\n"
                        report += f"    p-value: {result['p_value']:.6f}\n"
                        report += f"    Result: {significance}\n"
                        report += f"    Effect size: {result['effect_size']:.4f}\n"
                        
                        if 'model1_mean' in result:
                            report += f"    Digital Twin mean: {result['model1_mean']:.4f} ± {result['model1_std']:.4f}\n"
                            report += f"    {baseline_model} mean: {result['model2_mean']:.4f} ± {result['model2_std']:.4f}\n"
                        
                        report += "\n"
                
                report += "\n"
        
        # Overall summary
        significant_improvements = 0
        total_comparisons = 0
        
        if 'Digital_Twin' in self.test_results:
            for baseline_model, tests in self.test_results['Digital_Twin'].items():
                if baseline_model != 'Digital_Twin':
                    for test_name, result in tests.items():
                        if result and 't_test' in test_name:  # Use t-test as primary
                            total_comparisons += 1
                            if result['significant'] and result.get('model1_mean', 0) > result.get('model2_mean', 0):
                                significant_improvements += 1
        
        report += f"SUMMARY:\n"
        report += f"Digital Twin shows significant improvement in {significant_improvements}/{total_comparisons} comparisons\n"
        
        return report

# Execute statistical significance testing
print("Initializing statistical significance testing...")
stat_tester = StatisticalSignificanceTester(alpha=0.05)

# Perform comprehensive model comparison
comparison_results = stat_tester.comprehensive_model_comparison(cv_results)

# Generate and display significance report
significance_report = stat_tester.generate_significance_report()
print("\n" + significance_report)

# Create comprehensive visualization of statistical results
if comparison_results and 'Digital_Twin' in comparison_results:
    
    # Extract data for visualization
    comparison_data = []
    baseline_models = []
    
    for baseline_model, tests in comparison_results['Digital_Twin'].items():
        if baseline_model != 'Digital_Twin' and tests:
            baseline_models.append(baseline_model)
            
            # Get t-test results as primary comparison
            if 't_test' in tests and tests['t_test']:
                t_result = tests['t_test']
                comparison_data.append({
                    'Baseline_Model': baseline_model,
                    'p_value': t_result['p_value'],
                    'effect_size': t_result['effect_size'],
                    'dt_mean': t_result['model1_mean'],
                    'baseline_mean': t_result['model2_mean'],
                    'dt_std': t_result['model1_std'],
                    'baseline_std': t_result['model2_std'],
                    'significant': t_result['significant']
                })
    
    if comparison_data:
        comparison_df = pd.DataFrame(comparison_data)
        
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        
        # 1. P-values visualization
        colors = ['red' if sig else 'blue' for sig in comparison_df['significant']]
        bars = axes[0,0].bar(comparison_df['Baseline_Model'], -np.log10(comparison_df['p_value']), color=colors)
        axes[0,0].axhline(y=-np.log10(0.05), color='red', linestyle='--', linewidth=2, label='α = 0.05')
        axes[0,0].axhline(y=-np.log10(0.01), color='darkred', linestyle='--', linewidth=2, label='α = 0.01')
        axes[0,0].set_xlabel('Baseline Model')
        axes[0,0].set_ylabel('-log10(p-value)')
        axes[0,0].set_title('Statistical Significance\n(Digital Twin vs Baselines)', fontsize=14, fontweight='bold')
        axes[0,0].tick_params(axis='x', rotation=45)
        axes[0,0].legend()
        
        # Add p-value labels
        for bar, p_val in zip(bars, comparison_df['p_value']):
            axes[0,0].text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1, 
                          f'p={p_val:.4f}', ha='center', va='bottom', rotation=90, fontsize=8)
        
        # 2. Effect sizes
        colors = ['green' if eff > 0 else 'red' for eff in comparison_df['effect_size']]
        bars = axes[0,1].bar(comparison_df['Baseline_Model'], comparison_df['effect_size'], color=colors, alpha=0.7)
        axes[0,1].axhline(y=0, color='black', linestyle='-', alpha=0.5)
        axes[0,1].axhline(y=0.2, color='green', linestyle='--', alpha=0.5, label='Small effect')
        axes[0,1].axhline(y=0.5, color='orange', linestyle='--', alpha=0.5, label='Medium effect')
        axes[0,1].axhline(y=0.8, color='red', linestyle='--', alpha=0.5, label='Large effect')
        axes[0,1].set_xlabel('Baseline Model')
        axes[0,1].set_ylabel('Effect Size (Cohen\'s d)')
        axes[0,1].set_title('Effect Sizes\n(Digital Twin - Baseline)', fontsize=14, fontweight='bold')
        axes[0,1].tick_params(axis='x', rotation=45)
        axes[0,1].legend()
        
        # Add effect size labels
        for bar, eff in zip(bars, comparison_df['effect_size']):
            axes[0,1].text(bar.get_x() + bar.get_width()/2, 
                          bar.get_height() + (0.05 if eff > 0 else -0.1), 
                          f'{eff:.3f}', ha='center', va='bottom' if eff > 0 else 'top', fontsize=9)
        
        # 3. Performance comparison with error bars
        x_pos = np.arange(len(baseline_models) + 1)
        models_with_dt = ['Digital_Twin'] + list(comparison_df['Baseline_Model'])
        
        dt_mean = comparison_df['dt_mean'].iloc[0]
        dt_std = comparison_df['dt_std'].iloc[0]
        
        means = [dt_mean] + list(comparison_df['baseline_mean'])
        stds = [dt_std] + list(comparison_df['baseline_std'])
        
        colors = ['#FF6B6B'] + ['#4ECDC4'] * len(baseline_models)
        
        bars = axes[1,0].bar(x_pos, means, yerr=stds, capsize=5, color=colors, alpha=0.8)
        axes[1,0].set_xlabel('Model')
        axes[1,0].set_ylabel('Accuracy')
        axes[1,0].set_title('Performance Comparison with Standard Deviation', fontsize=14, fontweight='bold')
        axes[1,0].set_xticks(x_pos)
        axes[1,0].set_xticklabels(models_with_dt, rotation=45)
        
        # Add mean labels
        for bar, mean, std in zip(bars, means, stds):
            axes[1,0].text(bar.get_x() + bar.get_width()/2, bar.get_height() + std + 0.005, 
                          f'{mean:.3f}', ha='center', va='bottom', fontweight='bold')
        
        # 4. Significance summary pie chart
        sig_counts = comparison_df['significant'].value_counts()
        labels = ['Significant' if True in sig_counts.index else 'Not Significant',
                 'Not Significant' if False in sig_counts.index else 'Significant']
        sizes = [sig_counts.get(True, 0), sig_counts.get(False, 0)]
        colors_pie = ['lightgreen', 'lightcoral']
        
        if sum(sizes) > 0:
            wedges, texts, autotexts = axes[1,1].pie(sizes, labels=labels, autopct='%1.0f%%', 
                                                    colors=colors_pie, startangle=90)
            axes[1,1].set_title('Statistical Significance Summary\n(Digital Twin vs Baselines)', 
                               fontsize=14, fontweight='bold')
            
            # Make percentage text bold
            for autotext in autotexts:
                autotext.set_fontweight('bold')
                autotext.set_fontsize(12)
        
        plt.tight_layout()
        plt.show()
        
        # Create summary table
        summary_table = comparison_df[['Baseline_Model', 'p_value', 'effect_size', 'significant']].copy()
        summary_table['p_value'] = summary_table['p_value'].apply(lambda x: f"{x:.6f}")
        summary_table['effect_size'] = summary_table['effect_size'].apply(lambda x: f"{x:.4f}")
        summary_table['significant'] = summary_table['significant'].apply(lambda x: "Yes" if x else "No")
        
        print("\nSTATISTICAL COMPARISON SUMMARY TABLE:")
        print("=" * 60)
        print(summary_table.to_string(index=False))
        
        # Save results
        summary_table.to_csv('statistical_significance_results.csv', index=False)

else:
    print("No statistical comparison results available for visualization")

print("\nStatistical significance testing completed successfully")
