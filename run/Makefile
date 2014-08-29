SHELL := /bin/bash

.SECONDARY:

### PATH
SRILM_PATH=/ai/opt/srilm/bin/i686-m64

export PATH:=.:../bin:${SRILM_PATH}:${PATH}

SEED=1
CPU=25
LM=enw.lm.gz
SCORER= java -jar ../data/evaluation/task-3-scorer.jar

bin:
	cd ../bin; make

enw.lm.gz:
	ln -s /ai/work/upos_phd/run/enw_ukvac2/enw.lm.gz

s13-test-all.context.gz: 
	ln -s /ai/home/obaskaya/semeval13-task13/run/test.context.gz $@

s13-test.context.gz: s13-test-all.context.gz s13.key
	python s13-instance-filter.py $^ | gzip > $@
	zcat $@ | wc

%.key:
	cp /ai/home/obaskaya/semeval13-task13/test_data/keys/gold/all.singlesense.key s13.key

### FASTSUBS ### 

FS_NSUB=100 # go until you have this many substitutes
FS_PSUB=1.0 # or this much cumulative probability
FS_OPTIONS=-n ${FS_NSUB} -p ${FS_PSUB}
export OMP_NUM_THREADS=${CPU}

%.sub.gz: %.context.gz ${LM}
	zcat $< | fastsubs-omp ${FS_OPTIONS} ${LM} | grep -P "^<.*\d>" | gzip > $@
	zcat $< | wc; zcat $@ | wc

### SCODE ###

SC_OPTIONS=-s ${SEED} -v -d 100

%.scode.gz: %.pairs.gz
	zcat $< | scode ${SC_OPTIONS} | gzip > $@

### Substitute KNN ###
%/subs: %-test.sub.gz
	-mkdir -p $@
	zcat $< | ./subs2dist.py $*

%/dists: %/subs
	-mkdir $@
	for i in `ls $<`; do\
		echo -n $$i"   ";\
		for d in 0 1 2 3 4; do\
			echo -n $$d", ";\
			python instance_mapper.py <(cat $</$$i | preinput.py | ../bin/dists -d $$d) <(cut -f1 $</$$i) |\
			gzip > $@/$$i.dist$$d.gz;\
			done; echo;\
	done

scores/%.knn.txt: %/dists %.key
	-mkdir scores/
	-rm $@ # remove for append below
	for i in `ls $< | sort`; do\
		echo -n $$i"   ";\
		for k in 1 2 3 4 5 6 7 8 10 12 15 20; do\
			echo -n $$k", ";\
			python knn.py $</$$i $$k $*.key >> $@;\
		done; echo;\
	done
	

%.clean: %
	rm -ri $*



