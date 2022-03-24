{
  description = "elpy emacs package";
  inputs = {
    flake-utils.url = "github:numtide/flake-utils";
    nixpkgs.url = "github:NixOS/nixpkgs";
  };

  outputs = { self, nixpkgs, flake-utils }:
    let
      systemDependent = flake-utils.lib.eachDefaultSystem (system:
        let pkgs = import nixpkgs { inherit system; };
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
            ]) ++ (with pkgs; [ cask nixfmt ]);
          };
        });
    in systemDependent;
}
