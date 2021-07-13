# Why not GNU Stow?
[GNU Stow](https://www.gnu.org/software/stow/) is a tool that helps manage symlinks. It is very similar to dotstree - arguably dotstree is closer to stow than other dotfiles managers. The main differences are:

If you were using stow, instead of a `spec.yaml` you would create a `stowrc` file in each program's folder. To my knowledge, stow doesn't traverse a directory tree looking for all `stowrc` files, so you would have to run it separately for each program. Of course you could automate that with shell scripts. Incidentally, you could also automate it with dotstree: Your install command would invoke `stow` and your check command would invoke `stow -v -n`.

Stow can do more advanced tricks with symlinks than dotstree, and gives you more fine grained control over how various situations are handled. For managing dotfiles, I didn't find these useful, so dotstree has less customization and is simpler.

Stow also doesn't support handling install scripts, and lastly stow is written in Perl while dotstree is in Python -- something which may or may not be important to you.
