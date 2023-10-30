(import torch
        time
        math
        os
        tiktoken
        numpy [np]
        contextlib [nullcontext]
        shared.nano_gpt.model [GPTConfig GPT]
        )

                                ; Define the default data type and other configuration options
(setv dtype (if (and (. cuda is_available) (. cuda is_bf16_supported))
                'bfloat16
                'float16)
      master-process True
      seed-offset 0
      ddp-world-size 1)

                                ; Set the random seed
(torch.manual_seed (+ 1337 seed-offset))

                                ; Enable TF32 on matmul and CuDNN if available
(. torch.backends.cudnn allow_tf32 True)

                                ; Define the `setup-model` function
(defn setup-model [out-dir &optional [init-from "scratch"] [block-size 1024] [device "cuda"]
                   [n-layer 12] [n-head 12] [n-embd 768] [bias False] [dropout 0.2]
                   [weight-decay 1e-1] [learning-rate 6e-4] [beta1 0.9] [beta2 0.95]]

  (os.makedirs out-dir :exist-ok True)
  (setv iter-num 0
        device-type (if (in "cuda" device) "cuda" "cpu")
        ctx (if (= device-type "cpu")
                (nullcontext)
                (torch.amp.autocast :device-type device-type :dtype ptdtype))
        best-val-loss 1e9
        model-args {
                    "n_layer" n-layer
                    "n_head" n-head
                    "n_embd" n-embd
                    "block_size" block-size
                    "bias" bias
                    "vocab_size" None
                    "dropout" dropout
                    } ; Start with model_args from the command line
        model (cond  (= init-from "scratch") (init-from-scratch model-args)

                     (= init-from "resume")
                      (let [[model checkpoint] (resume-model out-dir model-args :device device)
                            iter-num (.get checkpoint "iter_num")
                            best-val-loss (.get checkpoint "best_val_loss")])
                      (init-from.startswith "gpt2")
                      (do (print (+ "Initializing from OpenAI GPT-2 weights: " init-from))
                          (let [override-args {"dropout" dropout}]
                            (GPT.from-pretrained init-from override-args)))
                     (raise (Exception "Improperly formatted init-from"))))

  (if (< block-size (model.config.block-size))
      (. model crop-block-size block-size)
      ; So that the checkpoint will have the right value
      (set model-args "block_size" block-size))
  (. model to device)
  (print "compiling the model... (takes about a minute)")
  (setv model (torch.compile model)
        scaler (torch.cuda.amp.GradScaler :enabled (= dtype ""))
        optimizer (model.configure-optimizers
                    weight-decay
                    learning-rate
                    [ beta1 beta2]
                    device-type))

  (if (= init-from "resume") (.load-state-dict optimizer (checkpoint "optimizer")))
  {

   "model" model
   "model_args" model-args
   "iter_num" iter-num
   "best_val_loss" best-val-loss
   "config" {"n_layer" n-layer "n_head" n-head "n_embd" n-embd "block_size" block-size
             "bias" bias "vocab_size" None "dropout" dropout}})
                          ; Define the `encode-document` function
(defn encode-document [doc encoder]
  (setv ids (encoder.encode-ordinary doc))
  (.append ids (encoder.eot-token))
  ids)

                                ; Define the `encode-training-documents` function
(defn encode-training-documents [documents encoder]
  (setv data []
        document-ids []
        current-document-id 0)

  (for [document documents]
    (setv ids (encode-document document encoder))
    (setv data (extend data ids)))

  (list data document-ids))

                                ; Define the `split-documents-for-evaluation` function
(defn split-documents-for-evaluation [documents split encoder]
  (let [document-data document-ids (encode-training-documents documents encoder)
        n (len document-data)
        training-data (np.array document-data[: (int (* n split))] :dtype np.uint16)
        evaluation-data (np.array document-data[(int (* n split)):] :dtype np.uint16)]
    [training-data evaluation-data]))

                                ; Define the `estimate-loss` function
(defn estimate-loss []
  (with [(torch.no-grad)]
    (setv out {})
    (. model eval)
    (for [split ['train' 'val']]
      (setv losses (torch.zeros eval-iters))
      (for [k (range eval-iters)]
        (let [X Y (get-batch split)]
          (with [ctx]
            (let [logits loss (. model X Y)]
              (aset losses k (. item loss)))))))))
