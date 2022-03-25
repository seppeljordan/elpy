{ buildPythonPackage

, flake8, toml, yapf, jedi, autopep8, black
}:
buildPythonPackage {
  pname = "elpy";
  version = "dev";
  src = ../..;
  propagatedBuildInputs = [
    flake8
    toml
  ];
  checkInputs = [
    black
    yapf
    jedi
    autopep8
  ];

  # parso needs this to be set. Otherwise it would try to write to
  # /homeless-shelter, which is read-only.
  XDG_CACHE_HOME = "/tmp";
}
