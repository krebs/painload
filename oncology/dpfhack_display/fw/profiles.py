# AX206 based DPF profiles
#
# Feel free to add your own and post this file..
#
# 
# Note: There are even identical type of DPFs with different flash sizes.
# Thus we use the fixed sectors from 0x380000 to 0x3f0000 for our own firmware.
# This is obviously not a problem with smaller flash sizes, as the addresses
# are just mirrored, e.g. for a 2 MB flash, the firmware will end up in
# 0x1f0000, etc.

BINARY = 0
COPY = -1
PATCH = -2

# Ebay, pink
patch_pink = [
	(COPY,   [0x000000, 0x3f0000]),  # Copy sector 0
	(PATCH,  [0x0, 0x3f0000], "jmptbl_pink.ihx"),
	(BINARY, [0x0, 0x390000], "font4x8.bin"),
	(PATCH,  [0x0, 0x380000], "fw_pink.ihx"),
	(37,     [ 0x87f37fa6, 0xc8c55832, 0x27b13328 ] ,  "p_start_pink.ihx"), 
]

# Pearl 320x240
patch_320x240 = [
	(COPY,  [0x000000, 0x1f0000]),  # Copy sector 0
	(PATCH, [0x0, 0x1f0000], "jmptbl_pearl.ihx"),
	(BINARY, [0x0, 0x190000], "font4x8.bin"),
	(PATCH,  [0x0, 0x180000], "fw_pearl.ihx"),
	(37,    [ 0x984e1a0a, 0x9ef54e54, 0xf0e0beea ], "p_start_pearl.ihx"), 
]

patch_white = [
	(COPY,   [0x000000, 0x1f0000]),  # Copy sector 0
	(PATCH,  [0x0, 0x1f0000], "jmptbl_white.ihx"),
	(BINARY, [0x0, 0x190000], "font4x8.bin"),
	(PATCH,  [0x0, 0x180000], "fw_white.ihx"),
	(37,     [ 0x8b7dd5f1, 0x1e8f075b, 0x570265f2 ], "p_start_white.ihx"), 
]

# Deal Extreme various colours
patch_blue = [
	(COPY,   [0x000000, 0x3f0000]),  # Copy sector 0
	(PATCH,  [0x0000,   0x3f0000], "jmptbl_blue.ihx"),
	(BINARY, [0x0000,   0x390000], "font4x8.bin"),
	(PATCH,  [0x0000,   0x380000], "fw_blue.ihx"),
	(41,     [ 0xc4269afb, 0x16ce51ee, 0x4be56536, 0x12a60556 ],
		"p_start_blue.ihx"), 
]

# No recent firmware for these DPFs yet:
patch_silver = [
	(COPY,  [0x000000, 0x1f0000]),  # Copy sector 0
	(PATCH, [0x0, 0x1f0000], "jmptbl_blue.ihx"),
	(PATCH, [0x1330, 0x1e0000], "cmdhandler_14e5.ihx"),
	(PATCH, [0x1330, 0x1f3896], "p_usbdesc.ihx"),
	(41,    [ 0xc4269afb, 0x16ce51ee ], "p_start_blue.ihx"), 
]

# Pearl 320x240
patch1 = [
	(COPY, [0x000000, 0x1f0000]),  # Copy sector 0
	(PATCH, [0x0, 0x1f0000], "jmptbl1.ihx"),
	(PATCH, [0x1330, 0x1f34dc], "p_usbdesc.ihx"),
	(PATCH, [0x1330, 0x1e0000], "cmdhandler_big_14fb.ihx"),
	(37, [0x984e1a0a, 0x9ef54e54], "p_start1.ihx"), 
]

patch_black = [
	(COPY,   [0x000000, 0x1f0000]),  # Copy sector 0
	(PATCH,  [0x0, 0x1f0000], "jmptbl_black.ihx"),
	(BINARY, [0x0, 0x190000], "font4x8.bin"),
	(PATCH,  [0x0, 0x180000], "fw_white.ihx"),
	(36,     [ 0x822c83e4, 0xd6fe7e58 ], "p_start_black.ihx"), 
]

KNOWN_DPFS = [
# Very bright and colourful TFT screen
	[ ('20090113', 'Nov 13 2010\xff\xff\xff\xff\xff', 'ProcTbl4'), # Version
		"pink",                                                    # Short ID
		"",                                                        # URL
		{ },
		# Patch information follows here:
		# Type/Version, flashsize, patchseq
	 	[ 0, 0x400000, patch_pink ]
	],
	[ ('20090113', 'Sep 16 2010\xff\xff\xff\xff\xff', 'ProcTbl4'), # Version
		"DX_white",                                                # Short ID
		"http://www.dealextreme.com/details.dx/sku.27893",
		{ },
		# Patch information follows here:
		# Type/Version, flashsize, patchseq
	 	[ 0, 0x100000, patch_white ]
	],
	[ ('20090401', 'Oct 15 2010\xff\xff\xff\xff\xff', 'ProcTbl1'),
		"DX_blue",
		"http://www.dealextreme.com/details.dx/sku.27894",
		{ },
	 	[ 0, 0x400000, patch_blue ]
	],
	[ ('20090504', 'Mar 26 2010\xff\xff\xff\xff\xff', 'ProcTbl5' ),
		"pearl",
		"http://www.pearl.de/a-HPM1184-5618.shtml",
		{ },
	 	[ 0, 0x200000, patch_320x240 ]
	],
# Low brightness backlight. Also shows mirrored screen. Partially supported.
	[ ('20090504', 'Jul 24 2010\xff\xff\xff\xff\xff', 'ProcTbl5'),
		"focal",
		"http://www.focalprice.com/detail_EX042W.html",
		{ },
	 	[ 0, 0x200000, patch_320x240 ]
	],
	[ ('20090504', 'Mar 27 2010\xff\xff\xff\xff\xff', 'ProcTbl5' ),
		"pearl",
		"http://www.pearl.de/a-HPM1184-5618.shtml",
		{ },
	 	[ 0, 0x200000, patch_320x240 ]
	],
# Bad quality, weak screen. Not recommended.
	[ ('20090401', 'Nov 29 2010\xff\xff\xff\xff\xff', 'ProcTbl1' ),
		"Ebay_silver",
		"",
		{ },
	 	[ 0, 0x100000, patch_silver ]
	],
# Bad quality, weak screen. Not recommended.
	# Don't use this one. BROKEN. You will brick your frame.
	# [ ('20090113', 'Jan 13 2011\xff\xff\xff\xff\xff', 'ProcTbl3') ,
		# "focal_silver",
		# "",
		# { },
	 	# [ 0, 0x100000, patch4 ]
	# ],
	[ ('20090113', 'Aug 26 2010\xff\xff\xff\xff\xff', 'ProcTbl2'),
		"DX_black",
		"http://www.dealextreme.com/details.dx/sku.16133",
		{ },
	 	[ 0, 0x100000, patch_black ]
	],
]
