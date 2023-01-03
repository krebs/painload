{ pkgs ? import <nixpkgs> {} }:
pkgs.mkShell {
  packages = [
    (pkgs.writers.writePython3Bin "run" {
      libraries = [
        pkgs.python3Packages.numpy
        pkgs.python3Packages.scipy
      ];
    } /* py */ ''
      import numpy as np
      from scipy.stats import fisher_exact
      SIGNIFICANCE = 0.05

      # ↓truth| KORN | VODKA |←guess
      # ------------------------
      # KORN  |  a   |   b   |
      # VODKA |  c   |   d   |

      a = 4
      b = 0
      c = 0
      d = 4

      _, p_value = fisher_exact(np.array([[a, b], [c, d]], np.int32))

      print("Scientists have found out", end=": ")

      if p_value < SIGNIFICANCE:
          print("korn != vodka.")
      else:
          print("korn == vodka.")

      print(f"p-value: {p_value} (threshold: {SIGNIFICANCE})")
    '')
  ];
}
