# FGB status

## 2026-09-16 — BCH terminology correction

### Observation

The FGB decoder verifies and corrects the T.001 BCH-1 and BCH-2 codewords, but
historical function names, diagnostics, CSV fields, and user-facing messages
call those checks `CRC1` and `CRC2`. This terminology is incorrect and also
propagates into generated statistics and documentation.

### Validated change

- Rename FGB validation symbols and diagnostics from `CRC` to `BCH` without
  changing parity calculations, correction limits, or frame acceptance.
- Keep the Figure 6 parser compatible with both legacy `CRC OK/FAIL` logs and
  new `BCH OK/FAIL` logs.
- Describe orbitography handling as BCH-1-only where BCH-2 is not applicable.

### Validation criteria

1. `dec406_fgb_iq` still decodes the synthetic FGB recording.
2. `dec406_iq` still decodes the mandatory synthetic SGB recording.
3. `dec406_scan` builds successfully.
4. New FGB diagnostics contain no `CRC` label; the historical-log parser still
   recognizes both spellings.

### Validation results

- `make build/dec406_fgb_iq build/dec406_iq build/dec406_scan`: passed. Only
  pre-existing compiler warnings were emitted.
- FGB OTA example
  `gqrx_FFE2F8E39048D158AC01E3AA482856824CE_40000.iq`: one frame decoded from
  four detected bursts. The accepted frame reported `BCH OK`, with zero BCH-1
  corrections and one BCH-2 correction, followed by
  `BCH: BCH-1=OK BCH-2=OK`.
- Mandatory SGB synthetic regression `test_sgb_halfsine.sigmf-data`: passed
  with normal-operation PRN, acquisition confidence 68.1, synchronization
  score 9639, and zero BCH corrections.
- `python3 -m py_compile scripts/plot_fig6_field_results.py`: passed.
- The Figure 6 parser counted 1449 legacy `CRC OK` and 57 legacy `CRC FAIL`
  markers in `logs/scan406_20260709_0000.log`, confirming compatibility with
  the historical log. Full figure generation was not run because matplotlib
  is not installed in the test environment.
- No active FGB source, public header, README, or protocol-coverage text still
  uses `CRC`; the only retained occurrences are the historical-log parser and
  this migration record.
