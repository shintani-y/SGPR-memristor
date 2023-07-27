SOURCES = $(wildcard *.sp)
CLEANALL = $(wildcard output.*)

main: *.sp
	hspice64 -i $(SOURCES) -o output/output


cleanall:
	rm -r -f output/$(CLEANALL)

