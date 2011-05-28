
ifndef patch_file
patch_file := /etc/Verkrebsung.patch
endif

ifndef patch_flags
patch_flags :=
endif

.PHONY: infest dry-run
infest: $(patch_file)
	unset POSIXLY_CORRECT; patch $(patch_flags) -fNp0 < $<

$(patch_file): bin/make-patch
	$< >$@

dry-run:
	 make patch_file=/tmp/krebs-infest-dry-run.patch patch_flags=--dry-run
