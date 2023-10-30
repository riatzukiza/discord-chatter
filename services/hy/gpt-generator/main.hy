(import shared.settings :as settings)
(import os re random json datetime)

(import shared.mongodb [discord-message-collection  generated-message-collection duck-gpt])

(import shared.training_data [collect-random-samples serialize-message get-most-recent-messages get-messages-for-inference])

(import shared.nano_gpt.generator [generate-text-from-gpt-model])
(import shared.nano_gpt.trainer [setup-model encode-document])


(setv service-started (datetime.utcnow))
(setv model-loaded (datetime.utcnow))

(defn get-frame []
  (encode-sample (duck-gpt.find-one)))

(defn dir-is-not-empty [path]
  (and (os.path.exists path)
       (> (len (os.listdir path)) 0)))

(defn generate-frame [sample-size]
  (let [prefix-samples (get-messages-for-inference sample-size)
        prefix "["]
    (for [sample prefix-samples]
      (setv prefix (+ prefix (json.dumps (encode-sample sample) :separators ["," ":"]) ",")))
    prefix))

(while True
  (let [[model model-args iter-num best-val-loss checkpoint scaler optimizer]
        (setup-model
          :out-dir model-path
          :device "cuda"
          :init-from (if (dir-is-not-empty model-path) "resume" "gpt2-medium"))
        started (datetime.utcnow)
        sample-size (random.randint 5 100)
        prefix (generate-frame :sample-size sample-size)
        temp (random.uniform (float MIN-TEMP) (float MAX-TEMP))
        sample (generate-text-from-gpt-model
                :model model
                :seed (random.randint 0 99999999)
                :temperature temp
                :device "cuda"
                :start prefix
                :max-new-tokens 10000)]
    (print "sample generated" sample)
    (setv finished (datetime.utcnow))

    (print "batch complete, saving samples")
    (setv sample-data (json.loads sample))

    (print "generated" (len sample-data) "samples")
    (setv generated-messages (get slice sample-data sample-size None))

    (print generated-messages)
    (setv is-valid True)

    (print "valid sample:" sample)
    (generated-message-collection.insert-one
      {"sample_text" (json.dumps generated-messages)
       "temp" temp
       "started" started
       "finished" finished
       "model" model-path
       "is_valid" is-valid
       "sent" False})))
