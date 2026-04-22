#!/usr/bin/env python3 """ CHUNK 5: Fixed Adaptive Learning System Add adaptive learning with real-time visualization 
(FIXED VERSION) Save as: chunk5_learning_fixed.py """ import numpy as np import pandas as pd import matplotlib.pyplot 
as plt import seaborn as sns import os from datetime import datetime # Import from previous chunks - make sure these 
files exist try:
    from chunk4_confidence_system import ConfidenceSystem print("✅ Successfully imported ConfidenceSystem") except 
ImportError as e:
    print(f"❌ Import Error: {e}") print("🔧 Creating standalone version...")

    # Create a minimal standalone version if import fails from chunk1_basic_system import BasicDigitalTwin

    class ConfidenceSystem(BasicDigitalTwin):
        def __init__(self):
            super().__init__() self.confidence_weights = {'gene_importance': 0.3, 'binding_affinity': 0.3, 
            'similarity_score': 0.2, 'historical_accuracy': 0.2} self.drug_confidence_history = {} 
            self.confidence_records = [] print("📊 Minimal Confidence System loaded")
class AdaptiveLearningSystem(ConfidenceSystem):
    """Digital twin with adaptive learning capabilities"""

    def __init__(self):
        super().__init__() print("🧠 Adaptive Learning System Module Loaded")

        # Learning components self.pattern_memory = {} self.learning_history = [] self.success_patterns = {} 
        self.failure_patterns = {} self.adaptation_count = 0

    def learn_from_outcome(self, patient_genes, drug_recommended, actual_outcome, patient_id="Patient"):
        """Learn from treatment outcome and adapt system"""

        print(f"\n🎓 LEARNING FROM TREATMENT OUTCOME") print("="*60) print(f"Patient: {patient_id}") print(f"Drug: 
        {drug_recommended}") print(f"Outcome: {actual_outcome}")

        try:
            # Create pattern signature pattern_signature = self._create_pattern_signature(patient_genes) 
            print(f"Pattern: {pattern_signature}")

            # Update pattern memory self._update_pattern_memory(pattern_signature, drug_recommended, actual_outcome)

            # Update drug confidence old_confidence = self.drug_confidence_history.get(drug_recommended, 50)

            # Simple confidence update if actual_outcome == 'success':
                new_confidence = min(95, old_confidence + 8)
            else:
                new_confidence = max(5, old_confidence - 12)
            
            self.drug_confidence_history[drug_recommended] = new_confidence
rint(f"Confidence updated: {old_confidence:.1f}% → {new_confidence:.1f}%")
                         # Record learning eventning_event = { ': datetime.now().isoformat(),
                'patient_id': patient_id, 'pattern_signature': pattern_signature, 'drug_recommended': 
                drug_recommended, 'actual_outcome': actual_outcome, 'confidence_change': new_confidence - 
                old_confidence, 'adaptation_number': self.adaptation_count
            }

            self.learning_history.append(learning_event) self.adaptation_count += 1

            # Visualize learning process self._visualize_learning_process(learning_event, patient_genes)

            print(f"✅ System adapted (Adaptation #{self.adaptation_count})")

            return learning_event

        except Exception as e:
            print(f"❌ Error in learning process: {e}") return None
         def _create_pattern_signature(self, gene_expression):eate unique pattern signature from gene expression""" 
53', 'EGFR', 'BRCA1', 'MYC', 'RAS']
        signature_parts = []

        for i, expr in enumerate(gene_expression[:5]):  # Use first 5 genes
            gene_name = genes[i] if i < len(genes) else f'GENE_{i}'

            if expr > 2.5:
                level = 'HIGH'
            elif expr > 1.5:
                level = 'MED'
            else:
                level = 'LOW'
                         signature_parts.append(f"{gene_name}_{level}")eturn "_".join(signature_parts) 
date_pattern_memory(self, pattern_signature, drug, outcome):
        """Update pattern memory with new outcome"""

        # Initialize pattern if new if pattern_signature not in self.pattern_memory:
            self.pattern_memory[pattern_signature] = {
                'success_drugs': [], 'failure_drugs': [], 'total_attempts': 0, 'success_rate': 0.0
            }
        
        # Update pattern data
attern_data = self.pattern_memory[pattern_signature]
        pattern_data['total_attempts'] += 1

        if outcome == 'success':
            pattern_data['success_drugs'].append(drug) if pattern_signature not in self.success_patterns:
                self.success_patterns[pattern_signature] = []
            self.success_patterns[pattern_signature].append(drug)
        else:
            pattern_data['failure_drugs'].append(drug) if pattern_signature not in self.failure_patterns:
                self.failure_patterns[pattern_signature] = []
            self.failure_patterns[pattern_signature].append(drug)
        
        # Update success rate
attern_data['success_drugs'])
        pattern_data['success_rate'] = successes / pattern_data['total_attempts']

        print(f"📚 Pattern memory updated:") print(f"  Success rate: {pattern_data['success_rate']:.2%}") print(f"  
        Total attempts: {pattern_data['total_attempts']}")
    
> def _visualize_learning_process(self, learning_event, patient_genes):eate learning visualization"""y:, ax2), (ax3, 
ax4)) = plt.subplots(2, 2, figsize=(16, 10)) lot 1: Learning progression
            if len(self.learning_history) > 1:
                adaptations = [e['adaptation_number'] for e in self.learning_history] conf_changes = 
                [e['confidence_change'] for e in self.learning_history]

                ax1.plot(adaptations, conf_changes, 'bo-', linewidth=2) ax1.axhline(y=0, color='gray', 
                linestyle='--', alpha=0.7) ax1.set_xlabel('Adaptation Number') ax1.set_ylabel('Confidence Change 
                (%)') ax1.set_title('Learning Progress') ax1.grid(True, alpha=0.3)

                # Highlight current current_change = learning_event['confidence_change'] current_adaptation = 
                learning_event['adaptation_number'] ax1.plot(current_adaptation, current_change, 'ro', markersize=10)
            else:
                ax1.text(0.5, 0.5, 'First Learning Event', ha='center', va='center',
                        transform=ax1.transAxes, fontsize=12)
                ax1.set_title('Learning Progress')
            
            # Plot 2: Pattern success rates
attern_memory:
                patterns = list(self.pattern_memory.keys()) success_rates = [self.pattern_memory[p]['success_rate'] 
                for p in patterns]

                # Simplify pattern names for display simple_patterns = [] for p in patterns:
                    simple = p.replace('_HIGH', '+').replace('_MED', '=').replace('_LOW', '-') simple = 
                    simple.replace('TP53', 'T').replace('EGFR', 'E').replace('BRCA1', 'B') simple = 
                    simple.replace('MYC', 'M').replace('RAS', 'R') simple_patterns.append(simple[:15])
                
>> >> colors = ['green' if sr >= 0.6 else 'orange' if sr >= 0.4 else 'red' for sr in >> 
success_rates].barh(simple_patterns, success_rates, color=colors, alpha=0.8).set_xlabel('Success >> 
Rate').set_title('Pattern Success Rates').set_xlim(0, 1).text(0.5, 0.5, 'No Patterns Yet', ha='center', 
va='center',ansform=ax2.transAxes, fontsize=12).set_title('Pattern Success Rates') lot 3: Drug confidence levels
            if self.drug_confidence_history:
                drugs = list(self.drug_confidence_history.keys()) confidences = 
                list(self.drug_confidence_history.values())

                colors = ['gold' if drug == learning_event['drug_recommended'] else 'lightblue' for drug in drugs] 
                ax3.bar(drugs, confidences, color=colors, alpha=0.8) ax3.set_ylabel('Confidence (%)') 
                ax3.set_title('Drug Confidence Levels') ax3.set_ylim(0, 100) plt.setp(ax3.get_xticklabels(), 
                rotation=45)
            else:
                ax3.text(0.5, 0.5, 'No Drug History', ha='center', va='center',
                        transform=ax3.transAxes, fontsize=12)
                ax3.set_title('Drug Confidence Levels')
            
            # Plot 4: Current patient genes
53', 'EGFR', 'BRCA1', 'MYC', 'RAS'][:len(patient_genes)]
            colors = ['red' if expr > 2.5 else 'orange' if expr > 1.5 else 'green' for expr in patient_genes]

            ax4.bar(genes, patient_genes, color=colors, alpha=0.8) ax4.axhline(y=2.0, color='red', linestyle='--', 
            alpha=0.7) ax4.set_ylabel('Expression Level') ax4.set_title(f'Patient: {learning_event["patient_id"]}')

            # Add labels for i, (gene, expr) in enumerate(zip(genes, patient_genes)):
                level = 'HIGH' if expr > 2.5 else 'MED' if expr > 1.5 else 'LOW' ax4.text(i, expr + 0.05, 
                f'{expr:.1f}\n{level}', ha='center', va='bottom', fontsize=8)
            
            outcome_emoji = '✅' if learning_event['actual_outcome'] == 'success' else '❌'
lt.suptitle(f'Learning Update {outcome_emoji} - Adaptation #{learning_event["adaptation_number"]}\n'
                        f'{learning_event["patient_id"]}: {learning_event["drug_recommended"]} → 
{learning_event["actual_outcome"]}',
                        fontsize=14, fontweight='bold')
            
            plt.tight_layout()
lot
            save_path = f'{self.results_dir}/learning_update_{learning_event["patient_id"]}.png' 
            plt.savefig(save_path, dpi=150, bbox_inches='tight') print(f"📊 Learning visualization saved: 
            {save_path}")

            plt.show() plt.close()

        except Exception as e:
            print(f"⚠️ Visualization error: {e}")
    
    def adaptive_predict(self, target_genes, target_patient_id="NewPatient"):
rediction using adaptive learning knowledge"""
        
        print(f"\n🧠 ADAPTIVE PREDICTION FOR: {target_patient_id}")
rint("="*60)
        
try:eate pattern signature for new patientget_pattern = self._create_pattern_signature(target_genes) rint(f"Target 
Pattern: {target_pattern}")
            
recommendations = []ategy 1: Exact pattern matchget_pattern in self.pattern_memory: attern_data = 
self.pattern_memory[target_pattern]
                print(f"📚 Found exact pattern match!") print(f"  Success rate: {pattern_data['success_rate']:.2%}") 
                print(f"  Total attempts: {pattern_data['total_attempts']}")

                # Recommend successful drugs from this pattern for drug in set(pattern_data['success_drugs']):  # 
                Remove duplicates
                    count = pattern_data['success_drugs'].count(drug) confidence = min(95, 
                    pattern_data['success_rate'] * 100 + count * 5)

                    recommendations.append({
                        'drug': drug, 'confidence': confidence, 'evidence': f'Exact pattern match 
                        ({count}/{pattern_data["total_attempts"]} success)', 'strategy': 'exact_match'
                    })
            
            # Strategy 2: Use general drug confidence if no exact match
rint("🔍 No exact pattern match, using general drug confidence...")
                
>>>> if self.drug_confidence_history: drug, confidence in self.drug_confidence_history.items():0:  # Only recommend 
drugs with decent confidenceecommendations.append({ug': drug,al drug confidence',ategy': 
'general_confidence'ecommendations, provide fallbackecommendations: rint("⚠️ No confident recommendations available")
                    fallback_drugs = ['Gefitinib', 'Imatinib', 'Dasatinib'] for drug in fallback_drugs:
                        recommendations.append({
                            'drug': drug, 'confidence': 50, 'evidence': 'Fallback recommendation - limited data', 
                            'strategy': 'fallback'
                        })
                         # Sort by confidenceecommendations.sort(key=lambda x: x['confidence'], reverse=True) lay 
recommendations
            self._display_adaptive_recommendations(recommendations, target_patient_id, target_pattern)

            return recommendations

        except Exception as e:
            print(f"❌ Error in adaptive prediction: {e}") return []
    
    def _display_adaptive_recommendations(self, recommendations, patient_id, pattern):
lay adaptive learning recommendations"""
        
        print(f"\n🎯 ADAPTIVE RECOMMENDATIONS FOR: {patient_id}")
rint("="*70)
        print(f"Pattern: {pattern}")

        if not recommendations:
            print("❌ No recommendations available") return
                 for i, rec in enumerate(recommendations, 1):ategy_emoji = "🎯" if rec['strategy'] == 'exact_match' 
else "📊" if rec['strategy'] == 'general_confidence' else "⚠️" rint(f"\n{i}. {rec['drug']} - {rec['confidence']:.1f}% 
Confidence")
            print(f"  {strategy_emoji} Strategy: {rec['strategy'].replace('_', ' ').title()}") print(f"  📚 Evidence: 
            {rec['evidence']}")

            # Add recommendation level if rec['confidence'] >= 80:
                print(f"  ✅ STRONGLY RECOMMENDED")
            elif rec['confidence'] >= 60:
                print(f"  ⚠️ RECOMMENDED WITH CAUTION")
            else:
                print(f"  ❌ LOW CONFIDENCE - CONSIDER ALTERNATIVES")
        
print("\n" + "="*70)ning_performance(self):ning performance""" rint(f"\n📊 LEARNING PERFORMANCE ANALYSIS")
        print("="*60)

        if not self.learning_history:
            print("⚠️ No learning history available") return {}
        
        # Basic statistics
tations = len(self.learning_history)
        successes = sum(1 for event in self.learning_history if event['actual_outcome'] == 'success') success_rate = 
        successes / total_adaptations

        print(f"Total Adaptations: {total_adaptations}") print(f"Successful Outcomes: {successes}") print(f"Overall 
        Success Rate: {success_rate:.2%}") print(f"Patterns Learned: {len(self.pattern_memory)}") print(f"Drugs 
        Tracked: {len(self.drug_confidence_history)}")

        # Recent performance if total_adaptations >= 3:
            recent_events = self.learning_history[-3:] recent_successes = sum(1 for event in recent_events if 
            event['actual_outcome'] == 'success') recent_success_rate = recent_successes / len(recent_events)

            print(f"\nRecent Performance (last 3):") print(f"  Success Rate: {recent_success_rate:.2%}")

            if recent_success_rate > success_rate:
                print(f"  📈 IMPROVING - System is learning")
            elif recent_success_rate < success_rate:
                print(f"  📉 DECLINING - May need more data")
            else:
                print(f"  ➡️ STABLE - Consistent performance")
        
        return {
tations': total_adaptations,
            'success_rate': success_rate, 'patterns_learned': len(self.pattern_memory), 'drugs_tracked': 
            len(self.drug_confidence_history)
        } def test_adaptive_learning():
    """Test the adaptive learning system"""

    print("🧪 TESTING ADAPTIVE LEARNING SYSTEM") print("="*60)

    try:
        # Initialize system learning_system = AdaptiveLearningSystem()

        # Add some basic patients first print("\n📚 Adding Basic Patients:")

        basic_patients = [
            ('Patient_001', [2.8, 3.2, 1.5, 1.1, 1.3], 'Gefitinib'), ('Patient_002', [2.1, 1.8, 1.4, 2.9, 2.3], 
            'Imatinib'), ('Patient_003', [1.9, 3.0, 2.1, 1.2, 1.1], 'Gefitinib'),
        ]

        for patient_id, genes, treatment in basic_patients:
            learning_system.add_patient(patient_id, genes, treatment)
                 print(f"✅ Added {len(basic_patients)} basic patients")ning from outcomes rint("\n🎓 Testing 
Learning from Outcomes:")
        
        learning_scenarios = [
atient_001', [2.8, 3.2, 1.5, 1.1, 1.3], 'Gefitinib', 'success'),
            ('Patient_002', [2.1, 1.8, 1.4, 2.9, 2.3], 'Imatinib', 'success'), ('Patient_004', [2.7, 3.1, 1.6, 1.2, 
            1.4], 'Gefitinib', 'success'), # Similar to P001 ('Patient_005', [2.0, 1.7, 1.3, 2.8, 2.4], 'Imatinib', 
            'failure'), # Similar to P002 but failed
        ]

        for patient_id, genes, drug, outcome in learning_scenarios:
            print(f"\n--- Learning from {patient_id} ---") learning_event = learning_system.learn_from_outcome(genes, 
            drug, outcome, patient_id) if learning_event:
                print(f"✅ Learning successful")
            else:
                print(f"❌ Learning failed")
        
        # Test adaptive prediction
rint("\n🧠 Testing Adaptive Prediction:")
        
> > # Test patient similar to successful Gefitinib cases = [2.9, 3.0, 1.7, 1.3, 1.2]ecommendations1 = 
learning_system.adaptive_predict(test_genes1, "AdaptiveTest_A") atient similar to patterns we've seen
        print("\n" + "="*60) test_genes2 = [2.0, 1.8, 1.4, 2.7, 2.5] recommendations2 = 
        learning_system.adaptive_predict(test_genes2, "AdaptiveTest_B")

        # Analyze performance print("\n📊 Analyzing Learning Performance:") performance = 
        learning_system.analyze_learning_performance()

        print("\n✅ ADAPTIVE LEARNING TEST COMPLETE!") print("🎯 System working and learning from outcomes")

        return learning_system

    except Exception as e:
        print(f"❌ Error in testing: {e}") import traceback traceback.print_exc() return None if __name__ == 
"__main__":
    # Run the test learning_system = test_adaptive_learning()

    if learning_system:
        print("\n" + "="*60) print("📝 CHUNK 5 COMPLETED SUCCESSFULLY!") print("="*60) print("✅ Adaptive learning 
        system working") print("✅ Pattern memory and recognition") print("✅ Learning from treatment outcomes") 
        print("✅ Adaptive prediction capabilities") print("✅ Learning performance analysis")

        print(f"\n📁 Check your results in: analysis_results/") print("🚀 Ready for Chunk 6: Complete System Demo!")
    else:
        print("\n❌ CHUNK 5 FAILED - Check error messages above")
        print("🔧 Try running chunks 1-4 first to ensure dependencies are available")
