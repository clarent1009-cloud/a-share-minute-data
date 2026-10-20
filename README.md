# A-share minute data collector

Collects the most recent five trading days of 1-minute data from Eastmoney `trends2` for `002463`.

## Setup
1. Create a **private** GitHub repository, e.g. `a-share-minute-data`.
2. Upload `collect.py` and `.github/workflows/collect.yml` (keep the paths exact). Add this README if desired.
3. In Settings → Actions → General → Workflow permissions, choose **Read and write permissions** and save (if available).
4. In Actions, enable workflows if prompted. Select **Collect A-share minute data** → **Run workflow**.
5. Inspect the run log and files under `data/002463/YYYY-MM-DD/`.

The workflow is scheduled Mon–Fri at 16:20 Beijing time (08:20 UTC). GitHub may delay scheduled runs; market holidays may still trigger runs. The five-day overlap helps recover missed days, but outages longer than five trading days cannot be automatically repaired using this endpoint alone.

## Data fields
The CSV preserves the Eastmoney `fields2` order as `timestamp,f52,f53,f54,f55,f56,f57,f58`. **Do not assume field meanings or minute label convention without independent validation.** `raw.json` preserves the source strings and metadata for audit.

## Important
- The endpoint is unofficial, may rate-limit, block GitHub runners, or change its schema without notice.
- This pipeline is for research, not trading execution or real-time trading signals.
- Validate row counts, time labels, and price/volume against Wind before backtesting.
- Keep the repository private if desired; this is not a licensed market-data redistribution service.
