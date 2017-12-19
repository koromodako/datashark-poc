Q=
RM=$(Q)rm
DOXYGEN=$(Q)doxygen

all: build

build: Doxyfile
	$(DOXYGEN) $<

clean:
	$(RM) -rf doxygen
