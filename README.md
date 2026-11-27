# BIC Explorer — Interactive Electromagnetic Research Lab

A standalone, confidentiality-safe Streamlit research and teaching application accompanying the 2026 postdoctoral project at the Instituto de Física, UASLP. Models and dimensions are generic or synthetic. It does not demonstrate a BIC in the research system or claim institutional endorsement.

## Run locally

Python 3.11 or 3.12 is recommended. From this directory:

```sh
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

Run `pytest -q` from this directory. No API keys, remote services, LLMs or paid dependencies are required.

## Community Cloud

Create a **new private repository containing only this directory's contents**, inspect its complete file list and history, and push only with explicit authorization. The parent workspace contains private research material and must never be used as the deployment root or copied wholesale. In Streamlit Community Cloud, select that repository and branch, set the main file to `app.py`, and deploy. The pinned `requirements.txt` is installed automatically. Review current sharing settings before deployment. No public deployment has been made.

## Models and limitations

- Rectangular PEC guide: analytical TE/TM modes, homogeneous lossless filling, exp(iβx−iωt), analytic transverse derivatives, SI internally. Cutoff uses a relative squared-wavenumber tolerance of 10⁻¹². The inclusion is only a schematic. E and H have independent arbitrary normalization.
- Coax TEM: ideal homogeneous line, no higher modes, generic dimensions.
- Symmetry: scalar test functions, not a device-specific coupling calculation.
- Coupled-mode theory: passive two-resonance synthetic model, assumed positive-frequency continuum. Candidate classification requires a real eigenvalue, all-channel darkness, zero intrinsic loss and a small residual; it is not proof of a physical BIC. Eigenvalues are sorted by real part; no parameter-sweep branch tracking or scattering model is supplied.
- Quasi-BIC: illustrative local γrad=Aδ² scaling, not a universal law. Exact zero gives infinite radiative Q.

The guide solver does not solve loaded structures, conductor loss, dispersion or a full 3D eigenproblem. No experimental validation is claimed. `metadata.json` contains editable public-safe status information.

## Confidentiality boundary

This directory is self-contained. It neither imports nor reads the parent workspace's research files. Do not add device geometries, parameters, coupling coefficients, solver outputs, experimental data, manuscript derivations or unpublished predictions. CSV downloads contain only calculated generic values and selected input metadata. Review files and Git history before any sharing.
