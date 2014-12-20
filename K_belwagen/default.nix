{ pkgs ? import <nixpkgs> {} }:

# TODO check if system has jack2 installed

pkgs.stdenv.mkDerivation {
  name = "K_belwagen-1";

  src = ./.;

  buildInputs = with pkgs; [
    coreutils
    jack2
    pkgconfig
  ];

  installPhase = ''
    mkdir -p $out/bin $out/lib
    cp alarm $out/bin
    cp a.out $out/lib
    sed -i '
      s:^\(jackd\|trap\|make\|cd\)\>:#&:
      s:\./a\.out:'$out/lib/a.out':
    ' $out/bin/alarm
  '';
}
