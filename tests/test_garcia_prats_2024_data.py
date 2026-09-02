from pathlib import Path

import numpy as np
import pandas as pd

DATA = Path("data/experimental")
DOI = "10.3389/fceng.2024.1384495"


def test_garcia_prats_public_tables_preserve_design_and_provenance() -> None:
    characteristics = pd.read_csv(DATA / "garcia_prats_2024_biochar_characteristics.csv")
    context = pd.read_csv(DATA / "garcia_prats_2024_material_context.csv")
    design = pd.read_csv(DATA / "garcia_prats_2024_treatment_design.csv")

    assert set(characteristics["biochar_id"]) == {"BC1", "BC2", "BC3"}
    assert set(context["sample_id"]) == {"OFMSW_S1", "OFMSW_S2", "INOCULUM"}
    assert len(design) == 12
    assert design["n_replicates"].sum() == 36

    amended = design.query("condition_type == 'biochar_amended'")
    assert len(amended) == 9
    assert set(amended["dose_pct_ts"]) == {1, 5, 10}
    assert np.allclose(
        amended["nominal_dose_g_l"],
        amended["biochar_mass_mg"] / amended["working_volume_ml"],
        atol=1e-6,
    )

    for frame in (characteristics, context, design):
        assert frame["source_doi"].eq(DOI).all()
        assert frame["license"].eq("CC BY 4.0").all()
        assert not any("methane" in column.lower() for column in frame.columns)
