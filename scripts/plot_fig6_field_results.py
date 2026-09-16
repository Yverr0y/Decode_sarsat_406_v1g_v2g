#!/usr/bin/env python3
"""Figure 6 — Field results, F5ZPI relay station, 2026-07-09 (00:00-08:59).

Counts are taken GLOBALLY from the log (total occurrences of each marker).
Per-burst block attribution is invalid since the decode worker was decoupled:
the output of burst N appears after the BURST line of burst N+1.

Usage: python3 scripts/plot_fig6_field_results.py [log] [out_basename]
"""
import re
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from PIL import Image

LOG = sys.argv[1] if len(sys.argv) > 1 else "logs/scan406_20260709_0000.log"
OUT = sys.argv[2] if len(sys.argv) > 2 else "docs/articles/figures/fig6_field_results"

txt = open(LOG, errors="replace").read()
c = lambda p: len(re.findall(p, txt))

sgb_det = c(r"BURST .* SGB ")
sgb_ok = c(r"BCH validated")
sgb_st = c(r"Frame Mode: Self-test")
sgb_no = c(r"Frame Mode: Normal")
sgb_rej = c(r"FRAME REJECTED")
sgb_fail = c(r"decode failed")

fgb_det = c(r"BURST .* FGB ")
fgb_ok = c(r"burst=\d+ (?:BCH|CRC) OK")
fgb_bad = c(r"burst=\d+ (?:BCH|CRC) FAIL")

ov = max([int(x) for x in re.findall(r"overruns (\d+)", txt)] or [0])
dr = max([int(x) for x in re.findall(r"decode drops (\d+)", txt)] or [0])

# Controle de coherence : le bilan doit boucler
assert sgb_ok + sgb_rej + sgb_fail == sgb_det, "SGB budget mismatch"
assert sgb_st + sgb_no == sgb_ok, "SGB mode split mismatch"
assert fgb_ok + fgb_bad == fgb_det, "FGB budget mismatch"

plt.rcParams.update({"font.size": 8, "font.family": "sans-serif"})
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(6.4, 2.75),
                               gridspec_kw={"width_ratios": [1.15, 1]})

# --- Panneau gauche : issue de chaque rafale detectee ---
groups = ["SGB\n(%d detected)" % sgb_det, "FGB\n(%d detected)" % fgb_det]
decoded = [sgb_ok, fgb_ok]
notdec = [sgb_rej + sgb_fail, fgb_bad]

x = range(len(groups))
b1 = ax1.bar(x, decoded, 0.55, color="0.25", label="decoded")
b2 = ax1.bar(x, notdec, 0.55, bottom=decoded, color="0.82",
             edgecolor="0.4", lw=0.6, label="not decoded")
for i, (d, n) in enumerate(zip(decoded, notdec)):
    tot = d + n
    ax1.text(i, d / 2, "%d\n(%.0f%%)" % (d, 100 * d / tot), ha="center",
             va="center", color="white", fontsize=7.5, fontweight="bold")
    if n:
        ax1.text(i, d + n / 2, "%d" % n, ha="center", va="center",
                 color="0.15", fontsize=7)
ax1.set_xticks(list(x))
ax1.set_xticklabels(groups)
ax1.set_ylabel("Bursts")
ax1.set_title("Outcome of every detected burst", fontsize=8, loc="left", pad=4)
ax1.legend(loc="upper left", frameon=False, fontsize=7)
for s in ("top", "right"):
    ax1.spines[s].set_visible(False)

# --- Panneau droit : SGB par mode + sante ---
labels = ["Self-test", "Normal"]
vals = [sgb_st, sgb_no]
ax2.bar(labels, vals, 0.5, color=["0.25", "0.55"])
for i, v in enumerate(vals):
    ax2.text(i, v + 4, str(v), ha="center", fontsize=7.5)
ax2.set_ylabel("SGB frames decoded")
ax2.set_ylim(0, max(vals) * 1.25)
ax2.set_title("Decoded SGB by spreading code", fontsize=8, loc="left", pad=4)
for s in ("top", "right"):
    ax2.spines[s].set_visible(False)

ax2.text(0.98, 0.92,
         "ring overruns: %d\ndecode-queue drops: %d\nBCH rejects: %d" % (ov, dr, sgb_rej),
         transform=ax2.transAxes, ha="right", va="top", fontsize=7,
         bbox=dict(boxstyle="round,pad=0.35", fc="white", ec="0.6", lw=0.6))

PROV = ("Figure 6 - Field results. Source log: %s (F5ZPI relay station, 80 km from "
        "Toulouse, RTL-SDR, 2026-07-09 00:00-08:59 local, 9 h continuous run, "
        "receiver software monitored through SSH over a VPN). "
        "Counts taken globally from log markers; per-burst attribution is "
        "invalid because decoding runs in a decoupled worker thread. "
        "SGB %d detected / %d decoded (%d self-test, %d normal), %d BCH "
        "rejects, %d decode failures. FGB %d detected / %d BCH OK, %d BCH "
        "FAIL. Ring overruns %d, decode-queue drops %d. "
        "Plot: python3 scripts/plot_fig6_field_results.py"
        % (LOG, sgb_det, sgb_ok, sgb_st, sgb_no, sgb_rej, sgb_fail,
           fgb_det, fgb_ok, fgb_bad, ov, dr))
META = {"Title": "dec406 field results, F5ZPI relay station, 2026-07-09",
        "Description": PROV,
        "Creator": "dec406 / scripts/plot_fig6_field_results.py",
        "Publisher": "Fabrice MOREL F4MLV"}

fig.tight_layout()
fig.savefig(OUT + ".png", dpi=300, facecolor="white", transparent=False,
            metadata={"Software": META["Creator"], "Description": PROV,
                      "Title": META["Title"]})
fig.savefig(OUT + ".svg", facecolor="white", transparent=False, metadata=META)

im = Image.open(OUT + ".png")
if im.mode != "RGB":
    from PIL.PngImagePlugin import PngInfo
    pnginfo = PngInfo()
    for k in ("Title", "Description"):
        pnginfo.add_text(k, META[k])
    pnginfo.add_text("Software", META["Creator"])
    bg = Image.new("RGB", im.size, "white")
    bg.paste(im, mask=im.split()[-1] if im.mode == "RGBA" else None)
    bg.save(OUT + ".png", dpi=(300, 300), pnginfo=pnginfo)

print("ecrit :", OUT + ".png / .svg")
print("SGB %d/%d (%d self-test, %d normal) | FGB %d/%d | overruns %d drops %d"
      % (sgb_ok, sgb_det, sgb_st, sgb_no, fgb_ok, fgb_det, ov, dr))
