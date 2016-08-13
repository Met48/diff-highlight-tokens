{ pkgs, stdenv, pythonPackages }:
let
  version = "0.2.0";
  self = pythonPackages;
  buildPythonPackage = self.buildPythonPackage;
in
buildPythonPackage rec {
  name = "diff-highlight-tokens-${version}";
  src = ./.;
  buildInputs = with self; [ pytest pytestrunner ];
  propagatedBuildInputs = with self; [ pygments ];

  meta = {
    description = "A command line tool to apply language-specific highlighting to git diffs";
    homepage = "https://github.com/Met48/diff-highlight-tokens";
    license = pkgs.lib.licenses.mit;
  };
}
