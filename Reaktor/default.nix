with import <nixpkgs> {};
# nix-shell --pure .
stdenv.mkDerivation rec {
    name = "Reaktor-${version}";
    version = "0.2.6";
    buildInputs = with pkgs;[
      python34
      python34Packages.docopt
    ];

    shellHook =''
      [ ! -d venv ] && virtualenv --python=python3.4 venv
      . venv/bin/activate
    '' ;
}
