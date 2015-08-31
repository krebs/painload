with import <nixpkgs> {};
# nix-build Reaktor.nix
# result/bin/reaktor
## or in your env
# nix-env -i -f Reaktor.nix

buildPythonPackage rec {
  name = "Reaktor-${version}";
  version = "0.2.6";
  propagatedBuildInputs = with pkgs;[
    pythonPackages.docopt
    utillinux # for tell_on-join
    git
  ];
  src = fetchurl {
    url = "https://pypi.python.org/packages/source/R/Reaktor/Reaktor-${version}.tar.gz";
    sha256 = "1dksw1s1n2hxvnga6pygjr174dywncr0wiggkrkn1srbn2amh1c2";
  };
  meta = {
    homepage = http://krebsco.de/;
    description = "An IRC bot based on asynchat";
    license = stdenv.lib.licenses.wtfpl;
  };
}
