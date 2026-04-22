#!/usr/bin/env python3
"""
CHUNK 1: Basic System Foundation
Create the core digital twin class with basic functionality

Save as: chunk1_basic_system.py
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os
from datetime import datetime

class BasicDigitalTwin:
    """Foundation class for the cancer digital twin"""
    
    def __init__(self):
        print("🚀 Initializing Basic Digital Twin System")
        
        # Core data storage
        self.patients_db = pd.DataFrame()
        self.outcomes_db = {}
        self.system_stats = {
            'patients_added': 0,
            'outcomes_recorded': 0,
            'creation_time': datetime.now().isoformat()
        }
        
        # Create results directory
        self.results_dir = "analysis_results"
        os.makedirs(self.results_dir, exist_ok=True)
        
        print(f"✅ System initialized")
        print(f"📁 Results directory: {self.results_dir}/")
    
    def add_patient(self, patient_id, gene_expression, treatment_outcome=None):
        """Add a new patient to the system database"""
        
        print(f"\n👤 Adding Patient: {patient_id}")
        print(f"🧬 Gene Expression: {gene_expression}")
        
        # Convert to DataFrame and add to database
        gene_df = pd.DataFrame([gene_expression], index=[patient_id])
        self.patients_db = pd.concat([self.patients_db, gene_df], sort=False)
        
        # Store outcome if provided
        if treatment_outcome:
            self.outcomes_db[patient_id] = treatment_outcome
            self.system_stats['outcomes_recorded'] += 1
            print(f"💊 Treatment Outcome: {treatment_outcome}")
        
        self.system_stats['patients_added'] += 1
        print(f"✅ Patient {patient_id} added successfully")
        
        # Show simple gene profile
        self._show_gene_profile(patient_id, gene_expression)
        
        return True
    
    def _show_gene_profile(self, patient_id, gene_expression):
        """Display basic gene expression profile"""
        
        genes = ['TP53', 'EGFR', 'BRCA1', 'MYC', 'RAS']
        
        print(f"\n📊 Gene Expression Profile for {patient_id}:")
        print("-" * 40)
        
        for i, (gene, expr) in enumerate(zip(genes[:len(gene_expression)], gene_expression)):
            status = "HIGH" if expr > 2.0 else "NORMAL"
            emoji = "🔴" if expr > 2.0 else "🟢"
            print(f"{emoji} {gene}: {expr:.1f}x ({status})")
        
        print("-" * 40)
    
    def show_database_summary(self):
        """Display current database status"""
        
        print(f"\n📈 DATABASE SUMMARY")
        print("=" * 50)
        print(f"Total Patients: {len(self.patients_db)}")
        print(f"Patients with Outcomes: {len(self.outcomes_db)}")
        print(f"System Created: {self.system_stats['creation_time'][:19]}")
        
        if len(self.patients_db) > 0:
            print(f"\n👥 Patient List:")
            for patient_id in self.patients_db.index:
                outcome = self.outcomes_db.get(patient_id, "Unknown")
                print(f"   • {patient_id}: {outcome}")
        
        print("=" * 50)
    
    def create_basic_visualization(self):
        """Create basic visualization of patient data"""
        
        if len(self.patients_db) == 0:
            print("⚠️ No patients to visualize yet")
            return
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
        
        # Plot 1: Gene expression heatmap
        if len(self.patients_db) > 0:
            # Transpose for better visualization (patients as columns, genes as rows)
            data_for_heatmap = self.patients_db.T
            
            im = ax1.imshow(data_for_heatmap.values, cmap='RdYlBu_r', aspect='auto')
            
            # Labels
            ax1.set_xticks(range(len(self.patients_db.index)))
            ax1.set_xticklabels(self.patients_db.index, rotation=45)
            ax1.set_yticks(range(len(data_for_heatmap.index)))
            ax1.set_yticklabels(['Gene1', 'Gene2', 'Gene3', 'Gene4', 'Gene5'][:len(data_for_heatmap.index)])
            ax1.set_title('Patient Gene Expression Heatmap')
            
            # Add colorbar
            plt.colorbar(im, ax=ax1, label='Expression Level')
        
        # Plot 2: Outcome distribution
        if self.outcomes_db:
            outcomes = list(self.outcomes_db.values())
            outcome_counts = {}
            for outcome in outcomes:
                outcome_counts[outcome] = outcome_counts.get(outcome, 0) + 1
            
            if outcome_counts:
                drugs = list(outcome_counts.keys())
                counts = list(outcome_counts.values())
                
                ax2.pie(counts, labels=drugs, autopct='%1.1f%%', startangle=90)
                ax2.set_title('Treatment Distribution')
        else:
            ax2.text(0.5, 0.5, 'No Treatment Data\nAvailable Yet', 
                    ha='center', va='center', transform=ax2.transAxes, fontsize=12)
            ax2.set_title('Treatment Distribution')
        
        plt.tight_layout()
        plt.suptitle('Basic Digital Twin - Patient Database Overview', fontsize=14, y=1.02)
        
        # Save plot
        save_path = f'{self.results_dir}/basic_database_overview.png'
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        print(f"📊 Visualization saved: {save_path}")
        
        plt.show()
        plt.close()


def test_basic_system():
    """Test the basic digital twin system"""
    
    print("🧪 TESTING BASIC DIGITAL TWIN SYSTEM")
    print("="*60)
    
    # Initialize system
    twin = BasicDigitalTwin()
    
    # Add some test patients
    print("\n📚 Adding Test Patients:")
    
    test_patients = [
        ('P001', [2.8, 3.2, 1.5, 1.1, 1.3], 'Gefitinib'),
        ('P002', [2.1, 1.8, 1.4, 2.9, 2.3], 'Imatinib'),
        ('P003', [1.9, 3.0, 2.1, 1.2, 1.1], 'Gefitinib'),
    ]
    
    for patient_id, genes, treatment in test_patients:
        twin.add_patient(patient_id, genes, treatment)
        print()  # Add space between patients
    
    # Show database summary
    twin.show_database_summary()
    
    # Create visualization
    print("\n🎨 Creating Basic Visualization...")
    twin.create_basic_visualization()
    
    print("\n✅ BASIC SYSTEM TEST COMPLETE!")
    print("🎯 Next: Run Chunk 2 for Patient Analysis")
    
    return twin


if __name__ == "__main__":
    # Run the test
    digital_twin = test_basic_system()
    
    print("\n" + "="*60)
    print("📝 CHUNK 1 COMPLETED SUCCESSFULLY!")
    print("="*60)
    print("✅ Basic digital twin system working")
    print("✅ Patient database functional")  
    print("✅ Basic visualization created")
    print("✅ Foundation ready for advanced features")
    
    print(f"\n📁 Check your results in: analysis_results/")
    print("🚀 Ready for Chunk 2: Patient Analysis!")
