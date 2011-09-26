# //bridge

Bridge is a tool to connect your favourite editor and interpreter (or
similar) for maximum profit.


## usage by example

    # start your favourite interpreter, e.g. bc, in a new session
    bridge create my_fancy_interpreter bc

    # attach a terminal to the session
    bridge attach my_fancy_interpreter

    # fire up your favourite editor (in another terminal)
    vim
    # press <F12> to connect to the session
    # press return
    # write interpreter stuff, e.g. 42^23
    # mark that stuff
    # press return

    # you can use tab-completion everywhere (if installed)


## install bridge (bourne) shell integration

Hint #1: reboot your system or similar for this to take full effect
Hint #2: you could also use ~/.profile or similar

    echo 'PATH="${PATH+$PATH:}//bridge/bin"' >> /etc/profile


## install bridge Vim integration

Hint: your vim-setup probably differs

    ln -s //bridge/share/vim/plugin/bridge.vim ~/.vim/plugin/


## install bridge bash completion

Hint #1: reboot your system or similar for this to take full effect
Hint #2: this could differ on your system, of course
Hint #3: you could also use ~/.profile or similar

    ln -s //bridge/etc/bash_completion.d/bridge /etc/bash_completion.d/


## install bridge into some usr-like hierarchy [advanced]

  tar -C //bridge -c . | tar --exclude=./README.md -C ~/opt -v -x

