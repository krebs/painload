Overview
=======
Punani is a meta packagemanager comprising a server which resolves package
requests and a client containing the logic to find the best suitable packer
on the host system. Packagenames in Punani are binaries in the PATH. All
library packages are named in the Principle of Least Surprise[1]. Different
package names can resolve into the same package.

If you want to install the `hostname` tool, the query is 
  punani install hostname
on an archlinux this will result in the call :
  pacman --noconfirm -Sy --needed inetutils

[1] http://de.wikipedia.org/wiki/Principle_of_Least_Surprise

Punani Client
============
The punani client will determine which packer are available on the system
and then send a request to the punani server to find out how the given
package is called with the given packer. In addition to that, the client
will add flags to the packers call in order to install packages only when
needed and disable user interaction.

Punani Server
============

The punani server is a web-service which resolves request in the following
manner:
  localhost/$packer/$package
The result is the package-name with the given packer or 404 if not found.
