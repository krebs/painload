# Distribution-Neutral Augmentation

Warning: This component will compromise your system in hard and obscure ways.

## //DNA/linux

This module will mutilate your running kernel's sys_call_table so //
resolves to the krebs repository.

## Quickstart

    make -C //DNA/linux
    sudo insmod //DNA/linux/krebs.ko

