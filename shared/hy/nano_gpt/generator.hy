(import tiktoken torch)
(import contextlib [nullcontext])

; Define the function to generate text
(defn generate-text-from-gpt-model [model &optional
                                    [device "cpu"]
                                    [seed 1337]
                                    [num-samples 1]
                                    [max-new-tokens 10000]
                                    [temperature 0.8]
                                    [top-k 200]
                                    [start "\n"]]

  (setv dtype (if (and (cuda.is_available)
                       (cuda.is_bf16_supported))
                  "bfloat16"
                  "float16")
        device-type (if (in "cuda" device) "cuda" "cpu")
        ptdtype (get {  "float32" torch.float32
                        "bfloat16" torch.bfloat16
                        "float16" torch.float16  } dtype)
        ctx (if (= device-type "cpu")
                (nullcontext)
                (torch.amp.autocast {"device-type" device-type
                                     "dtype" ptdtype}))
        enc (tiktoken.get_encoding "gpt2")
        start-ids (enc.encode_ordinary start)
        encode (fn [s] (enc.encode s :allowed_special #{"<|endoftext|>"}))
        decode (fn [] (enc.decode l))
        x (get (torch.tensor start-ids
                             :dtype torch.long
                             :device device) None ...))

  (model.eval)

  (with [(torch.no_grad)]
    (with [ctx]
      (for [k (range num-samples)]
        (setv y (model.generate x max-new-tokens
                                :encoder enc
                                :temperature temperature
                                :top_k top-k))
        (.append samples (.replace (decode (.tolist (first y) )) ""))))
    samples))
