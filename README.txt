
📄 README.md（最终版）

When Regulation Divides  An Empirically Calibrated Agent-Based Model of Trust Polarization in a Personal Pension System

This repository contains the source code for the agent-based model described in the manuscript:  
"When Regulation Divides: An Empirically Calibrated Agent-Based Model of Trust Polarization in a Personal Pension System", submitted to theJournal of Artificial Societies and Social Simulation (JASSS).

The model demonstrates how heterogeneous perceptions of regulatory policy—calibrated from empirical survey data on latent class analysis (LCA)—interact with social network structures to generate a paradoxical outcome: macro-level stability in pension participation coexisting with micro-level polarization in trust following a negative regulatory shock.

📁 Repository Structure

.
├── model.py                 # Main model class (PensionModel)
├── agent.py                 # Agent definition (PensionAgent)
├── robustness_check.py      # Script to run multi-network robustness analysis (generates Table 1)
├── requirements.txt         # Python dependencies
├── results/                 # (Optional) Sample output directory
│   └── table1_robustness.csv
└── README.md                # This file
├── data/
│   └── agent_params_ready_for_abm.csv  # Empirically calibrated agent parameters from a Feb 2026 survey (N=526), derived via Latent Class Analysis (LCA)

⚙️ Requirements

Python 3.8 or higher
Required packages (see requirements.txt):
  mesa>=0.9.4
  networkx>=2.8
  pandas>=1.5
  numpy>=1.21

Install dependencies via:
bash
pip install -r requirements.txt

▶️ How to Run

Reproduce Table 1: Robustness across network topologies
This script runs the model on small-world, random, and scale-free networks and saves aggregated participation rates to results/table1_robustness.csv.

bash
python robustness_check.py

Output:  
results/table1_robustness.csv: Steady-state participation rates (%) by sensitivity group and network type (reported at step 24).  
Console logs showing progress for each network configuration.

📊 Expected Results

Running robustness_check.py should produce a CSV file matching Table 1 in the manuscript:
Network Type            Aggregate Participation (%)   Negative Group (%)   Positive Group (%)
Small-world (p=0.1)     ~94.7                         ~87.2                100.0

Random                  ~96.0                         ~90.4                100.0

Scale-free (m=2)        ~94.5                         ~86.7                100.0

These results confirm that the stability–polarization duality is robust to network structure.

## 📊 Data Source and Calibration

The model is initialized using individual-level parameters from a national survey on personal pension participation conducted in **February 2026** (N = 526). 

- **Policy sensitivity groups** (`reg_sensitivity`: -1, 0, 1) were identified via **Latent Class Analysis (LCA)** of respondents' attitudes toward regulatory policies.
- The file `data/agent_params_ready_for_abm.csv` contains one row per agent, with columns for:
  - Demographics (`age`, `gender`, `income_level`, `education`)
  - Behavioral traits (`initial_trust`, `loss_tolerance`)
  - Social influence weights (`weight_strong_tie`, `weight_weak_tie`, etc.)
  - Group membership (`reg_sensitivity`)

> 🔒 **Note**: Raw questionnaire responses are not shared due to privacy restrictions. However, this calibrated dataset contains all information necessary to reproduce the agent heterogeneity in the model.

📜 License

This work is licensed under the MIT License — see LICENSE for details.

Copyright (c) 2026 [XU Jie]

📬 Citation & Archiving

DOI: https://doi.org/10.5281/zenodo.xxxxxxx  
 (Replace with your Zenodo DOI after archiving)
Repository: https://github.com/[your-username]/pension-trust-abm

If you use this model in your research, please cite our manuscript:

[XU Jie]. (2026). When Regulation Divides: An Empirically Calibrated Agent-Based Model of Trust Polarization in a Personal Pension System.Journal of Artificial Societies and Social Simulation, forthcoming.

👤 Authors

[XU Jie] – [Shanghai Advanced Institute of Finance (SAIF), Shanghai Jiaotong Uinversity] – Jxu2@saif.sjtu.edu.cn


