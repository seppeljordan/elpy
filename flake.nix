{
  description = "elpy emacs package";
  inputs = {
    flake-utils.url = "github:numtide/flake-utils";
    nixpkgs.url = "github:NixOS/nixpkgs";
  };

  outputs = { self, nixpkgs, flake-utils }:
    let
      systemDependent = flake-utils.lib.eachDefaultSystem (system:
        let pkgs = import nixpkgs { inherit system; overlays = [self.overlay];};
        in {
          devShell = pkgs.mkShell {
            buildInputs = (with pkgs.python3.pkgs; [
              autopep8
              black
              coverage
              flake8
              isort
              jedi
              mock
              mypy
              nose
              pip
              setuptools
              twine
              types-toml
              types-setuptools
              virtualenv
              wheel
              yapf
            ]) ++ (with pkgs; [ cask nixfmt bump2version ]);
          };
          checks = import ./checks.nix {
            inherit (pkgs) python3 python38 python39 python310;
          };
        });
      systemIndependent = let
        overridePython = originalPython: let
          packageOverrides = import nix/pythonPackages.nix;
          overriddenPython = originalPython.override {
            inherit packageOverrides;
            self = overriddenPython;
          };
        in overriddenPython;
      in {
        overlay = final: prev: {
          python38 = overridePython prev.python38;
          python39 = overridePython prev.python39;
          python310 = overridePython prev.python310;
        };
      };
    in systemDependent // systemIndependent;
}
