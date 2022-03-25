{ python3, python38, python39, python310 }:
{
  python38Tests = python38.pkgs.elpy;
  python39Tests = python39.pkgs.elpy;
  python310Tests = python310.pkgs.elpy;
  python3Tests = python3.pkgs.elpy;
}
