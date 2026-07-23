#!/usr/bin/env python3
"""Run full eyeglasses-hypothesis validation pipeline."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SCRIPTS = [
    "00_sync_downloads.py",
    "01a_fetch_external_data.py",
    "01d_fetch_expansion_data.py",
    "01c_process_geonames.py",
    "01_fetch_istc.py",
    "01b_process_istc_holdings.py",
    "02_fetch_rete.py",
    "02a_fetch_rete_api.py",
    "02a_fetch_rete_institutions.py",
    "02a_fetch_rete_activities.py",
    "02e_process_stelter.py",
    "02f_process_manuscripts.py",
    "02g_process_human_accomplishment.py",
    "02h_process_wiag.py",
    "02n_process_wiag_domherren.py",
    "02o_process_rag.py",
    "02p_process_bologna_knod.py",
    "02q_process_mmm.py",
    "02r_process_bhotmg.py",
    "02s_process_leuven.py",
    "02t_process_utrecht.py",
    "02u_fetch_studium.py",
    "02v_process_studium.py",
    "02w_process_scholar_age_tests.py",
    "02ab_parse_ilardi_florence_makers.py",
    "02y_process_ilardi_orders.py",
    "02x_process_spectacle_adoption.py",
    "02z_process_london_customs_spectacles.py",
    "02y_process_sdbm.py",
    "02i_process_owid_extras.py",
    "02j_process_wikidata.py",
    "02k_process_europop.py",
    "02l_process_pantheon.py",
    "02m_process_patentcity.py",
    "02aa_process_age_at_work.py",
    "01f_enrich_age_at_work_birthplace.py",
    # re-process glass×age tests after P19 enrich (idempotent if birthplaces.json present)
    "02aa_process_age_at_work.py",
    "02d_process_rete_activities.py",
    "02c_process_rete_individual.py",
    "02b_process_cdmv_extras.py",
    "03_build_panel.py",
    "04_run_timeseries.py",
    "05_run_regressions.py",
    "06_run_counterfactual.py",
    "08_run_robustness.py",
    "09_power_and_sensitivity.py",
    "10_studium_sample_audit.py",
    "11_city_leaveoneout_permute.py",
    "12_data_provenance.py",
    "13_wikidata_p800_audit.py",
    "14_equivalence_ci.py",
    "15_b1_wearer_offline_expand.py",
    "07_synthesis.py",
]


def main() -> None:
    for script in SCRIPTS:
        path = ROOT / script
        print(f"\n{'='*60}\nRunning {script}\n{'='*60}")
        result = subprocess.run([sys.executable, str(path)], cwd=str(ROOT))
        if result.returncode != 0:
            print(f"FAILED: {script}")
            sys.exit(result.returncode)
    print("\nPipeline complete. See outputs/tables/")


if __name__ == "__main__":
    main()
