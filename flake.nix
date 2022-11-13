{
  description = "elpy emacs package";
  inputs = {
    flake-utils.url = "github:numtide/flake-utils";
    nixpkgs.url = "github:NixOS/nixpkgs";
  };

  outputs = { self, nixpkgs, flake-utils }:
    let
      systemDependent = flake-utils.lib.eachDefaultSystem (system:
        let
          pkgs = import nixpkgs {
            inherit system;
            overlays = [ self.overlays.default ];
          };
        in {
          devShells.default = pkgs.mkShell {
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
          checks = import ./checks.nix { inherit (pkgs) python3; };
        });
      systemIndependent = {
        overlays.default = final: prev: {
          pythonPackagesExtensions = prev.pythonPackagesExtensions
            ++ [ (import nix/pythonPackages.nix) ];
        };
      };
    in systemDependent // systemIndependent;
}
