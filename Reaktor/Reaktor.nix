with import <nixpkgs> {};
# nix-build Reaktor.nix
# result/bin/reaktor

buildPythonPackage rec {
  name = "Reaktor-${version}";
  version = "0.2.6";
  propagatedBuildInputs = with pkgs.pythonPackages;[
    pythonPackages.docopt
  ];
  src = fetchurl {
    url = "https://pypi.python.org/packages/source/R/Reaktor/Reaktor-0.2.6.tar.gz";
    sha256 = "1dksw1s1n2hxvnga6pygjr174dywncr0wiggkrkn1srbn2amh1c2";
  };
}
