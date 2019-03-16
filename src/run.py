import data_cleanup
import identification

print "Fetching data"
data = data_cleanup.get_data("train_data_noorder")
print "Starting identification"
identification.perform_identification(data[0],data[1])
