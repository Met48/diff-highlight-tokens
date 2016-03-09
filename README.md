# diff-highlight-tokens

`diff-highlight-tokens` provides language-aware highlighting for git diff output.


## Usage

Pipe any git diff to `diff-highlight-tokens`. To always use this script, configure the pager in `.gitconfig`:

```
[pager]
    diff = diff-highlight-tokens | less -FX
    show = diff-highlight-tokens | less -FX
```


## Installation

Clone the repo. Then:

```lang=sh
python setup.py install
```

If using Nix:
```lang=sh
nix-env -f . -i
```
