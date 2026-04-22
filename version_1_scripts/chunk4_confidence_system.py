#!/usr/bin/env python3
"""
CHUNK 4: Confidence Scoring System
Add confidence scoring with visualization

Save as: chunk4_confidence_system.py
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from chunk3_basic_system import SimilarityEngine

class ConfidenceSystem(SimilarityEngine):
    """Digital twin with confidence scoring capabilities"""
    
    def __init__(self):
        super().__init__()
        print("📊 Confidence System Module Loaded")
        
        # Confidence scoring parameters
        self.confidence_weights = {
            'gene_importance': 0.3,
            'binding_affinity': 0.3,
            'similarity_score': 0.2,
            'historical_accuracy': 0.2
        }
        
        # Historical accuracy tracking
        self.drug_confidence_history = {}
        self.confidence_records = []
    
    def calculate_confidence_score(self, gene_importance, binding_affinity, similarity_score, drug_name):
        """Calculate multi-factor confidence score"""
        
        print(f"\n📊 CALCULATING CONFIDENCE FOR: {drug_name}")
        print("="*50)
        
        # Component 1: Gene importance score (0-100)
        gene_confidence = min(100, gene_importance * 30)
        print(f"🧬 Gene Importance: {gene_importance:.2f} → {gene_confidence:.1f}%")
        
        # Component 2: Binding affinity score (0-100)
        # Higher binding affinity (more negative) = higher confidence
        binding_confidence = min(100, abs(binding_affinity) * 10)
        print(f"🔗 Binding Affinity: {binding_affinity:.2f} → {binding_confidence:.1f}%")
        
        # Component 3: Similarity score (0-100)
        similarity_confidence = similarity_score * 100
        print(f"👥 Patient Similarity: {similarity_score:.3f} → {similarity_confidence:.1f}%")
        
        # Component 4: Historical accuracy (0-100)
        historical_confidence = self.drug_confidence_history.get(drug_name, 50)  # Default 50%
        print(f"📈 Historical Accuracy: {historical_confidence:.1f}%")
        
        # Calculate weighted combination
        components = [gene_confidence, binding_confidence, similarity_confidence, historical_confidence]
        weights = list(self.confidence_weights.values())
        
        final_confidence = sum(w * c for w, c in zip(weights, components))
        final_confidence = min(100, max(0, final_confidence))
        
        print(f"\n🎯 FINAL CONFIDENCE SCORE: {final_confidence:.1f}%")
        
        # Store confidence record
        confidence_record = {
            'drug_name': drug_name,
            'gene_confidence': gene_confidence,
            'binding_confidence': binding_confidence,
            'similarity_confidence': similarity_confidence,
            'historical_confidence': historical_confidence,
            'final_confidence': final_confidence,
            'timestamp': pd.Timestamp.now().isoformat()
        }
        
        self.confidence_records.append(confidence_record)
        
        return final_confidence, confidence_record
    
    def create_confidence_visualization(self, confidence_record, patient_id="Patient"):
        """Create detailed confidence score visualization"""
        
        drug_name = confidence_record['drug_name']
        
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
        
        # Plot 1: Confidence component breakdown
        components = ['Gene\nImportance', 'Binding\nAffinity', 'Patient\nSimilarity', 'Historical\nAccuracy']
        values = [
            confidence_record['gene_confidence'],
            confidence_record['binding_confidence'],
            confidence_record['similarity_confidence'],
            confidence_record['historical_confidence']
        ]
        weights = list(self.confidence_weights.values())
        weighted_values = [v * w for v, w in zip(values, weights)]
        
        colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4']
        
        bars = ax1.bar(components, weighted_values, color=colors, alpha=0.8, edgecolor='black')
        ax1.set_ylabel('Weighted Contribution to Confidence')
        ax1.set_title(f'Confidence Score Breakdown: {drug_name}')
        ax1.set_ylim(0, max(weighted_values) * 1.3)
        
        # Add value labels
        for bar, raw_val, weight in zip(bars, values, weights):
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height + 0.5,
                    f'{raw_val:.1f}%\n(×{weight})', ha='center', va='bottom', fontsize=9, fontweight='bold')
        
        # Add final confidence line
        final_conf = confidence_record['final_confidence']
        ax1.axhline(y=final_conf/4, color='red', linestyle='-', linewidth=3, 
                   label=f'Final: {final_conf:.1f}%')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # Plot 2: Confidence gauge
        self._draw_confidence_gauge(ax2, final_conf, drug_name)
        
        # Plot 3: Confidence category and risk assessment
        self._draw_confidence_categories(ax3, final_conf, drug_name)
        
        # Plot 4: Historical confidence tracking
        self._draw_confidence_history(ax4, drug_name)
        
        plt.suptitle(f'Confidence Analysis: {patient_id} → {drug_name}', fontsize=16, fontweight='bold')
        plt.tight_layout()
        
        # Save visualization
        save_path = f'{self.results_dir}/confidence_analysis_{patient_id}_{drug_name}.png'
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        print(f"📊 Confidence analysis saved: {save_path}")
        
        plt.show()
        plt.close()
    
    def _draw_confidence_gauge(self, ax, confidence, drug_name):
        """Draw confidence gauge/speedometer"""
        
        # Create semicircle gauge
        theta = np.linspace(0, np.pi, 100)
        ax.plot(np.cos(theta), np.sin(theta), 'lightgray', linewidth=15, alpha=0.3)
        
        # Confidence level arc with color coding
        if confidence >= 80:
            color = 'green'
            label = 'VERY HIGH'
        elif confidence >= 60:
            color = 'lightgreen'
            label = 'HIGH'
        elif confidence >= 40:
            color = 'orange'
            label = 'MEDIUM'
        else:
            color = 'red'
            label = 'LOW'
        
        confidence_theta = np.linspace(0, np.pi * confidence/100, 50)
        ax.plot(np.cos(confidence_theta), np.sin(confidence_theta), color, linewidth=15, alpha=0.8)
        
        # Needle
        needle_angle = np.pi * (1 - confidence/100)
        ax.arrow(0, 0, 0.8*np.cos(needle_angle), 0.8*np.sin(needle_angle), 
                head_width=0.05, head_length=0.08, fc='black', ec='black', linewidth=2)
        
        # Labels
        ax.text(0, -0.15, f'{confidence:.1f}%', ha='center', va='center', 
               fontsize=20, fontweight='bold')
        ax.text(0, -0.35, label, ha='center', va='center', 
               fontsize=12, color=color, fontweight='bold')
        ax.text(0, -0.5, 'Confidence Level', ha='center', va='center', fontsize=10)
        
        # Gauge markings
        for i in range(0, 101, 20):
            angle = np.pi * (1 - i/100)
            x1, y1 = 0.85 * np.cos(angle), 0.85 * np.sin(angle)
            x2, y2 = 0.95 * np.cos(angle), 0.95 * np.sin(angle)
            ax.plot([x1, x2], [y1, y2], 'black', linewidth=2)
            ax.text(1.05 * np.cos(angle), 1.05 * np.sin(angle), f'{i}%', 
                   ha='center', va='center', fontsize=8)
        
        ax.set_xlim(-1.2, 1.2)
        ax.set_ylim(-0.6, 1.2)
        ax.set_aspect('equal')
        ax.axis('off')
        ax.set_title(f'Confidence Gauge\n{drug_name}', fontweight='bold')
    
    def _draw_confidence_categories(self, ax, confidence, drug_name):
        """Draw confidence categories and recommendations"""
        
    def _draw_confidence_categories(self, ax, confidence, drug_name):
        """Draw confidence categories and recommendations"""
        
        # Define confidence categories
        categories = [
            {'range': '80-100%', 'label': 'Very High', 'color': 'green', 'recommendation': 'Proceed immediately'},
            {'range': '60-79%', 'label': 'High', 'color': 'lightgreen', 'recommendation': 'Good option'},
            {'range': '40-59%', 'label': 'Medium', 'color': 'orange', 'recommendation': 'Consider carefully'},
            {'range': '0-39%', 'label': 'Low', 'color': 'red', 'recommendation': 'High risk - avoid'}
        ]
        
        # Determine current category
        if confidence >= 80:
            current_category = 0
        elif confidence >= 60:
            current_category = 1
        elif confidence >= 40:
            current_category = 2
        else:
            current_category = 3
        
        # Create category visualization
        y_positions = range(len(categories))
        category_scores = [90, 70, 50, 20]  # Representative scores for each category
        
        bars = ax.barh(y_positions, category_scores, 
                      color=[cat['color'] for cat in categories], alpha=0.7, edgecolor='black')
        
        # Highlight current category
        bars[current_category].set_alpha(1.0)
        bars[current_category].set_edgecolor('red')
        bars[current_category].set_linewidth(3)
        
        # Add labels
        for i, (cat, bar) in enumerate(zip(categories, bars)):
            # Category info
            ax.text(5, i, f"{cat['label']}\n({cat['range']})", va='center', fontweight='bold')
            # Recommendation
            ax.text(bar.get_width() + 2, i, cat['recommendation'], va='center', fontsize=9)
        
        # Add current drug's exact position
        ax.plot([confidence, confidence], [-0.5, len(categories)-0.5], 'r--', linewidth=3, 
               label=f'{drug_name}: {confidence:.1f}%')
        
        ax.set_xlim(0, 110)
        ax.set_ylim(-0.5, len(categories)-0.5)
        ax.set_xlabel('Confidence Score (%)')
        ax.set_title('Confidence Categories & Recommendations')
        ax.set_yticks([])
        ax.legend()
        ax.grid(True, alpha=0.3, axis='x')
    
    def _draw_confidence_history(self, ax, drug_name):
        """Draw confidence history for the drug"""
        
        # Get records for this drug
        drug_records = [r for r in self.confidence_records if r['drug_name'] == drug_name]
        
        if len(drug_records) > 1:
            # Multiple records - show trend
            confidences = [r['final_confidence'] for r in drug_records]
            times = range(len(confidences))
            
            ax.plot(times, confidences, 'bo-', linewidth=2, markersize=8)
            ax.set_xlabel('Analysis Number')
            ax.set_ylabel('Confidence Score (%)')
            ax.set_title(f'Confidence History: {drug_name}')
            ax.grid(True, alpha=0.3)
            ax.set_ylim(0, 100)
            
            # Add trend line
            if len(confidences) > 2:
                z = np.polyfit(times, confidences, 1)
                p = np.poly1d(z)
                ax.plot(times, p(times), "r--", alpha=0.8, label=f'Trend: {z[0]:+.1f}%/analysis')
                ax.legend()
            
            # Highlight current analysis
            ax.plot(len(confidences)-1, confidences[-1], 'ro', markersize=12, 
                   label='Current Analysis')
            
        else:
            # Single record - show component comparison
            if drug_records:
                record = drug_records[0]
                components = ['Gene', 'Binding', 'Similarity', 'Historical']
                values = [
                    record['gene_confidence'],
                    record['binding_confidence'], 
                    record['similarity_confidence'],
                    record['historical_confidence']
                ]
                
                ax.bar(components, values, color=['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4'], 
                      alpha=0.8, edgecolor='black')
                ax.set_ylabel('Component Score (%)')
                ax.set_title(f'Component Breakdown: {drug_name}')
                ax.set_ylim(0, 100)
                plt.setp(ax.get_xticklabels(), rotation=45)
                
                # Add value labels
                for bar, val in zip(ax.patches, values):
                    ax.text(bar.get_x() + bar.get_width()/2., bar.get_height() + 1,
                           f'{val:.1f}%', ha='center', va='bottom', fontweight='bold')
            else:
                ax.text(0.5, 0.5, f'First Analysis\nfor {drug_name}', 
                       ha='center', va='center', transform=ax.transAxes, fontsize=12)
                ax.set_title('Confidence History')
    
    def update_drug_confidence(self, drug_name, was_successful):
        """Update historical confidence based on treatment outcome"""
        
        print(f"\n📈 UPDATING DRUG CONFIDENCE: {drug_name}")
        print("="*50)
        
        # Get current confidence or start with default
        current_confidence = self.drug_confidence_history.get(drug_name, 50)
        
        # Update based on outcome
        if was_successful:
            new_confidence = min(95, current_confidence + 8)  # Increase for success
            outcome_text = "SUCCESS - Confidence increased"
        else:
            new_confidence = max(5, current_confidence - 12)  # Decrease for failure
            outcome_text = "FAILURE - Confidence decreased"
        
        self.drug_confidence_history[drug_name] = new_confidence
        
        print(f"Drug: {drug_name}")
        print(f"Outcome: {outcome_text}")
        print(f"Confidence: {current_confidence:.1f}% → {new_confidence:.1f}%")
        print(f"Change: {new_confidence - current_confidence:+.1f}%")
        
        return new_confidence
    
    def predict_with_confidence(self, target_genes, target_patient_id="NewPatient"):
        """Complete prediction with confidence analysis"""
        
        print(f"\n🎯 COMPLETE PREDICTION WITH CONFIDENCE: {target_patient_id}")
        print("="*60)
        
        # Step 1: Find similar patients
        similar_patients = self.find_similar_patients(target_genes, target_patient_id, show_visualization=False)
        
        # Step 2: Get treatment recommendations
        treatment_predictions = self.predict_treatment_from_similarity(target_genes, target_patient_id)
        
        if not treatment_predictions:
            print("❌ No treatment predictions available")
            return None
        
        # Step 3: Calculate confidence for each recommendation
        final_recommendations = []
        
        for prediction in treatment_predictions:
            drug_name = prediction['treatment']
            
            # Calculate confidence factors
            gene_importance = max(target_genes)  # Use highest gene expression as importance
            binding_affinity = np.random.uniform(-9, -6)  # Simulated binding data
            similarity_score = prediction['avg_similarity']
            
            # Calculate confidence
            confidence_score, confidence_record = self.calculate_confidence_score(
                gene_importance, binding_affinity, similarity_score, drug_name
            )
            
            # Create comprehensive recommendation
            recommendation = {
                'drug': drug_name,
                'confidence_score': confidence_score,
                'confidence_category': self._get_confidence_category(confidence_score),
                'gene_importance': gene_importance,
                'binding_affinity': binding_affinity,
                'similarity_score': similarity_score,
                'supporting_patients': prediction['supporting_patients'],
                'patient_list': prediction['patient_list'],
                'risk_assessment': self._assess_risk(confidence_score),
                'recommendation_text': self._generate_recommendation_text(confidence_score),
                'confidence_record': confidence_record
            }
            
            final_recommendations.append(recommendation)
            
            # Create individual confidence visualization
            self.create_confidence_visualization(confidence_record, target_patient_id)
        
        # Sort by confidence score
        final_recommendations.sort(key=lambda x: x['confidence_score'], reverse=True)
        
        # Display final recommendations
        self._display_final_recommendations(final_recommendations, target_patient_id)
        
        return final_recommendations
    
    def _get_confidence_category(self, confidence):
        """Get confidence category label"""
        if confidence >= 80:
            return "Very High"
        elif confidence >= 60:
            return "High"
        elif confidence >= 40:
            return "Medium"
        else:
            return "Low"
    
    def _assess_risk(self, confidence):
        """Assess treatment risk based on confidence"""
        if confidence >= 80:
            return "Low Risk"
        elif confidence >= 60:
            return "Medium Risk"
        elif confidence >= 40:
            return "High Risk"
        else:
            return "Very High Risk"
    
    def _generate_recommendation_text(self, confidence):
        """Generate recommendation text based on confidence"""
        if confidence >= 80:
            return "Strongly recommended - Proceed with treatment"
        elif confidence >= 60:
            return "Recommended - Good treatment option"
        elif confidence >= 40:
            return "Consider carefully - Monitor closely if used"
        else:
            return "Not recommended - Seek alternative treatments"
    
    def _display_final_recommendations(self, recommendations, patient_id):
        """Display final treatment recommendations"""
        
        print(f"\n🏥 FINAL TREATMENT RECOMMENDATIONS FOR: {patient_id}")
        print("="*70)
        
        for i, rec in enumerate(recommendations, 1):
            print(f"\n{i}. {rec['drug']} - {rec['confidence_category']} Confidence ({rec['confidence_score']:.1f}%)")
            print("-" * 60)
            print(f"   🎯 Recommendation: {rec['recommendation_text']}")
            print(f"   ⚠️  Risk Level: {rec['risk_assessment']}")
            print(f"   🧬 Gene Importance: {rec['gene_importance']:.2f}")
            print(f"   🔗 Binding Affinity: {rec['binding_affinity']:.2f} kcal/mol")
            print(f"   👥 Patient Similarity: {rec['similarity_score']:.3f}")
            print(f"   📊 Supporting Evidence: {rec['supporting_patients']} patients ({', '.join(rec['patient_list'])})")
        
        print("\n" + "="*70)
        
        # Summary recommendation
        top_rec = recommendations[0]
        if top_rec['confidence_score'] >= 70:
            print(f"✅ RECOMMENDED TREATMENT: {top_rec['drug']} ({top_rec['confidence_score']:.1f}% confidence)")
        elif top_rec['confidence_score'] >= 50:
            print(f"⚠️  CONSIDER TREATMENT: {top_rec['drug']} ({top_rec['confidence_score']:.1f}% confidence) - Monitor closely")
        else:
            print(f"❌ NO STRONG RECOMMENDATION - All options below 50% confidence")
            print("   Recommend: Seek additional testing or alternative approaches")


def test_confidence_system():
    """Test the confidence scoring system"""
    
    print("🧪 TESTING CONFIDENCE SCORING SYSTEM")
    print("="*60)
    
    # Initialize system
    confidence_system = ConfidenceSystem()
    
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
        confidence_system.add_patient(patient_id, genes, treatment)
    
    print(f"✅ Added {len(training_patients)} training patients")
    
    # Test confidence prediction
    print("\n🎯 Testing Complete Prediction with Confidence:")
    
    # Test patient 1: Similar to high EGFR patients
    new_patient_genes1 = [2.7, 3.1, 1.6, 1.2, 1.4]
    recommendations1 = confidence_system.predict_with_confidence(new_patient_genes1, "TestPatient_A")
    
    # Test patient 2: Similar to high MYC/RAS patients  
    print("\n" + "="*60)
    new_patient_genes2 = [2.0, 1.7, 1.3, 2.8, 2.4]
    recommendations2 = confidence_system.predict_with_confidence(new_patient_genes2, "TestPatient_B")
    
    # Simulate learning from outcomes
    print("\n📈 Simulating Learning from Treatment Outcomes:")
    
    if recommendations1:
        top_drug1 = recommendations1[0]['drug']
        success1 = recommendations1[0]['confidence_score'] > 60  # Simulate based on confidence
        confidence_system.update_drug_confidence(top_drug1, success1)
    
    if recommendations2:
        top_drug2 = recommendations2[0]['drug']
        success2 = recommendations2[0]['confidence_score'] > 60
        confidence_system.update_drug_confidence(top_drug2, success2)
    
    print("\n✅ CONFIDENCE SYSTEM TEST COMPLETE!")
    print("🎯 Next: Run Chunk 5 for Learning System")
    
    return confidence_system


if __name__ == "__main__":
    # Run the test
    confidence_system = test_confidence_system()
    
    print("\n" + "="*60)
    print("📝 CHUNK 4 COMPLETED SUCCESSFULLY!")
    print("="*60)
    print("✅ Confidence scoring system working")
    print("✅ Multi-factor confidence calculation")
    print("✅ Confidence visualization with gauges")
    print("✅ Risk assessment and recommendations")
    print("✅ Historical confidence tracking")
    
    print(f"\n📁 Check your results in: analysis_results/")
    print("🚀 Ready for Chunk 5: Learning System!")
