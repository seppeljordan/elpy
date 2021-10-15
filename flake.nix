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
            buildInputs = (with pkgs.python3.pkgs; [ virtualenv ])
              ++ (with pkgs; [ cask nixfmt ]);
          };
        });
    in systemDependent;
}
