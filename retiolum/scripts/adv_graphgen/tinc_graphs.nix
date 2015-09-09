with import <nixpkgs> {};
# nix-build Reaktor.nix
# result/bin/reaktor
## or in your env
# nix-env -i -f tinc_graphs.nix

buildPythonPackage rec {
  name = "tinc_graphs-${version}";
  version = "0.2.6";
  propagatedBuildInputs = with pkgs;[
    pythonPackages.docopt
    graphviz
    imagemagick
    pythonPackages.pygeoip
  ];
  src = fetchurl {
    url = "";
    sha256 = "1dksw1s1n2hxvnga6pygkr174dywncr0wiggkrkn1srbn2amh1c2";
  };
  meta = {
    homepage = http://krebsco.de/;
    description = "Create Graphs from Tinc Stats";
    license = stdenv.lib.licenses.wtfpl;
  };
}
