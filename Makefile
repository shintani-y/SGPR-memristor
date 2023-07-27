# file directory
file_dir = ./data/

# train test file
train_file = train_TriD_real_new2.csv
test_file = test_RanD_real_new2.csv

train = $(file_dir)$(train_file)
test = $(file_dir)$(test_file)

# Generate SGPR model
train:
	python sgpr_train.py $(train)

# Generate VerilogA model and Simulate with HSPICE
hspice:./HSPICE*/*.sp
	python params.py
	hspice64 -i ./HSPICE_test/1R.sp -o ./HSPICE_test/output/output
	hspice64 -i ./HSPICE_train/1R.sp -o ./HSPICE_train/output/output
	python read_plot_data.py $(train) $(test)

