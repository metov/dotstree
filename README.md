# Dotfiles manager based on directory trees
Dotstree is a dotfiles manager. "Another one??" I know, right. Here's the highlights:

* The dotfiles are symlinked
* Every program's deployment spec is stored in its own folder
* Install commands can be part of the deployment
* You can cherrypick which programs to deploy based on which directory trees you pass to dotstree (hence the name)
    * This can be used to handle alternate platforms and dependencies
* You can check and sync programs against their spec 
* Written in Python, released to Pypi

## Usage
You can install it with `pip install dotstree`. To see basic usage info, try `dots --help`. I can provide a [`tldr`](https://github.com/tldr-pages/tldr) page if there's interest - just open an issue. Your dotfiles specs are expected to be in some kind of directory tree that you pass to dotstree. Normally this would be a git repo - but dotstree doesn't care. 

Further reading:
* [Details](doc/details.md)
* [Why not GNU Stow?](doc/why-not-gnu-stow.md)
