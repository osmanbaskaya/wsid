all: scripts fastsubs dists runsc.m wkmeans

scripts: check
	test -e $@ || ln -s ../src/scripts/* .


check:
	true

clean:
	-rm *.m *.pl *.pyc *.py *.gp *.sh fastsubs subs dists scode wkmeans wordsub *.mexa64 fastsubs-omp *~  deprecated_or_old 

### Reprository Check-out Commands
## If the latest version is required then do not set the corresponding
## tag variable.
## SCODE
SCODE_GIT_REPO=git://github.com/ai-ku/scode.git
SCODE_GIT_TAG=
## DIST
DIST_GIT_REPO=git://github.com/ai-ku/dist.git
DIST_GIT_TAG=
## WKMEANS
WKMEANS_GIT_REPO=git://github.com/ai-ku/wkmeans.git
WKMEANS_GIT_TAG=
## FASTSUBS
FASTSUBS_GIT_REPO=git://github.com/ai-ku/fastsubs.git
FASTSUBS_GIT_TAG=
###
fastsubs: check
	test -e ../src/fastsubs || (cd ../src/ ; git clone ${FASTSUBS_GIT_REPO} ; git checkout ${FASTSUBS_GIT_TAG}) 
	cd ../src/fastsubs; make
	test -e $@ || ln -s ../src/fastsubs/fastsubs-omp .
	test -e $@ || ln -s ../src/fastsubs/fastsubs .
	test -e subs || ln -s ../src/fastsubs/subs .
	test -e wordsub || ln -s ../src/fastsubs/wordsub .

dists: check
	test -e ../src/dist || (cd ../src/ ; git clone ${DIST_GIT_REPO} ; git checkout ${DIST_GIT_TAG}) 
	cd ../src/dist; make
	test -e $@ || ln -s ../src/dist/dists .

scripts: check
	test -e $@ || ln -s ../src/scripts/* .

scode: check
	test -e ../src/scode || (cd ../src/ ; git clone ${SCODE_GIT_REPO} ; git checkout ${SCODE_GIT_TAG}) 
	cd ../src/scode; make
	test -e $@ || ln -s ../src/scode/scode .

wkmeans: check
	test -e ../src/wkmeans || (cd ../src/ ; git clone ${WKMEANS_GIT_REPO} ; git checkout ${WKMEANS_GIT_TAG}) 
	cd ../src/wkmeans; make
	test -e $@ || ln -s ../src/wkmeans/wkmeans .
