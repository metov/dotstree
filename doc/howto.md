# Program-specific usage tips
For most programs, using dotstree should be straightforward. That's the point! 😎

Occasionally, you get quirky programs that have a convoluted way of storing configuration. This page has some tips for known cases.

## Linux
### Kitty
[Kitty](https://github.com/kovidgoyal/kitty) has the nice feature of allowing [includes in its config](https://sw.kovidgoyal.net/kitty/conf/). The include will not work if you symlink just `kitty.conf`, as kitty will look for includes relative to the symlink, not the symlink target. Instead you should symlink the entire kitty dir:
```
symlinks:
  # This breaks includes, don't do it!
  #- from: ~/.config/kitty/kitty.conf
  #  to: dots/kitty.conf

  # Symlink entire dir so that includes work
  - from: ~/.config/kitty
    to: ./dots
```

Now `include colors.conf` in `dots/kitty.conf` will correctly load `dots/colors.conf`.

### Cinnamon
Cinnamon uses a [complex configuration system](https://wiki.archlinux.org/title/Cinnamon#Configuration) and it's not practical to simply symlink the underlying files. Instead, you can dump the config into a file and version that.

Your `dump.sh` script will look like this:
```
#!/usr/bin/env sh

dconf dump /org/cinnamon/desktop/keybindings/ > keybindings.dconf
dconf dump /org/cinnamon/desktop/applications/ > applications.dconf
```

You can do whatever paths you want, but it's probably not a good idea to just do the entire `/org/cinnamon/` it will have many non-portable things and probably won't work.

A `load.sh` must have the corresponding commands (yes, I know it's cat abuse):
```
#!/usr/bin/env sh

cat keybindings.dconf | dconf load /org/cinnamon/desktop/keybindings/
cat applications.dconf | dconf load /org/cinnamon/desktop/applications/
```

You can now create a `spec.yaml`:
```
install ./load.sh
```

And `dots install` will also load your dconf settings.

In this example, you'd have to manually keep the two scripts synchronized. You can also single-source the list of dconf keys and corresponding files from something like `keys.json`. Then your dump and load scripts would iterate through `keys.json` and call dconf load/dump for each one. I find that doing this kind of stuff is easier in Python, so the scripts can become `dump.py` and `load.py` -- and your spec would say `install: python load.py`.

