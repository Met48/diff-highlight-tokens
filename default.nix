{ pkgs ? import <nixpkgs> {} }:
pkgs.callPackage ./project.nix {}
