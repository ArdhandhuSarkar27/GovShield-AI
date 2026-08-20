"""
nfhs_engine.py — GovShield NFHS-5 State Intelligence Engine
============================================================
Loads NFHS-5 (National Family Health Survey 2019-21) data from
data.gov.in and provides:
  1. State-level fraud vulnerability scores (FVI)
  2. Context-aware fraud scoring boost for /api/predict
  3. State comparison data for the State Analytics page
  4. Globe colour data for the 3D visualisation

No API key needed. Pure pandas + xlrd, 100% offline.
"""

import os, json, logging
import pandas as pd
import xlrd

logger = logging.getLogger('govshield.nfhs')

BASE_DIR   = os.path.dirname(os.path.abspath(__file__))
XLS_PATH   = os.path.join(BASE_DIR, 'NFHS_5_Factsheets_Data.xls')
JSON_CACHE = os.path.join(BASE_DIR, 'static', 'nfhs_state_data.json')

# ── Column map (0-indexed) ────────────────────────────────────────────────────
_COLS = {
    'insurance_pct':       16,
    'oop_delivery':        51,
    'institutional_birth': 54,
    'public_birth_pct':    55,
    'csection_total':      58,
    'csection_private':    59,
    'csection_public':     60,
    'stunted_pct':         85,
    'low_bmi_women':       90,
    'children_anaemic':    96,
    'high_sugar_women':   103,
    'high_bp_women':      109,
    'tobacco_women':      132,
    'tobacco_men':        133,
}

_state_cache: dict = {}

def _compute_fvi(ins: float, csec_pvt: float, oop: float) -> float:
    """
    Fraud Vulnerability Index (0–100).
    Based on three independently defensible NFHS-5 indicators:

      1. Insurance gap (40 pts max)
         Low insurance coverage → hospitals face desperate patients with no
         alternative → higher temptation to inflate claims.
         Formula: max(0, 60 - insurance_pct) / 60 × 40

      2. Private C-section over-medicalisation (35 pts max)
         C-section fraud is the #1 Ayushman Bharat fraud type.
         Above 20% private C-section rate is considered the safe baseline
         (WHO recommends ≤15% medically necessary; 20% allows for regional
         variation). Every % above 20 adds risk.
         Formula: max(0, csec_pvt - 20) / 60 × 35

      3. Out-of-pocket delivery burden (25 pts max)
         High OOP in PUBLIC hospitals means the system is already broken —
         patients are paying bribes or extra charges even in free facilities,
         indicating systemic billing fraud.
         Formula: min(oop / 20000, 1.0) × 25

    Reference thresholds:
      FVI ≥ 40 → HIGH   (strong need for enhanced surveillance)
      FVI 22–39 → MEDIUM (standard monitoring)
      FVI < 22  → LOW   (routine checks sufficient)
    """
    ins_risk  = max(0.0, (60.0 - ins)    / 60.0) * 40.0
    csec_risk = max(0.0, (csec_pvt - 20) / 60.0) * 35.0
    oop_risk  = min(oop / 20000.0, 1.0)           * 25.0
    return round(ins_risk + csec_risk + oop_risk, 1)


def load_nfhs_data(force_reload: bool = False) -> dict:
    """Load NFHS-5 state data. Returns dict keyed by state name."""
    global _state_cache
    if _state_cache and not force_reload:
        return _state_cache

    # Try pre-built JSON cache first (faster)
    if os.path.exists(JSON_CACHE) and not force_reload:
        try:
            with open(JSON_CACHE) as f:
                _state_cache = json.load(f)
            logger.info(f"✅ NFHS-5 loaded from cache ({len(_state_cache)} states)")
            return _state_cache
        except Exception as e:
            logger.warning(f"Cache read failed: {e} — falling back to XLS")

    if not os.path.exists(XLS_PATH):
        logger.warning(f"⚠️  NFHS XLS not found at {XLS_PATH}")
        return {}

    try:
        wb = xlrd.open_workbook(XLS_PATH)
        sh = wb.sheet_by_index(0)
        result = {}
        for r in range(1, sh.nrows):
            state = str(sh.cell_value(r, 0)).strip()
            area  = str(sh.cell_value(r, 1)).strip()
            if area != 'Total' or not state:
                continue

            def _safe(col):
                try:
                    v = sh.cell_value(r, col)
                    return round(float(v), 2) if v != '' else None
                except Exception:
                    return None

            rec = {k: _safe(c) for k, c in _COLS.items()}

            ins      = rec['insurance_pct']    or 40.0
            csec_pvt = rec['csection_private'] or 21.0
            oop      = rec['oop_delivery']     or 2916.0

            fvi = _compute_fvi(ins, csec_pvt, oop)
            rec['fraud_vulnerability_index'] = fvi
            rec['risk_level'] = 'HIGH' if fvi >= 40 else ('MEDIUM' if fvi >= 22 else 'LOW')
            result[state] = rec

        _state_cache = result
        # Persist cache
        try:
            with open(JSON_CACHE, 'w') as f:
                json.dump(result, f, indent=2)
        except Exception:
            pass
        logger.info(f"✅ NFHS-5 parsed from XLS ({len(result)} states)")
        return result

    except Exception as e:
        logger.error(f"Failed to load NFHS-5 data: {e}", exc_info=True)
        return {}


def get_state_profile(state_name: str) -> dict | None:
    """Return NFHS-5 profile for a single state. None if not found."""
    data = load_nfhs_data()
    # Exact match first
    if state_name in data:
        return data[state_name]
    # Case-insensitive fallback
    sl = state_name.lower()
    for k, v in data.items():
        if k.lower() == sl:
            return v
    return None


def nfhs_score_boost(state_name: str, procedure: str = '') -> tuple:
    """
    Returns (extra_risk_points: float, reason_string: str | None)

    Adds up to 20 extra points to fraud score based on:
      - State FVI level  (HIGH=+15, MEDIUM=+8, LOW=+0)
      - Procedure match  (C-section claim in high-csec state: +5 extra)

    This is a bounded, additive modifier — it CANNOT push a clean claim
    into fraud territory on its own. Max 20 pts, so a 39% claim stays at
    59% max — still REVIEW, not FLAGGED.
    """
    profile = get_state_profile(state_name)
    if not profile:
        return 0.0, None

    fvi   = profile.get('fraud_vulnerability_index', 0)
    level = profile.get('risk_level', 'LOW')
    ins   = profile.get('insurance_pct', 40)
    csec  = profile.get('csection_private', 21)

    pts = 0.0
    reasons = []

    if level == 'HIGH':
        pts += 15
        reasons.append(
            f"🌍 {state_name} is HIGH fraud-vulnerability (FVI={fvi}, "
            f"insurance only {ins}%) — NFHS-5 data (+15 pts)"
        )
    elif level == 'MEDIUM':
        pts += 8
        reasons.append(
            f"🌍 {state_name} is MEDIUM fraud-vulnerability (FVI={fvi}) "
            f"— NFHS-5 data (+8 pts)"
        )

    proc_lower = procedure.lower()
    csec_keywords = ('caesarean','c-section','csection','c section','delivery','maternal','obstetric')
    if any(k in proc_lower for k in csec_keywords):
        if csec > 50:
            pts += 5
            reasons.append(
                f"🔬 {state_name} private C-section rate is {csec}% "
                f"(national avg 47%) — procedure-state mismatch (+5 pts)"
            )

    reason_str = ' | '.join(reasons) if reasons else None
    return round(min(pts, 20.0), 1), reason_str


def get_all_states_summary() -> list:
    """Return sorted list of all state profiles for the analytics page."""
    data = load_nfhs_data()
    result = []
    for name, rec in data.items():
        if name == 'India':
            continue
        result.append({
            'state': name,
            'insurance_pct':          rec.get('insurance_pct'),
            'csection_private':       rec.get('csection_private'),
            'oop_delivery':           rec.get('oop_delivery'),
            'institutional_birth':    rec.get('institutional_birth'),
            'children_anaemic':       rec.get('children_anaemic'),
            'high_bp_women':          rec.get('high_bp_women'),
            'fraud_vulnerability_index': rec.get('fraud_vulnerability_index'),
            'risk_level':             rec.get('risk_level'),
        })
    result.sort(key=lambda x: -(x.get('fraud_vulnerability_index') or 0))
    return result


def get_india_summary() -> dict:
    """Return India-level aggregate from NFHS-5."""
    data = load_nfhs_data()
    return data.get('India', {})


# Pre-load on import so first request is fast
try:
    load_nfhs_data()
except Exception:
    pass
