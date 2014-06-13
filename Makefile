install: clean
	python setup.py install

build_vedis:
	gcc -DVEDIS_ENABLE_THREADS=1 -Wall -fPIC -c vedis/src/vedis.c -o vedis/src/vedis.o
	gcc -shared -Wl,-soname,libvedis.so.1 -o vedis/libvedis.so.1.0 vedis/src/vedis.o

clean:
	rm -fr build/
	rm -fr dist/
	rm -fr vedis.egg-info/

sdist: clean
	python setup.py sdist

upload: clean
	python setup.py sdist upload

all: clean install
