{
  description = "elpy emacs package";
  inputs = {
    flake-utils.url = "github:numtide/flake-utils";
    # The following is only here since in the current version of
    # nixpkgs the cask command is broken
    nixpkgs.url = "github:seppeljordan/nixpkgs/fix-cask";
  };

  outputs = { self, nixpkgs, flake-utils }: let
    systemDependent = flake-utils.lib.eachDefaultSystem (system: let
      pkgs = import nixpkgs { inherit system; };
    in {
      devShell = pkgs.mkShell {
        buildInputs = (with pkgs.python3.pkgs; [ virtualenv ]) ++ (with pkgs; [ cask ]);
      };
    });
  in systemDependent;
}
