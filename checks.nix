{ python }:
{
  pythonTests = python.pkgs.buildPythonPackage {
    pname = "elpy";
    version = "dev";
    src = ./.;
    propagatedBuildInputs = with python.pkgs; [
      flake8
      toml
    ];
    checkInputs = with python.pkgs; [
      black
      yapf
      jedi
      autopep8
    ];

    # parso needs this to be set. Otherwise it would try to write to
    # /homeless-shelter, which is read-only.
    XDG_CACHE_HOME = "/tmp";
  };
}
