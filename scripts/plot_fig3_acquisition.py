#!/usr/bin/env python3
"""Figure 3 — SGB acquisition diagnostic (two stacked panels).

Same over-the-air self-test burst correlated against both PRN families, over
the same +/-8 kHz acquisition sweep and on the same vertical scale. The wrong
code yields no peak; the correct code yields a sharp one.

Input CSV produced by:
    COARSE_DIAG=1 ./build/dec406_iq <burst.cf32> -s 2457600
"""
import csv
import sys
from collections import defaultdict

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import LogLocator, NullLocator

CSV = sys.argv[1] if len(sys.argv) > 1 else "logs/freq_acq_coarse_selftest_194013.csv"
OUT = sys.argv[2] if len(sys.argv) > 2 else "docs/articles/figures/fig3_acquisition_diagnostic"

# passe 1 = NORMAL PRN (mauvais code), passe 2 = SELF-TEST PRN (bon code)
TITLES = {1: "Normal PRN — wrong spreading code",
          2: "Self-test PRN — correct spreading code"}

best = defaultdict(dict)
with open(CSV) as fh:
    for row in csv.DictReader(fh):
        b, f, s = int(row["burst"]), float(row["f_hz"]), float(row["step_max"])
        if f not in best[b] or s > best[b][f]:
            best[b][f] = s

plt.rcParams.update({"font.size": 8, "font.family": "sans-serif"})
fig, axes = plt.subplots(2, 1, figsize=(4.33, 3.60), sharex=True, sharey=True)

for ax, b in zip(axes, (1, 2)):
    freqs = sorted(best[b])
    scores = [best[b][f] / 1e12 for f in freqs]
    ax.plot([f / 1000.0 for f in freqs], scores, color="black", lw=0.8)

    pf = max(best[b], key=lambda f: best[b][f])
    ps = best[b][pf] / 1e12
    ax.set_title(TITLES[b], fontsize=8, loc="left", pad=3)
    ax.set_yscale("log")
    ax.set_ylim(3, 600)
    ax.set_xlim(-8, 8)
    # Uniquement les decades : pas de foret de graduations mineures
    ax.yaxis.set_major_locator(LogLocator(base=10.0))
    ax.yaxis.set_minor_locator(NullLocator())
    ax.set_xticks(range(-8, 9, 2))
    ax.grid(True, which="major", ls=":", lw=0.5, color="0.85")
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)

    if b == 1:
        txt = (r"wrong-code maximum: $%.2f \times 10^{13}$"
               "\n" r"at $%.0f$ Hz" % (ps / 10.0, pf))
    else:
        txt = (r"correlation peak: $%.2f \times 10^{14}$"
               "\n" r"at $%.0f$ Hz" % (ps / 100.0, pf))
    ax.annotate(txt, xy=(pf / 1000.0, ps), xytext=(1.0, 260),
                arrowprops=dict(arrowstyle="->", lw=0.8),
                fontsize=7, ha="left", va="center")

axes[1].set_xlabel("Residual carrier frequency (kHz)")
fig.supylabel(r"Raw correlation power / $10^{12}$ (log scale)",
              fontsize=8, x=0.015)

PROV = (
    "Figure 3 - SGB acquisition diagnostic. "
    "Source IQ: logs/firmin_sgb_selftest_20260708/sgb_ok_194013_2773Hz.cf32 "
    "(real over-the-air SGB self-test burst, TAC 65534, captured 2026-07-08 "
    "19:40:13 UTC+2 at the F5ZPI relay station 80 km from Toulouse, RTL-SDR, "
    "post-NCO window dumped by dec406_scan DUMP_OK). "
    "Sample rate 2457600 Hz; chip rate 38400 chips/s (64 samples/chip). "
    "Coarse search window +/-8000 Hz, step 12 Hz, 1024-chip coherent "
    "correlation, best of I/Q phase per frequency. "
    "Displayed correlation powers are divided by 1e12. "
    "CSV: COARSE_DIAG=1 ./build/dec406_iq "
    "logs/firmin_sgb_selftest_20260708/sgb_ok_194013_2773Hz.cf32 -s 2457600 "
    "-> logs/freq_acq_coarse_selftest_194013.csv . "
    "Plot: python3 scripts/plot_fig3_acquisition.py . "
    "Result: Normal PRN max 1.34e13 @ -1724 Hz (confidence 2.6, rejected); "
    "Self-test PRN peak 2.73e14 @ -1712 Hz (confidence 52.8, accepted); "
    "frame decoded with BCH nerr=0."
)
META = {"Title": "SGB acquisition diagnostic: correct vs wrong spreading code",
        "Description": PROV,
        "Creator": "dec406 / scripts/plot_fig3_acquisition.py",
        "Publisher": "Fabrice MOREL F4MLV"}

fig.tight_layout()
fig.savefig(OUT + ".png", dpi=300, facecolor="white", transparent=False,
            metadata={"Software": META["Creator"], "Description": PROV,
                      "Title": META["Title"]})
fig.savefig(OUT + ".svg", facecolor="white", transparent=False, metadata=META)

from PIL import Image
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

r = {b: (max(best[b], key=lambda f: best[b][f]), max(best[b].values())) for b in best}
print("ecrit :", OUT + ".png / .svg")
print("normal    : max %.2e @ %+.0f Hz" % (r[1][1], r[1][0]))
print("self-test : max %.2e @ %+.0f Hz  (ratio %.0fx)"
      % (r[2][1], r[2][0], r[2][1] / r[1][1]))
