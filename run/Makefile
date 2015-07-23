SHELL := /bin/bash

.SECONDARY:

### PATH
SRILM_PATH=/ai/opt/srilm/bin/i686-m64
LIBSVM_PATH=/ai/home/obaskaya/wsid/src/libsvm/svm-train

export PATH:=../bin/:.:${SRILM_PATH}:${PATH}

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

s13-test.context.gz: s13-test-all.context.gz s13-test.key
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

SC_OPTIONS=-s ${SEED} -v -d 100 -r 5 -t 0.0001
%.noun.scode.gz: sampled.noun.pairs.gz %.noun.pairs.gz
	zcat $^ | scode ${SC_OPTIONS} | gzip > $@

%.verb.scode.gz: sampled.verb.pairs.gz %.verb.pairs.gz
	zcat $^ | scode ${SC_OPTIONS} | gzip > $@

%.adj.scode.gz: sampled.adj.pairs.gz %.adj.pairs.gz
	zcat $^ | scode ${SC_OPTIONS} | gzip > $@

### Baselines ###

## Supervised Random Baseline ##

shuffled-supervised-random-baseline-%: %.key
	python scorer.py <(python supervised-random-baseline.py $< shuffled) $<

weighted-supervised-random-baseline-%: %.key
	python scorer.py <(python supervised-random-baseline.py $< shuffled) $<

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
	

### Substitute SVM
%/subs-svm: %/subs %.key
	-mkdir $@
	for fn in `ls $<`; do \
		echo $$fn processing;\
		python svmlib-input.py <(cat $</$$fn | cut -f1) <(cat $</$$fn | preinput.py) $*.key > $@/$$fn; \
	done

# No need to use easy because scaling is not necessary
# (we're using probability -- it's scaled [0,1] already)
%-subs-svm-scores.txt: %/subs-svm
	-rm $@.nm.tmp $@.tmp  # clear because of append in tee
	for fn in `ls $<`; do \
		echo $$fn processing;\
		../bin/grid.py -log2g -3,-15,-1 -out null -svmtrain ${LIBSVM_PATH} $</$$fn | tail -1 | tee -a $@.tmp;\
	done
	ls $< > $@.nm.tmp
	paste -d ' ' $@.nm.tmp $@.tmp > $@
	rm $@.nm.tmp $@.tmp
	-rm *.png *.scale *.range *.scale.out

### EMBEDDING CREATION

## 1. Original (--subs_embed_same) POS embeddings.

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

%/embeddings/XYw.global.scode.gz: %.global.scode.gz %.sub.gz
	-mkdir $*/embeddings
	python concat-XYw.py $< $^ --subs_embed_same 2>$*-XYw.global.err | gzip > $@  

%/embeddings/XYw.global2.scode.gz: %.global2.scode.gz %.sub.gz
	-mkdir $*/embeddings
	python concat-XYw.py $< $^ --subs_embed_same 2>$*-XYw.global2.err | gzip > $@  

# 1.1 Separation and creating directory for each target word.

s13-test/embeddings/orig-%: s13-test/embeddings/%.noun.scode.gz s13-test/embeddings/%.verb.scode.gz s13-test/embeddings/%.adj.scode.gz 
	-mkdir -p $@
	zcat $^ | python instance-sep.py $@

s10-test/embeddings/orig-%: s10-test/embeddings/%.noun.scode.gz s10-test/embeddings/%.verb.scode.gz
	-mkdir -p $@
	zcat $^ | python instance-sep.py $@

%/embeddings/global-XYw: %/embeddings/XYw.global.scode.gz
	-mkdir -p $@
	zcat $^ | python instance-sep.py $@

%/embeddings/global2-XYw: %/embeddings/XYw.global2.scode.gz
	-mkdir -p $@
	zcat $^ | python instance-sep.py $@

## 2. Other embeddings (Word vectors come from Pos-Based scode vectors; Context vectors come 
##    from various type of embedding representations.

# Run for all embeddings: 
# ls embeddings | grep -v simple | xargs -P 4 -I{} make s13-test/embeddings/{}.gz

s10-test/embeddings/%.gz: s10-test.noun.scode.gz s10-test.verb.scode.gz embeddings/% s10-test.sub.gz
	python concat-XYw.py <(zcat $< s10-test.verb.scode.gz) embeddings/$* s10-test.sub.gz --subs_embed_same --y-not-scode 2>s10-test-$*.err | gzip > $@

s13-test/embeddings/%.gz: s13-test.noun.scode.gz s13-test.verb.scode.gz s13-test.adj.scode.gz embeddings/% s13-test.sub.gz
	python concat-XYw.py <(zcat $< s13-test.verb.scode.gz s13-test.adj.scode.gz) embeddings/$* s13-test.sub.gz --subs_embed_same --y-not-scode 2>s13-test-$*.err | gzip > $@

# 2.1 Separation and creating directory for each target word.

# Run for all embeddings: 
# ls embeddings | grep -v simple | xargs -P 4 -I{} make s13-test/embeddings/{}

s10-test/embeddings/%: s10-test/embeddings/%.gz
	-mkdir -p $@
	zcat $^ | python instance-sep.py $@

s13-test/embeddings/%: s13-test/embeddings/%.gz
	-mkdir -p $@
	zcat $^ | python instance-sep.py $@

# 3. Y-based embeddings. Only Context Vector representation counts.

s10-test/embeddings/%-Y: s10-test/embeddings/%
	-mkdir -p $@
	for fn in `ls $<`; do \
		echo $$fn processing;\
		cat $</$$fn | cut -f1,2,103- > $@/$$fn;\
	done

s13-test/embeddings/%-Y: s13-test/embeddings/%
	-mkdir -p $@
	for fn in `ls $<`; do \
		echo $$fn processing;\
		cat $</$$fn | cut -f1,2,103- > $@/$$fn;\
	done

# 4. X-based embedding. Only for SCODE

%-test/embeddings/orig-XYw-X: %-test/embeddings/orig-XYw
	-mkdir -p $@
	for fn in `ls $<`; do \
		echo $$fn processing;\
		cat $</$$fn | cut -f1-103 > $@/$$fn;\
	done


### Embedding SVM

s10-test/%-svm: s10-test/embeddings/% s10-test.key # make s10-test/orig-XYw-svm
	-mkdir $@
	for fn in `ls $<`; do \
		echo $$fn processing;\
		python svmlib-input-embedding.py <(cat $</$$fn | cut -f1) $</$$fn s10-test.key > $@/$$fn; \
	done

s13-test/%-svm: s13-test/embeddings/% s13-test.key # make s13-test/orig-XYw-svm
	-mkdir $@
	for fn in `ls $<`; do \
		echo $$fn processing;\
		python svmlib-input-embedding.py <(cat $</$$fn | cut -f1) $</$$fn s13-test.key > $@/$$fn; \
	done

# Run for embeddings in embeddings/ directory.
# ls embeddings | grep -v simple | xargs -P 4 -I{} make s13-test-{}-svm-scores.txt

s10-test-%-scores.txt: s10-test/% # make s10-test-orig-XYw-svm-scores.txt
	-rm $@.nm.tmp $@.tmp  # clear because of append in tee
	for fn in `ls $<`; do \
		echo $$fn processing;\
		../bin/easy.py $</$$fn | grep Best | tee -a $@.tmp;\
	done
	ls $< > $@.nm.tmp
	paste -d ' ' $@.nm.tmp $@.tmp | sed -Ee 's|\w+=||g' -e "s|Best ||g" -e "s|CV ||g" -e "s|,||" > $@
	rm $@.nm.tmp $@.tmp

s13-test-%-scores.txt: s13-test/% # make s13-test-orig-XYw-svm-scores.txt
	-rm $@.nm.tmp $@.tmp  # clear because of append in tee
	for fn in `ls $<`; do \
		echo $$fn processing;\
		../bin/easy.py $</$$fn | grep Best | tee -a $@.tmp;\
	done
	ls $< > $@.nm.tmp
	paste -d ' ' $@.nm.tmp $@.tmp | sed -Ee 's|\w+=||g' -e "s|Best ||g" -e "s|CV ||g" -e "s|,||" > $@
	rm $@.nm.tmp $@.tmp


### Embedding KNN ###

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

### Clustering


### AD-HOC targets

global.scode.gz: global.pairs.gz s13-test.verb.pairs.gz s13-test.noun.pairs.gz s13-test.adj.pairs.gz s10-test.verb.pairs.gz s10-test.noun.pairs.gz
	cat <(zcat $<) <(zcat s13-test.verb.pairs.gz s13-test.noun.pairs.gz s13-test.adj.pairs.gz | sed 's|^<|<s13.|g') <(zcat s10-test.verb.pairs.gz s10-test.noun.pairs.gz | sed 's|^<|<s10.|g') | scode ${SC_OPTIONS} | gzip > $@

s13-test.global.scode.gz: global.scode.gz
	zcat $< | grep -vP '^0:<s10' | sed 's|^0:<s13.|0:<|g' | gzip > $@
	#zcat $< | grep -P '^0:<s13' | sed 's|^0:<s13.|0:<|g' | gzip > $@ # target words only

s10-test.global.scode.gz: global.scode.gz
	zcat $< | grep -vP '^0:<s13' | sed 's|^0:<s10.|0:<|g' | gzip > $@
	#zcat $< | grep -P '^0:<s10' | sed 's|^0:<s10.|0:<|g' | gzip > $@  # target words only

additional.global.scode.gz: global.scode.gz
	zcat $< | grep -vP '^0:<s1[03]' | gzip > $@

global2.scode.gz: sampled.adj.pairs.gz sampled.verb.pairs.gz sampled.noun.pairs.gz s13-test.verb.pairs.gz s13-test.noun.pairs.gz s13-test.adj.pairs.gz s10-test.verb.pairs.gz s10-test.noun.pairs.gz
	cat <(zcat sampled.adj.pairs.gz sampled.verb.pairs.gz sampled.noun.pairs.gz) <(zcat s13-test.verb.pairs.gz s13-test.noun.pairs.gz s13-test.adj.pairs.gz | sed 's|^<|<s13.|g') <(zcat s10-test.verb.pairs.gz s10-test.noun.pairs.gz | sed 's|^<|<s10.|g') | scode ${SC_OPTIONS} | gzip > $@

s13-test.global2.scode.gz: global2.scode.gz
	zcat $< | grep -vP '^0:<s10' | sed 's|^0:<s13.|0:<|g' | gzip > $@
	#zcat $< | grep -P '^0:<s13' | sed 's|^0:<s13.|0:<|g' | gzip > $@ # target words only

s10-test.global2.scode.gz: global2.scode.gz
	zcat $< | grep -vP '^0:<s13' | sed 's|^0:<s10.|0:<|g' | gzip > $@
	#zcat $< | grep -P '^0:<s10' | sed 's|^0:<s10.|0:<|g' | gzip > $@  # target words only

## Cleaning 

%.clean: %
	rm -ri $*
	#cat $< | grep -P "k = $$k$$" | grep -P "$$d" | awk 'BEGIN{sum=0}{sum+=$$4}END{printf("%s\t%s\t%f\n", $$d, $$k, sum/NR)}';\

clean-svmlib: 
	-rm *.png *.scale *.range *.scale.out
