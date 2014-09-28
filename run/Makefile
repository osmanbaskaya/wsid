SHELL := /bin/bash

.SECONDARY:

### PATH
SRILM_PATH=/ai/opt/srilm/bin/i686-m64

export PATH:=.:${SRILM_PATH}:${PATH}:../bin:

SEED=1
CPU=25
LM=enw.lm.gz
SCORER= java -jar ../data/evaluation/task-3-scorer.jar

bin:
	cd ../bin; make

enw.lm.gz:
	ln -s /ai/work/upos_phd/run/enw_ukvac2/enw.lm.gz

sampled.%.sub.gz:
	ln -s /ai/home/obaskaya/semeval13-task13/run/$*.sub.gz $@

../data/s10/%_data.tar.gz: # make ../data/s10/[test/training]_data.tar.gz 
	-mkdir ../data/s10/
	wget http://www.cs.york.ac.uk/semeval2010_WSI/files/$*_data.tar.gz
	mv $*_data.tar.gz $@
	tar xzf $@

../bin/ss.jar: /ai/home/obaskaya/semeval13-task13/test_data/scoring/single-sense-precision.jar
	cp $< $@

s13-test-all.context.gz: 
	ln -s /ai/home/obaskaya/semeval13-task13/run/test.context.gz $@

s13-test.context.gz: s13-test-all.context.gz s13.key
	python s13-instance-filter.py $^ | gzip > $@
	zcat $@ | wc

s13-test.key:
	cp /ai/home/obaskaya/semeval13-task13/test_data/keys/gold/all.singlesense.key $@

s10-test.key: s10-test-context-fetch.err
	python filterer.py $< <(cat ../data/s10/*.key | sort |\
	uniq | grep -v "^$$") 0 1 exclude > $@

TEST_S10=$(shell find ../data/s10/test_data -name "*.[nv].xml" | sort)
s10-test.gz: ../data/s10/test_data
	python s10-fetch.py ${TEST_S10} | gzip > $@

TRAIN_S10=$(shell find ../data/s10/training_data -name "*.[nv].xml" | sort)
s10-train.gz: ../data/s10/training_data
	python s10-fetch.py ${TRAIN_S10} #| gzip > $@

s10-%.context.gz s10-%-context-fetch.err: s10-%.gz
	zcat $< | python s10-context-fetch.py 2>s10-$*-context-fetch.err | gzip > s10-$*.context.gz
	zcat $< | wc; zcat s10-$*.context.gz | wc; wc s10-$*-context-fetch.err

### FASTSUBS ### 

FS_NSUB=100 # go until you have this many substitutes
FS_PSUB=1.0 # or this much cumulative probability
FS_OPTIONS=-n ${FS_NSUB} -p ${FS_PSUB}
export OMP_NUM_THREADS=${CPU}

%.sub.gz: %.context.gz ${LM}
	zcat $< | fastsubs-omp ${FS_OPTIONS} ${LM} | grep -P "^<.*\d>" | gzip > $@
	zcat $< | wc; zcat $@ | wc


### Wordsub ###

## 1. Pos-Based ##
sampled.%.pairs.gz: sampled.%.sub.gz
	ln -s /ai/home/obaskaya/uwsd/run/$*.pairs.gz $@

%.noun.pairs.gz: %.sub.gz
	zcat $< | grep -P "^<.*\.n\." | python wordsub.py 100 ${SEED} | gzip > $@
	zcat $< | grep -P "^<.*\.n\." | wc; zcat $@ | wc

%.verb.pairs.gz: %.sub.gz
	zcat $< | grep -P "^<.*\.v\." | python wordsub.py 100 ${SEED} | gzip > $@
	zcat $< | grep -P "^<.*\.v\." | wc; zcat $@ | wc

%.adj.pairs.gz: %.sub.gz
	zcat $< | grep -P "^<.*\.j\." | python wordsub.py 100 ${SEED} | gzip > $@
	zcat $< | grep -P "^<.*\.j\." | wc; zcat $@ | wc

## 2. Instance-based ##
%.pairs.gz: %.sub.gz
	zcat $< | python wordsub.py 100 ${SEED} | gzip > $@
	zcat $< | wc; zcat $@ | wc


### SCODE ###

SC_OPTIONS=-s ${SEED} -v -d 100
%.noun.scode.gz: sampled.noun.pairs.gz %.noun.pairs.gz
	zcat $^ | scode ${SC_OPTIONS} | gzip > $@

%.verb.scode.gz: sampled.verb.pairs.gz %.verb.pairs.gz
	zcat $^ | scode ${SC_OPTIONS} | gzip > $@

%.adj.scode.gz: sampled.adj.pairs.gz %.adj.pairs.gz
	zcat $^ | scode ${SC_OPTIONS} | gzip > $@

### Baselines ###

## Supervised Random Baseline ##

supervised-random-baseline-%: %.key
	python scorer.py <(python supervised-random-baseline.py $<) $<

induced-random-baseline-%: %.key ../bin/ss.jar # make induced-random-baseline-s13-test NUM_SENSE=3
	python random-baseline.py $< ${NUM_SENSE} > /tmp/$@.${NUM_SENSE}
	java -jar ../bin/ss.jar -s $< /tmp/$@.${NUM_SENSE} 

induced-gold-n-random-baseline-%: %.key ../bin/ss.jar
	python random-baseline-gold-n.py $< > /tmp/$@
	java -jar ../bin/ss.jar -s $< /tmp/$@

### Substitute KNN ###

%/subs: %.sub.gz
	-mkdir -p $@
	zcat $< | python instance-sep.py $@

%/dists: %/subs
	-mkdir $@
	touch $@
	for i in `ls $<`; do\
		echo -n $$i"   ";\
		for d in 0 1 2 3 4; do\
			echo -n $$d", ";\
			python instance_mapper.py <(cat $</$$i | preinput.py | ../bin/dists -d $$d) <(cut -f1 $</$$i) |\
			gzip > $@/$$i.dist$$d.gz;\
			done; echo;\
	done

scores/%.knn-mv.txt: %/dists %.key # mv=majority voting 
	-mkdir scores/
	-rm $@ # remove for append below
	for i in `ls $< | sort`; do\
		echo -n $$i"   ";\
		for k in 1 2 3 4 5 6 7 8 10 12 15 20; do\
			echo -n $$k", ";\
			python knn.py $$k majority_voting $</$$i $*.key >> $@;\
		done; echo;\
	done

scores/%.knn-mad.txt: %/dists %.key # mad=min_avg_dist
	-mkdir scores/
	-rm $@ # remove for append bel
	for i in `ls $< | sort`; do\
		echo -n $$i"   ";\
		for k in 1 2 3 4 5 6 7 8 10 12 15 20; do\
			echo -n $$k", ";\
			python knn.py $$k min_avg_dist $</$$i $*.key >> $@;\
		done; echo;\
	done

%.knn-mad.tab: scores/%.knn-mad.txt 
	-rm $@ # remove for append below
	for d in ${DISTS}; do\
		for k in 1 2 3 4 5 6 7 8 10 12 15 20; do\
			echo -ne "dist"$$d'\t'$$k'\t' >> $@;\
			cat $< | grep -P "k = $$k$$" | grep -P "dist$$d" | awk '{sum+=$$4}END{print sum/NR}' >> $@;\
		done;\
		echo >> $@;\
	done;

%.knn-mv.tab: scores/%.knn-mv.txt # call exp: make s10-test.orig-XYw-dists.knn-mv.tab DISTS="0 1 2 3"
	-rm $@ # remove for append below
	for d in ${DISTS}; do\
		for k in 1 2 3 4 5 6 7 8 10 12 15 20; do\
			echo -ne "dist"$$d'\t'$$k'\t' >> $@;\
			cat $< | grep -P "k = $$k$$" | grep -P "dist$$d" | awk '{sum+=$$4}END{print sum/NR}' >> $@;\
		done;\
		echo >> $@;\
	done;
	
### Embedding KNN ###

## Original (--subs_embed_same) POS embeddings.

%/embeddings/XYw.noun.scode.gz: %.noun.scode.gz %.sub.gz
	-mkdir $*/embeddings
	python concat-XYw.py $< $^ --subs_embed_same 2>$*-XYw.noun.err | gzip > $@

%/embeddings/XYw.verb.scode.gz: %.verb.scode.gz %.sub.gz
	-mkdir $*/embeddings
	python concat-XYw.py $< $^ --subs_embed_same 2>$*-XYw.verb.err | gzip > $@  

%/embeddings/XYw.adj.scode.gz: %.adj.scode.gz %.sub.gz
	-mkdir $*/embeddings
	python concat-XYw.py $< $^ --subs_embed_same 2>$*-XYw.adj.err | gzip > $@  

%/embeddings/XYb.noun.scode.gz: %.noun.scode.gz %.noun.pairs.gz
	-mkdir $*/embeddings
	python concat-XYb.py $^ 2>$*-XYb.noun.err | gzip > $@

%/embeddings/XYb.verb.scode.gz: %.verb.scode.gz %.verb.pairs.gz
	-mkdir $*/embeddings
	python concat-XYb.py $^ 2>$*-XYb.verb.err | gzip > $@ 

%/embeddings/XYb.adj.scode.gz: %.adj.scode.gz %.adj.pairs.gz
	-mkdir $*/embeddings
	python concat-XYb.py $^ 2>$*-XYb.adj.err | gzip > $@ 

s13-test/embeddings/orig-%: s13-test/embeddings/%.noun.scode.gz s13-test/embeddings/%.verb.scode.gz s13-test/embeddings/%.adj.scode.gz 
	-mkdir -p $@
	zcat $^ | python instance-sep.py $@

s10-test/embeddings/orig-%: s10-test/embeddings/%.noun.scode.gz s10-test/embeddings/%.verb.scode.gz
	-mkdir -p $@
	zcat $^ | python instance-sep.py $@

s13-test/embeddings/%-dists: s13-test/embeddings/%
	-mkdir $@; touch $@
	for i in `ls $<`; do\
		echo -n $$i"   ";\
		for d in 0 1 2 3; do\
			echo -n $$d", ";\
			python instance_mapper.py <(cat $</$$i | python predist.py | ../bin/dists -d $$d) <(cut -f1 $</$$i) |\
			gzip > $@/$$i.dist$$d.gz;\
			done; echo;\
	done

s10-test/embeddings/%-dists: s10-test/embeddings/%
	-mkdir $@; touch $@
	for i in `ls $<`; do\
		echo -n $$i"   ";\
		for d in 0 1 2 3; do\
			echo -n $$d", ";\
			python instance_mapper.py <(cat $</$$i | python predist.py | ../bin/dists -d $$d) <(cut -f1 $</$$i) |\
			gzip > $@/$$i.dist$$d.gz;\
			done; echo;\
	done

scores/s13-test.%.knn-mv.txt: s13-test/embeddings/% s13-test.key # mv=majority voting 
	-mkdir scores/
	-rm $@ # remove for append below
	for i in `ls $< | sort`; do\
		echo -n $$i"   ";\
		for k in 1 2 3 4 5 6 7 8 10 12 15 20; do\
			echo -n $$k", ";\
			python knn.py $$k majority_voting $</$$i s13-test.key >> $@;\
		done; echo;\
	done

scores/s13-test.%.knn-mad.txt: s13-test/embeddings/% s13-test.key # mad=min_avg_dist
	-mkdir scores/
	-rm $@ # remove for append bel
	for i in `ls $< | sort`; do\
		echo -n $$i"   ";\
		for k in 1 2 3 4 5 6 7 8 10 12 15 20; do\
			echo -n $$k", ";\
			python knn.py $$k min_avg_dist $</$$i s13-test.key >> $@;\
		done; echo;\
	done

scores/s10-test.%.knn-mv.txt: s10-test/embeddings/% s10-test.key # mv=majority voting 
	-mkdir scores/
	-rm $@ # remove for append below
	for i in `ls $< | sort`; do\
		echo -n $$i"   ";\
		for k in 1 2 3 4 5 6 7 8 10 12 15 20; do\
			echo -n $$k", ";\
			python knn.py $$k majority_voting $</$$i s10-test.key >> $@;\
		done; echo;\
	done

scores/s10-test.%.knn-mad.txt: s10-test/embeddings/% s10-test.key # mad=min_avg_dist
	-mkdir scores/
	-rm $@ # remove for append bel
	for i in `ls $< | sort`; do\
		echo -n $$i"   ";\
		for k in 1 2 3 4 5 6 7 8 10 12 15 20; do\
			echo -n $$k", ";\
			python knn.py $$k min_avg_dist $</$$i s10-test.key >> $@;\
		done; echo;\
	done

%.clean: %
	rm -ri $*
	#cat $< | grep -P "k = $$k$$" | grep -P "$$d" | awk 'BEGIN{sum=0}{sum+=$$4}END{printf("%s\t%s\t%f\n", $$d, $$k, sum/NR)}';\
