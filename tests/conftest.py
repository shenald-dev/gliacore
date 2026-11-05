import os

# Disable heavy foundation model auto-loading during rapid unit testing
os.environ["GLIACORE_NO_AUTOLOAD"] = "1"
os.environ["NEURON_NO_AUTOLOAD"] = "1"
