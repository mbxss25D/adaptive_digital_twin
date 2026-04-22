#!/usr/bin/env python3
"""
CHUNK 2: Patient Analysis with Gene Visualization
Add detailed patient gene expression analysis with real-time plots

Save as: chunk2_patient_analysis.py
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from chunk1_basic_system import BasicDigitalTwin
import os

class PatientAnalyzer(BasicDigitalTwin):
    """Extended digital twin with detailed patient analysis"""
    
    def __init__(self):
        super().__init__()
        print("🔬 Patient Analyzer Module Loaded")
        
        # Gene information
        self.gene_info = {
            'TP53': {'name': 'Tumor Protein 53', 'type': 'Tumor Suppressor'},
            'EGFR': {'name': 'Epidermal Growth Factor Receptor', 'type': 'Oncogene'},
            'BRCA1': {'name': 'Breast Cancer 1', 'type': 'Tumor Suppressor'},
            'MYC': {'name': 'MYC Proto-Oncogene', 'type': 'Oncogene'},
            'RAS': {'name': 'RAS Proto-Oncogene', 'type': 'Oncogene'}
        }
    
    def analyze_patient_profile(self, patient_id, gene_expression, treatment_outcome=None):
        """Detailed analysis of patient gene expression profile"""
        
        print(f"\n🔍 DETAILED ANALYSIS: {patient_id}")
        print("="*50)
        
        # Add to database first
        self.add_patient(patient_id, gene_expression, treatment_outcome)
        
        # Perform detailed analysis
        analysis_results = self._perform_gene_analysis(gene_expression, patient_id)
        
        # Create detailed visualization
        self._create_patient_visualization(patient_id, gene_expression, analysis_results, treatment_outcome)
        
        return analysis_results
    
    def _perform_gene_analysis(self, gene_expression, patient_id):
        """Analyze gene expression patterns"""
        
        genes = ['TP53', 'EGFR', 'BRCA1', 'MYC', 'RAS']
        analysis = {
            'patient_id': patient_id,
            'overexpressed_genes': [],
            'normal_genes': [],
            'cancer_risk_score': 0,
            'gene_details': []
        }
        
        print(f"\n📊 Gene Expression Analysis:")
        print("-"*40)
        
        total_score = 0
        for i, (gene, expr) in enumerate(zip(genes[:len(gene_expression)], gene_expression)):
            gene_analysis = {
                'gene': gene,
                'expression': expr,
                'fold_change': expr,
                'status': 'HIGH' if expr > 2.0 else 'NORMAL',
                'gene_type': self.gene_info.get(gene, {}).get('type', 'Unknown'),
                'full_name': self.gene_info.get(gene, {}).get('name', gene)
            }
            
            # Calculate contribution to cancer risk
            if expr > 2.0:
                analysis['overexpressed_genes'].append(gene)
                if gene_analysis['gene_type'] == 'Oncogene':
                    total_score += expr * 2  # Oncogenes contribute more when overexpressed
                else:
                    total_score += expr * 1.5
            else:
                analysis['normal_genes'].append(gene)
                total_score += expr
            
            analysis['gene_details'].append(gene_analysis)
            
            # Display analysis
            emoji = "🔴" if expr > 2.0 else "🟢"
            risk_contribution = "HIGH RISK" if expr > 2.0 and gene_analysis['gene_type'] == 'Oncogene' else "Low risk"
            
            print(f"{emoji} {gene} ({gene_analysis['gene_type']}):")
            print(f"   Expression: {expr:.1f}x ({gene_analysis['status']})")
            print(f"   Risk: {risk_contribution}")
            print()
        
        # Calculate overall cancer risk score
        analysis['cancer_risk_score'] = min(100, (total_score / len(gene_expression)) * 20)
        
        print(f"🎯 Overall Cancer Risk Score: {analysis['cancer_risk_score']:.1f}/100")
        print(f"📈 Overexpressed Genes: {len(analysis['overexpressed_genes'])}/{len(gene_expression)}")
        
        return analysis
    
    def _create_patient_visualization(self, patient_id, gene_expression, analysis, treatment_outcome):
        """Create detailed patient visualization"""
        
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
        
        # Plot 1: Gene expression bar chart
        genes = ['TP53', 'EGFR', 'BRCA1', 'MYC', 'RAS'][:len(gene_expression)]
        gene_types = [self.gene_info.get(gene, {}).get('type', 'Unknown') for gene in genes]
        
        # Color by gene type
        colors = ['red' if gt == 'Oncogene' else 'blue' for gt in gene_types]
        
        bars = ax1.bar(genes, gene_expression, color=colors, alpha=0.7, edgecolor='black')
        ax1.axhline(y=2.0, color='red', linestyle='--', linewidth=2, label='Overexpression Threshold')
        ax1.set_ylabel('Fold Change (Cancer vs Normal)')
        ax1.set_title(f'Gene Expression Profile: {patient_id}')
        ax1.legend()
        ax1.set_ylim(0, max(gene_expression) * 1.3)
        
        # Add value labels and status
        for bar, expr, gene in zip(bars, gene_expression, genes):
            height = bar.get_height()
            status = 'HIGH' if expr > 2.0 else 'NORM'
            ax1.text(bar.get_x() + bar.get_width()/2., height + 0.05,
                    f'{expr:.1f}x\n{status}', ha='center', va='bottom', fontsize=9, fontweight='bold')
        
        # Plot 2: Risk assessment gauge
        self._draw_risk_gauge(ax2, analysis['cancer_risk_score'], patient_id)
        
        # Plot 3: Gene type breakdown
        oncogenes = sum(1 for detail in analysis['gene_details'] if detail['gene_type'] == 'Oncogene' and detail['expression'] > 2.0)
        tumor_suppressors = sum(1 for detail in analysis['gene_details'] if detail['gene_type'] == 'Tumor Suppressor' and detail['expression'] > 2.0)
        normal_genes = len(analysis['normal_genes'])
        
        categories = ['Overexpressed\nOncogenes', 'Overexpressed\nTumor Suppressors', 'Normal\nExpression']
        values = [oncogenes, tumor_suppressors, normal_genes]
        colors_pie = ['red', 'orange', 'green']
        
        if sum(values) > 0:
            ax3.pie(values, labels=categories, colors=colors_pie, autopct='%1.0f%%', startangle=90)
        ax3.set_title('Gene Status Distribution')
        
        # Plot 4: Patient position in database context
        if len(self.patients_db) > 1:
            # Create scatter plot of all patients
            patient_scores = []
            patient_ids = []
            
            for pid in self.patients_db.index:
                genes_patient = self.patients_db.loc[pid].values
                # Calculate simple score for visualization
                score = np.mean(genes_patient)
                patient_scores.append(score)
                patient_ids.append(pid)
            
            # Color by outcome
            colors_scatter = []
            for pid in patient_ids:
                if pid in self.outcomes_db:
                    if 'success' in str(self.outcomes_db[pid]).lower() or self.outcomes_db[pid] in ['Gefitinib', 'Imatinib', 'Dasatinib']:
                        colors_scatter.append('green')
                    else:
                        colors_scatter.append('red')
                else:
                    colors_scatter.append('gray')
            
            x_positions = range(len(patient_ids))
            ax4.scatter(x_positions, patient_scores, c=colors_scatter, s=100, alpha=0.7, edgecolors='black')
            
            # Highlight current patient
            if patient_id in patient_ids:
                current_idx = patient_ids.index(patient_id)
                ax4.scatter(current_idx, patient_scores[current_idx], c='yellow', s=300, marker='*', 
                           edgecolors='red', linewidths=3, label='Current Patient')
            
            ax4.set_xlabel('Patient Index')
            ax4.set_ylabel('Average Gene Expression')
            ax4.set_title('Patient Database Context')
            ax4.set_xticks(x_positions)
            ax4.set_xticklabels(patient_ids, rotation=45)
            ax4.legend()
            ax4.grid(True, alpha=0.3)
        else:
            ax4.text(0.5, 0.5, 'Single Patient\nNo Comparison Available', 
                    ha='center', va='center', transform=ax4.transAxes, fontsize=12)
            ax4.set_title('Patient Database Context')
        
        # Overall title
        outcome_text = f" | Treatment: {treatment_outcome}" if treatment_outcome else ""
        risk_level = "HIGH" if analysis['cancer_risk_score'] > 60 else "MEDIUM" if analysis['cancer_risk_score'] > 40 else "LOW"
        
        plt.suptitle(f'Patient Analysis: {patient_id} (Risk: {risk_level}){outcome_text}', 
                    fontsize=14, fontweight='bold')
        plt.tight_layout()
        
        # Save plot
        save_path = f'{self.results_dir}/patient_analysis_{patient_id}.png'
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        print(f"📊 Patient analysis saved: {save_path}")
        
        plt.show()
        plt.close()
    
    def _draw_risk_gauge(self, ax, risk_score, patient_id):
        """Draw cancer risk assessment gauge"""
        
        # Create semicircle gauge
        theta = np.linspace(0, np.pi, 100)
        ax.plot(np.cos(theta), np.sin(theta), 'lightgray', linewidth=15, alpha=0.3)
        
        # Risk level coloring
        if risk_score >= 70:
            color = 'red'
            label = 'HIGH RISK'
        elif risk_score >= 50:
            color = 'orange'
            label = 'MEDIUM RISK'
        elif risk_score >= 30:
            color = 'yellow'
            label = 'LOW-MEDIUM RISK'
        else:
            color = 'green'
            label = 'LOW RISK'
        
        # Risk level arc
        risk_theta = np.linspace(0, np.pi * risk_score/100, 50)
        ax.plot(np.cos(risk_theta), np.sin(risk_theta), color, linewidth=15, alpha=0.8)
        
        # Needle
        needle_angle = np.pi * (1 - risk_score/100)
        ax.arrow(0, 0, 0.8*np.cos(needle_angle), 0.8*np.sin(needle_angle), 
                head_width=0.05, head_length=0.08, fc='black', ec='black', linewidth=2)
        
        # Labels
        ax.text(0, -0.2, f'{risk_score:.1f}', ha='center', va='center', 
               fontsize=18, fontweight='bold')
        ax.text(0, -0.4, label, ha='center', va='center', 
               fontsize=10, color=color, fontweight='bold')
        ax.text(0, -0.6, 'Cancer Risk Score', ha='center', va='center', fontsize=8)
        
        # Gauge markings
        for i in range(0, 101, 25):
            angle = np.pi * (1 - i/100)
            x1, y1 = 0.85 * np.cos(angle), 0.85 * np.sin(angle)
            x2, y2 = 0.95 * np.cos(angle), 0.95 * np.sin(angle)
            ax.plot([x1, x2], [y1, y2], 'black', linewidth=2)
            ax.text(1.05 * np.cos(angle), 1.05 * np.sin(angle), f'{i}', 
                   ha='center', va='center', fontsize=8)
        
        ax.set_xlim(-1.2, 1.2)
        ax.set_ylim(-0.8, 1.2)
        ax.set_aspect('equal')
        ax.axis('off')
        ax.set_title(f'Cancer Risk Assessment\n{patient_id}', fontweight='bold')
    
    def compare_patients(self, patient_ids):
        """Compare multiple patients side by side"""
        
        if len(patient_ids) < 2:
            print("⚠️ Need at least 2 patients for comparison")
            return
        
        print(f"\n🔄 COMPARING PATIENTS: {', '.join(patient_ids)}")
        print("="*60)
        
        # Create comparison visualization
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
        
        # Plot 1: Gene expression comparison
        genes = ['TP53', 'EGFR', 'BRCA1', 'MYC', 'RAS']
        x = np.arange(len(genes))
        width = 0.8 / len(patient_ids)
        
        colors = ['blue', 'red', 'green', 'orange', 'purple']
        
        for i, patient_id in enumerate(patient_ids):
            if patient_id in self.patients_db.index:
                gene_values = self.patients_db.loc[patient_id].values[:len(genes)]
                ax1.bar(x + i*width, gene_values, width, 
                       label=patient_id, color=colors[i % len(colors)], alpha=0.7)
        
        ax1.axhline(y=2.0, color='red', linestyle='--', alpha=0.7, label='Overexpression Threshold')
        ax1.set_xlabel('Genes')
        ax1.set_ylabel('Expression Level')
        ax1.set_title('Gene Expression Comparison')
        ax1.set_xticks(x + width * (len(patient_ids)-1) / 2)
        ax1.set_xticklabels(genes)
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # Plot 2: Risk score comparison
        risk_scores = []
        for patient_id in patient_ids:
            if patient_id in self.patients_db.index:
                genes_patient = self.patients_db.loc[patient_id].values
                # Simple risk calculation
                risk = min(100, np.mean(genes_patient) * 20)
                risk_scores.append(risk)
            else:
                risk_scores.append(0)
        
        bars = ax2.bar(patient_ids, risk_scores, 
                      color=[colors[i % len(colors)] for i in range(len(patient_ids))], 
                      alpha=0.7, edgecolor='black')
        ax2.set_ylabel('Cancer Risk Score')
        ax2.set_title('Risk Score Comparison')
        ax2.set_ylim(0, 100)
        
        # Add value labels
        for bar, score in zip(bars, risk_scores):
            ax2.text(bar.get_x() + bar.get_width()/2., bar.get_height() + 1,
                    f'{score:.1f}', ha='center', va='bottom', fontweight='bold')
        
        plt.tight_layout()
        
        # Save comparison
        save_path = f'{self.results_dir}/patient_comparison.png'
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        print(f"📊 Patient comparison saved: {save_path}")
        
        plt.show()
        plt.close()


def test_patient_analysis():
    """Test the patient analysis system"""
    
    print("🧪 TESTING PATIENT ANALYSIS SYSTEM")
    print("="*60)
    
    # Initialize analyzer
    analyzer = PatientAnalyzer()
    
    # Analyze individual patients
    print("\n📚 Analyzing Individual Patients:")
    
    test_patients = [
        ('Patient_A', [2.8, 3.2, 1.5, 1.1, 1.3], 'Gefitinib'),
        ('Patient_B', [2.1, 1.8, 1.4, 2.9, 2.3], 'Imatinib'),
        ('Patient_C', [1.9, 3.0, 2.1, 1.2, 1.1], 'Gefitinib'),
    ]
    
    for patient_id, genes, treatment in test_patients:
        print(f"\n{'='*30}")
        analysis = analyzer.analyze_patient_profile(patient_id, genes, treatment)
        print(f"Analysis complete for {patient_id}")
        print(f"Risk Score: {analysis['cancer_risk_score']:.1f}/100")
        print(f"Overexpressed genes: {', '.join(analysis['overexpressed_genes'])}")
    
    # Compare patients
    print(f"\n{'='*30}")
    print("🔄 Comparing All Patients:")
    analyzer.compare_patients(['Patient_A', 'Patient_B', 'Patient_C'])
    
    print("\n✅ PATIENT ANALYSIS TEST COMPLETE!")
    print("🎯 Next: Run Chunk 3 for Similarity Engine")
    
    return analyzer


if __name__ == "__main__":
    # Run the test
    patient_analyzer = test_patient_analysis()
    
    print("\n" + "="*60)
    print("📝 CHUNK 2 COMPLETED SUCCESSFULLY!")
    print("="*60)
    print("✅ Patient analysis system working")
    print("✅ Detailed gene expression analysis")
    print("✅ Risk assessment gauges created")
    print("✅ Patient comparison functionality")
    
    print(f"\n📁 Check your results in: analysis_results/")
    print("🚀 Ready for Chunk 3: Similarity Engine!")
