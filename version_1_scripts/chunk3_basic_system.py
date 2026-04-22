#!/usr/bin/env python3
"""
CHUNK 3: Patient Similarity Engine
Add patient similarity matching with visualization

Save as: chunk3_similarity_engine.py
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics.pairwise import cosine_similarity
from chunk2_basic_system import PatientAnalyzer

class SimilarityEngine(PatientAnalyzer):
    """Digital twin with patient similarity matching capabilities"""
    
    def __init__(self):
        super().__init__()
        print("🔍 Similarity Engine Module Loaded")
        self.similarity_threshold = 0.7
        self.similarity_history = {}
    
    def find_similar_patients(self, target_genes, target_patient_id="NewPatient", show_visualization=True):
        """Find patients with similar gene expression patterns"""
        
        print(f"\n🎯 FINDING SIMILAR PATIENTS FOR: {target_patient_id}")
        print("="*50)
        print(f"Target Gene Expression: {target_genes}")
        
        if self.patients_db.empty:
            print("⚠️ No patients in database for comparison")
            return []
        
        # Calculate similarity scores
        target_array = np.array(target_genes).reshape(1, -1)
        similarity_scores = cosine_similarity(target_array, self.patients_db.values)[0]
        
        # Create similarity results
        similar_patients = []
        print(f"\n📊 Similarity Analysis:")
        print("-"*40)
        
        for i, score in enumerate(similarity_scores):
            patient_id = self.patients_db.index[i]
            patient_genes = self.patients_db.iloc[i].values
            treatment = self.outcomes_db.get(patient_id, "Unknown")
            
            similar_patients.append({
                'patient_id': patient_id,
                'similarity_score': score,
                'genes': patient_genes,
                'treatment': treatment,
                'is_similar': score >= self.similarity_threshold
            })
            
            # Display results
            similarity_emoji = "✅" if score >= self.similarity_threshold else "❌"
            print(f"{similarity_emoji} {patient_id}: {score:.3f} similarity | Treatment: {treatment}")
        
        # Sort by similarity (highest first)
        similar_patients.sort(key=lambda x: x['similarity_score'], reverse=True)
        
        # Count similar patients
        highly_similar = [p for p in similar_patients if p['is_similar']]
        print(f"\n🎯 Found {len(highly_similar)} highly similar patients (≥{self.similarity_threshold})")
        
        # Store similarity analysis
        self.similarity_history[target_patient_id] = {
            'target_genes': target_genes,
            'similar_patients': similar_patients,
            'analysis_timestamp': pd.Timestamp.now().isoformat()
        }
        
        # Create visualization
        if show_visualization:
            self._visualize_similarity_analysis(target_patient_id, target_genes, similar_patients)
        
        return similar_patients
    
    def _visualize_similarity_analysis(self, target_patient_id, target_genes, similar_patients):
        """Create comprehensive similarity analysis visualization"""
        
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
        
        # Plot 1: Similarity score distribution
        scores = [p['similarity_score'] for p in similar_patients]
        
        ax1.hist(scores, bins=min(10, len(scores)), alpha=0.7, color='skyblue', edgecolor='black')
        ax1.axvline(x=self.similarity_threshold, color='red', linestyle='--', linewidth=2, 
                   label=f'Similarity Threshold ({self.similarity_threshold})')
        ax1.set_xlabel('Similarity Score')
        ax1.set_ylabel('Number of Patients')
        ax1.set_title('Similarity Score Distribution')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # Add statistics
        mean_sim = np.mean(scores)
        ax1.text(0.02, 0.98, f'Mean: {mean_sim:.3f}\nMax: {max(scores):.3f}\nMin: {min(scores):.3f}', 
                transform=ax1.transAxes, verticalalignment='top',
                bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
        
        # Plot 2: Top similar patients ranking
        top_patients = similar_patients[:5]  # Top 5
        patient_names = [p['patient_id'] for p in top_patients]
        similarity_values = [p['similarity_score'] for p in top_patients]
        
        colors_bar = ['green' if s >= self.similarity_threshold else 'orange' for s in similarity_values]
        bars = ax2.barh(patient_names, similarity_values, color=colors_bar, alpha=0.8, edgecolor='black')
        
        ax2.axvline(x=self.similarity_threshold, color='red', linestyle='--', alpha=0.7)
        ax2.set_xlabel('Similarity Score')
        ax2.set_title('Top 5 Most Similar Patients')
        ax2.set_xlim(0, 1)
        
        # Add similarity values on bars
        for bar, sim in zip(bars, similarity_values):
            ax2.text(bar.get_width() + 0.01, bar.get_y() + bar.get_height()/2,
                    f'{sim:.3f}', va='center', fontweight='bold')
        
        # Plot 3: Gene expression comparison with most similar patient
        if similar_patients:
            most_similar = similar_patients[0]
            genes = ['TP53', 'EGFR', 'BRCA1', 'MYC', 'RAS'][:len(target_genes)]
            
            x = np.arange(len(genes))
            width = 0.35
            
            bars1 = ax3.bar(x - width/2, target_genes, width, label=f'{target_patient_id} (Target)', 
                           color='blue', alpha=0.7, edgecolor='black')
            bars2 = ax3.bar(x + width/2, most_similar['genes'][:len(genes)], width, 
                           label=f'{most_similar["patient_id"]} (Most Similar)', 
                           color='orange', alpha=0.7, edgecolor='black')
            
            ax3.axhline(y=2.0, color='red', linestyle='--', alpha=0.7, label='Overexpression Threshold')
            ax3.set_xlabel('Genes')
            ax3.set_ylabel('Expression Level')
            ax3.set_title(f'Gene Expression Comparison\n(Similarity: {most_similar["similarity_score"]:.3f})')
            ax3.set_xticks(x)
            ax3.set_xticklabels(genes)
            ax3.legend()
            ax3.grid(True, alpha=0.3)
            
            # Add value labels
            for bars in [bars1, bars2]:
                for bar in bars:
                    height = bar.get_height()
                    ax3.text(bar.get_x() + bar.get_width()/2., height + 0.05,
                            f'{height:.1f}', ha='center', va='bottom', fontsize=9)
        
        # Plot 4: Treatment recommendations from similar patients
        similar_with_treatment = [p for p in similar_patients if p['treatment'] != 'Unknown' and p['is_similar']]
        
        if similar_with_treatment:
            treatments = [p['treatment'] for p in similar_with_treatment]
            treatment_counts = {}
            treatment_similarities = {}
            
            for p in similar_with_treatment:
                treatment = p['treatment']
                if treatment not in treatment_counts:
                    treatment_counts[treatment] = 0
                    treatment_similarities[treatment] = []
                treatment_counts[treatment] += 1
                treatment_similarities[treatment].append(p['similarity_score'])
            
            # Create pie chart with treatment recommendations
            treatments_list = list(treatment_counts.keys())
            counts = list(treatment_counts.values())
            
            # Calculate average similarity for each treatment
            avg_similarities = [np.mean(treatment_similarities[t]) for t in treatments_list]
            
            # Create pie chart
            colors_pie = plt.cm.Set3(np.linspace(0, 1, len(treatments_list)))
            wedges, texts, autotexts = ax4.pie(counts, labels=treatments_list, colors=colors_pie, 
                                              autopct='%1.0f%%', startangle=90)
            
            ax4.set_title('Treatment Recommendations\nfrom Similar Patients')
            
            # Add similarity information in text box
            recommendation_text = "Recommendations:\n"
            for treatment, count, avg_sim in zip(treatments_list, counts, avg_similarities):
                recommendation_text += f"• {treatment}: {count} patient(s)\n  (Avg similarity: {avg_sim:.3f})\n"
            
            ax4.text(1.3, 0.5, recommendation_text, transform=ax4.transAxes, 
                    verticalalignment='center', fontsize=9,
                    bbox=dict(boxstyle='round', facecolor='lightgray', alpha=0.8))
        else:
            ax4.text(0.5, 0.5, 'No Treatment Data\nfor Similar Patients', 
                    ha='center', va='center', transform=ax4.transAxes, fontsize=12)
            ax4.set_title('Treatment Recommendations\nfrom Similar Patients')
        
        plt.suptitle(f'Patient Similarity Analysis: {target_patient_id}', fontsize=16, fontweight='bold')
        plt.tight_layout()
        
        # Save visualization
        save_path = f'{self.results_dir}/similarity_analysis_{target_patient_id}.png'
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        print(f"📊 Similarity analysis saved: {save_path}")
        
        plt.show()
        plt.close()
    
    def predict_treatment_from_similarity(self, target_genes, target_patient_id="NewPatient"):
        """Predict treatment based on similar patients"""
        
        print(f"\n💊 TREATMENT PREDICTION FOR: {target_patient_id}")
        print("="*50)
        
        # Find similar patients
        similar_patients = self.find_similar_patients(target_genes, target_patient_id, show_visualization=False)
        
        # Get treatment recommendations
        similar_with_treatment = [p for p in similar_patients if p['treatment'] != 'Unknown' and p['is_similar']]
        
        if not similar_with_treatment:
            print("❌ No similar patients with known treatments found")
            return None
        
        # Calculate treatment recommendations with confidence
        treatment_recommendations = {}
        
        for patient in similar_with_treatment:
            treatment = patient['treatment']
            similarity = patient['similarity_score']
            
            if treatment not in treatment_recommendations:
                treatment_recommendations[treatment] = {
                    'count': 0,
                    'total_similarity': 0,
                    'similarities': [],
                    'supporting_patients': []
                }
            
            treatment_recommendations[treatment]['count'] += 1
            treatment_recommendations[treatment]['total_similarity'] += similarity
            treatment_recommendations[treatment]['similarities'].append(similarity)
            treatment_recommendations[treatment]['supporting_patients'].append(patient['patient_id'])
        
        # Calculate confidence scores
        final_recommendations = []
        
        for treatment, data in treatment_recommendations.items():
            avg_similarity = data['total_similarity'] / data['count']
            confidence = min(100, avg_similarity * 100)  # Convert to percentage
            
            final_recommendations.append({
                'treatment': treatment,
                'confidence': confidence,
                'avg_similarity': avg_similarity,
                'supporting_patients': data['count'],
                'patient_list': data['supporting_patients'],
                'similarity_range': f"{min(data['similarities']):.3f} - {max(data['similarities']):.3f}"
            })
        
        # Sort by confidence
        final_recommendations.sort(key=lambda x: x['confidence'], reverse=True)
        
        # Display recommendations
        print(f"\n🎯 TREATMENT RECOMMENDATIONS:")
        print("-"*40)
        
        for i, rec in enumerate(final_recommendations, 1):
            confidence_level = "HIGH" if rec['confidence'] >= 70 else "MEDIUM" if rec['confidence'] >= 50 else "LOW"
            
            print(f"{i}. {rec['treatment']}")
            print(f"   Confidence: {rec['confidence']:.1f}% ({confidence_level})")
            print(f"   Supporting Patients: {rec['supporting_patients']} ({', '.join(rec['patient_list'])})")
            print(f"   Avg Similarity: {rec['avg_similarity']:.3f}")
            print(f"   Similarity Range: {rec['similarity_range']}")
            print()
        
        return final_recommendations
    
    def create_similarity_network(self):
        """Create network visualization of patient similarities"""
        
        if len(self.patients_db) < 2:
            print("⚠️ Need at least 2 patients to create similarity network")
            return
        
        print(f"\n🕸️ CREATING PATIENT SIMILARITY NETWORK")
        print("="*50)
        
        # Calculate similarity matrix
        similarity_matrix = cosine_similarity(self.patients_db.values)
        
        # Create network visualization
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))
        
        # Plot 1: Similarity heatmap
        patient_ids = self.patients_db.index.tolist()
        mask = np.triu(np.ones_like(similarity_matrix, dtype=bool))  # Only show lower triangle
        
        sns.heatmap(similarity_matrix, mask=mask, annot=True, cmap='coolwarm', center=0,
                   square=True, xticklabels=patient_ids, yticklabels=patient_ids,
                   cbar_kws={'label': 'Cosine Similarity'}, ax=ax1)
        ax1.set_title('Patient Similarity Heatmap')
        
        # Plot 2: Network graph (simplified)
        n_patients = len(patient_ids)
        
        # Position patients in a circle
        angles = np.linspace(0, 2*np.pi, n_patients, endpoint=False)
        x_pos = np.cos(angles)
        y_pos = np.sin(angles)
        
        # Draw connections for high similarity (> threshold)
        for i in range(n_patients):
            for j in range(i+1, n_patients):
                if similarity_matrix[i][j] >= self.similarity_threshold:
                    ax2.plot([x_pos[i], x_pos[j]], [y_pos[i], y_pos[j]], 
                            'gray', alpha=0.6, linewidth=2)
                    
                    # Add similarity score as text
                    mid_x = (x_pos[i] + x_pos[j]) / 2
                    mid_y = (y_pos[i] + y_pos[j]) / 2
                    ax2.text(mid_x, mid_y, f'{similarity_matrix[i][j]:.2f}', 
                            ha='center', va='center', fontsize=8, 
                            bbox=dict(boxstyle='round,pad=0.2', facecolor='white', alpha=0.8))
        
        # Draw patient nodes
        colors_nodes = []
        for patient_id in patient_ids:
            if patient_id in self.outcomes_db:
                colors_nodes.append('lightgreen')
            else:
                colors_nodes.append('lightblue')
        
        ax2.scatter(x_pos, y_pos, c=colors_nodes, s=300, alpha=0.8, edgecolors='black', linewidth=2)
        
        # Add patient labels
        for i, patient_id in enumerate(patient_ids):
            ax2.text(x_pos[i]*1.2, y_pos[i]*1.2, patient_id, ha='center', va='center', 
                    fontweight='bold', fontsize=10)
        
        ax2.set_xlim(-1.5, 1.5)
        ax2.set_ylim(-1.5, 1.5)
        ax2.set_aspect('equal')
        ax2.axis('off')
        ax2.set_title(f'Patient Similarity Network\n(Threshold: {self.similarity_threshold})')
        
        # Add legend
        legend_elements = [
            plt.scatter([], [], c='lightgreen', s=100, label='Has Treatment Data'),
            plt.scatter([], [], c='lightblue', s=100, label='No Treatment Data'),
            plt.Line2D([0], [0], color='gray', linewidth=2, label='High Similarity')
        ]
        ax2.legend(handles=legend_elements, loc='upper right')
        
        plt.tight_layout()
        
        # Save network visualization
        save_path = f'{self.results_dir}/similarity_network.png'
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        print(f"📊 Similarity network saved: {save_path}")
        
        plt.show()
        plt.close()


def test_similarity_engine():
    """Test the similarity engine system"""
    
    print("🧪 TESTING SIMILARITY ENGINE SYSTEM")
    print("="*60)
    
    # Initialize engine
    engine = SimilarityEngine()
    
    # Add training patients
    print("\n📚 Adding Training Patients:")
    
    training_patients = [
        ('Patient_001', [2.8, 3.2, 1.5, 1.1, 1.3], 'Gefitinib'),
        ('Patient_002', [2.1, 1.8, 1.4, 2.9, 2.3], 'Imatinib'),
        ('Patient_003', [1.9, 3.0, 2.1, 1.2, 1.1], 'Gefitinib'),
        ('Patient_004', [2.6, 2.8, 1.3, 2.4, 2.1], 'Dasatinib'),
        ('Patient_005', [1.7, 1.5, 2.2, 1.9, 2.8], 'Imatinib'),
    ]
    
    for patient_id, genes, treatment in training_patients:
        engine.add_patient(patient_id, genes, treatment)
    
    print(f"✅ Added {len(training_patients)} training patients")
    
    # Test similarity matching
    print("\n🔍 Testing Similarity Matching:")
    
    # New patient similar to Patient_001 (high TP53, EGFR)
    new_patient_genes = [2.7, 3.1, 1.6, 1.2, 1.4]
    similar_patients = engine.find_similar_patients(new_patient_genes, "NewPatient_A")
    
    # Test treatment prediction
    print("\n💊 Testing Treatment Prediction:")
    recommendations = engine.predict_treatment_from_similarity(new_patient_genes, "NewPatient_A")
    
    # Create similarity network
    print("\n🕸️ Creating Similarity Network:")
    engine.create_similarity_network()
    
    # Test with another patient
    print("\n" + "="*60)
    print("🔍 Testing with Different Patient:")
    
    # New patient similar to Patient_002 (high MYC, RAS)
    new_patient_genes2 = [2.0, 1.7, 1.3, 2.8, 2.4]
    similar_patients2 = engine.find_similar_patients(new_patient_genes2, "NewPatient_B")
    recommendations2 = engine.predict_treatment_from_similarity(new_patient_genes2, "NewPatient_B")
    
    print("\n✅ SIMILARITY ENGINE TEST COMPLETE!")
    print("🎯 Next: Run Chunk 4 for Confidence System")
    
    return engine


if __name__ == "__main__":
    # Run the test
    similarity_engine = test_similarity_engine()
    
    print("\n" + "="*60)
    print("📝 CHUNK 3 COMPLETED SUCCESSFULLY!")
    print("="*60)
    print("✅ Similarity engine working")
    print("✅ Patient matching visualization")
    print("✅ Treatment prediction from similarity")
    print("✅ Similarity network created")
    
    print(f"\n📁 Check your results in: analysis_results/")
    print("🚀 Ready for Chunk 4: Confidence System!")
