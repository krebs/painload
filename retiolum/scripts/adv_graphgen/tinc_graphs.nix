with import <nixpkgs> {};
# nix-build Reaktor.nix
# result/bin/reaktor
## or in your env
# nix-env -i -f tinc_graphs.nix

python3Packages.buildPythonPackage rec {
  name = "tinc_graphs-${version}";
  version = "0.2.6";
  propagatedBuildInputs = with pkgs;[
    graphviz
    imagemagick
    librsvg
    libpng

    # optional if you want geolocation:
    python3Packages.pygeoip
    # geolite-legacy for the db:
    ## ${geolite-legacy}/share/GeoIP/GeoIPCity.dat
  ];
  #src = fetchurl {
    #url = "";
    #sha256 = "1dksw1s1n2hxvnga6pygkr174dywncr0wiggkrkn1srbn2amh1c2";
  #};
  src = ./.;
  meta = {
    homepage = http://krebsco.de/;
    description = "Create Graphs from Tinc Stats";
    license = stdenv.lib.licenses.wtfpl;
  };
}
