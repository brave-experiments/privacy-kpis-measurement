all: split run

split:
	python3 splitTrace.py ../../crawls/
	
run:
	python3 statsRunner.py
	
clean:	clean_plots
	rm -rf browsers-traces/

plots:
	make -C plots/

clean_plots:
	make clean -C plots/