# Detailed description
Dotstree works on "specs". A spec tells dotstree how to manage that program.

* If you specify any `symlinks`, `dots install` will create them and `dots check` will verify them.
* If you specify an `install` command, `dots install` will run it (after setting up symlinks)
* If you specify an `check` command, `dots check` will run it to check that the program is installed and `dots install` will skip it if it is already installed

Specs are YAML files called `spec.yaml` or `spec.yml` and they must each go in their own folder. Dotstree will treat the name of the folder as the name of the program. You should put all files pertaining to the program in that folder as well.

So long as you follow the above, you can organize your specs in folders however you like. You can group related programs together, or separate them by stages. You can split up your dotfiles across several git repos if you want. Dotstree doesn't care, you give it a folder and it will process everything in that folder. Everything important is contained in the specs under that folder. 

## Spec syntax
Specs are YAML dictionaries. They can have three keys (all are optional):

```yaml
# A list of dicts with from and to keys 
symlinks:
    # Where the dotfile would normally be
  - from: ./.zshrc
    # Where you want to actually keep it, relative to this spec
    to: dots/zshrc

  # Another symlink, this one is a directory
  - from: ./zsh-custom
    to: dots/custom

# If this exits with code 0, the program is installed
check: zsh --version

# This command will be run if you do dots install
install: sudo pacman -S zsh
```

That's all!

## Tips and tricks
### Portable installs
One problem with install commands is that they depend on the platform. It might be `pacman -S` on one computer and `apt-get install` on another. The obvious solution is to just add some if-else logic that checks what plaform you're on, and runs whichever command is appropriate.

Well, the good news is you don't have to write this yourself. I wrote a package called [installcmd](https://github.com/metov/installcmd) that does it. So instead of `pacman -S` you would use `$(installcmd noninteractive)` and hopefully installcmd knows the command for your platform.

### Complex commands
Sometimes the install isn't just one short command but more involved. For example, my actual zsh installation is something like:

* Install zsh
* Set environment variables related to Oh-my-zsh
* Install Oh-my-zsh
* Set zsh to be default shell

I *could* just make this one command by chaining them all with `&&`, but that looks ugly to me. Plus, Python isn't quite as good at running shell commands as your actual shell, so there's a certain point after which some shell magic can get lost in translation.
 
The alternative? I put it in a script called `install.sh`, and the install command is just `install: ./install.sh`. Simple! Now I can document my script to my heart's content.

### Multiple programs in a spec
Dotstree doesn't care about the programs themselves, it only knows the install and check commands you gave. So you can actually give install command that install multiple things. This might be useful when two programs are so closely related that it makes no sense to install one without the other.

### Dummy installs
It doesn't matter what you actually put in your install and check commands. Dotstree will just blindly run them as commands. This allows you to do things other than just installing programs.

For example, I like to set certain parameters in my `/etc/` files. I have a spec for these and the install command is actually a script that edits the file. The check command greps the file to see if the correct line is in it.

### Grouping specs into layers
The name of the folder containing a spec is assumed to be the name of that program. All parent dirs of *that* are assumed to be the "layer".

By itself, the layer doesn't do much. It allows you to organize your specs the way you want and makes the output a bit more informative. However, because dotstree relies on directory trees, you can use this to conveniently specify subsets of your specs. For example, you can create three directories in your dotfiles repo: `general`, `linux`, `mac` to handle both OS-specific programs as well as portable ones. On Linux machines you can run `dots install` for `general` and for `linux`. On Macs you can run it for `general` and then for `mac`.

### Using layers to handle dependencies
I like to use a Python venv for my day to day use rather than my system Python. I set my shell to automatically activate the venv by putting the command in my zshrc. So my setup goes like:

* Set up zsh and Python venv
* Install everything else

Step 2 must happen after 1 because "everything else" includes Python packages. If I install them before the venv, they'll end up in the system Python, not the venv, and won't be usable from my automatically-activating venv. These is an example of dependencies.

I solve it by simply having two layers. The first layer has things that don't have dependencies. The second layer has things that depend on the first layer. If I had a more complex situation, I could continue like this: Programs that depend on layer n and below go to layer n+1. In practice, it doesn't get that complicated -- package managers handle most dependencies well enough and finicky situations like the above are rare.

### Spec order
If you care about order, specs are handled lexicographically. This means you can follow a common Unix convention to make your specs be installed in a certain order: Call their folders `10-first` and `90-last`.

### Bootstrapping
Having an automated dotfile deployment is nice, but it has one problem: The deployment script itself will usually have some dependencies that must be set up manually. For dotstree, you at least need to have Python and dotstree installed. I handle this with a `bootstrap.sh` script. I also use layers to handle dependencies between my dotfiles. The end result is that in my dotfiles repo, there are three scripts:

* `bootstrap.sh` - installs dotstree and installcmd in the system's default Python.
* `deploy-1.sh` - sets up my shell and Python venv. Installs dotstree and installcmd in this venv (bootstrap would install them in the system Python).
* `deploy-2.sh` - installs the other programs.

When I am deploying my dotfiles on a new computer, I manually install Python and git if necessary, clone the dotfiles repo, then run these three scripts in sequence. You can of course roll all of this into a single script, that you can curl and source. I don't really see the need to do all that just to save a few seconds of extra typing, but YMMV.

### Local files
Sometimes you want to add some configuration to your program, but it is only relevant to that one system and shouldn't be versioned. For example, if you have a file called `password.txt` that contains a password for your program to use, you might not want to store the password in your git repo (you can gpg-encrypt the file and then version it, but that's not the point). There's nothing stopping you from just adding the file to your `.gitignore`.

A sligthly more annoying situation is when the machine-specific data is part of a file which *should* otherwise be versioned. For example, if instead you have `credentials.yaml` containing:
```yaml
# This should be versioned
username: foo@example.com

# This shouldn't be
password: "real password"
```

One way to handle it is [git filters](https://git-scm.com/docs/gitattributes#_filter). An alternative which may be more convenient is to do the following:
* Create a "template" config, for example `~/dotfiles/foo/template/credentials.yaml` containing:
    ```yaml
    username: foo@example.com
    password: changeme
    ```
* Add this template to git
* In your install command, copy the template to its real location:
    ```yaml
    symlinks:
      - from: ~/.config/foo
        to: configs/
    
    install: $(installcmd) foo && mkdir /&& cp template/* configs/*
    check: foo --version
    ```
 * Create a `~/dotfiles/foo/configs/.gitignore` and put `credentials.yaml` in it
    * It is better to use the `foo/configs/.gitignore` rather  
