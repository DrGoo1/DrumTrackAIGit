#!/usr/bin/env python3
import argparse, json, shutil
from pathlib import Path

EX_DRUMMERS = {"drummers": [
    {"id": "bonham", "name": "John Bonham", "feel": ["heavy","behind"], "swing": 0.06},
    {"id": "porcaro", "name": "Jeff Porcaro", "feel": ["tight","groovy"], "swing": 0.02},
    {"id": "grohl", "name": "Dave Grohl", "feel": ["aggressive"], "swing": 0.0}
]}

EX_SAMPLES = {
    "kick":   [{"id":"kick_deep","name":"Kick Deep","url":"/api/stems/common/kick_deep.wav"}],
    "snare":  [{"id":"snare_crack","name":"Snare Crack","url":"/api/stems/common/snare_crack.wav"}],
    "hihat":  [{"id":"hh_closed","name":"HiHat Closed","url":"/api/stems/common/hh_closed.wav"}],
    "ride":   [{"id":"ride_clean","name":"Ride Clean","url":"/api/stems/common/ride_clean.wav"}],
    "crash":  [{"id":"crash_big","name":"Crash Big","url":"/api/stems/common/crash_big.wav"}],
    "tom":    [{"id":"tom_mid","name":"Tom Mid","url":"/api/stems/common/tom_mid.wav"}]
}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--job-id", required=True)
    ap.add_argument("--stems", type=str, required=True)
    ap.add_argument("--meta", type=str, default=None)
    ap.add_argument("--data-root", type=str, default="./data")
    args = ap.parse_args()

    data_root = Path(args.data_root)
    stems_src = Path(args.stems)
    meta_src = Path(args.meta) if args.meta else None

    d_stems = data_root / "stems" / args.job_id
    d_common = data_root / "stems" / "common"
    d_meta = data_root / "meta"

    for p in (d_stems, d_common, d_meta):
        p.mkdir(parents=True, exist_ok=True)

    count = 0
    for ext in ("*.wav","*.flac"):
        for f in stems_src.glob(ext):
            shutil.copy2(f, d_stems / f.name)
            count += 1
    if count == 0:
        raise SystemExit(f"No stems found in {stems_src} (expected .wav/.flac)")

    drummers_dst = d_meta / "drummers.json"
    if meta_src and (meta_src / "drummers.json").exists():
        shutil.copy2(meta_src / "drummers.json", drummers_dst)
    else:
        drummers_dst.write_text(json.dumps(EX_DRUMMERS, indent=2))

    samples_dst = d_meta / "samples.json"
    if meta_src and (meta_src / "samples.json").exists():
        shutil.copy2(meta_src / "samples.json", samples_dst)
    else:
        samples_dst.write_text(json.dumps(EX_SAMPLES, indent=2))

    print(f"Seed complete: {count} stems → {d_stems}")
    print(f"Meta: {drummers_dst}, {samples_dst}")

if __name__ == "__main__":
    main()
