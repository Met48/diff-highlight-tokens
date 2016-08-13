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

Run

```lang=sh
sudo pip install diff-highlight-tokens

# OR

sudo easy_install diff-highlight-tokens
```

Alternatively, to install from source clone the repo and then:

```lang=sh
python setup.py install

# Or, if using Nix
nix-env -f . -i
```

## Requirements

- Python 2.7, 3.3, 3.4, 3.5
- Pygments >= 2.1
