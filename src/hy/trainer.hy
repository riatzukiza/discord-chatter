(import [textgenrnn [textgenrnn]] )
(import os)


(defn train (d e)
  (.train-on-texts textgen d None 128 e)
  (.save textgen "./relational.hdf5"))
