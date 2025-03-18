let
  overlay = (self: super: rec {
    python313 = super.python312.override {
      packageOverrides = self: super: {
      };
    };

    python313Packages = python313.pkgs;
  });

in
{ pkgs ? import <nixpkgs> { overlays = [ overlay ]; } }:
pkgs.mkShell {

  buildInputs = with pkgs; [
    gnumake
    markdown-oxide
    nfdump
    nil
    nixd

    (python313.withPackages (python-pkgs: [
      python-pkgs.docker
      python-pkgs.flask
      python-pkgs.kafka-python-ng
      python-pkgs.loguru
      python-pkgs.python-dotenv
      python-pkgs.python-lsp-server
      python-pkgs.websockets
    ]))
  ];
}
