# Tahoe in Retiolum
For all the secret stuff, krebsco is using a tahoe installation with 1
introducer and a number of tahoe bricks. 

# Adding new bricks & clients
see //cholerab/tahoe/{brick,client}\_installation

# Replacing the introducer
if the introducer may die off, all crypto material is saved in 
krebs:tahoe/introducer. There will be a backup somewhere, but bootstrapping
always sucks.

Follow the generic brick installation,
use the configuration file at conf/tahoe.cfg and copy the crypto material in
the private folder of the installation. 
autostart that shit
