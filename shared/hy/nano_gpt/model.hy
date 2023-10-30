(import torch
        [torch.nn [Module Linear Embedding Dropout LayerNorm]]
        [torch.nn.functional [layer-norm softmax]]
        [math [sqrt]]
        [dataclasses [dataclass]])

(defclass LayerNorm [Module]
  "LayerNorm but with an optional bias. PyTorch doesn't support simply bias=False"
  (defn __init__ [self ndim bias]
    (super __init__)
    (setv self.weight (Parameter (torch.ones ndim))
          self.bias (if bias (Parameter (torch.zeros ndim)) None))

  (defn forward [self input]
    (layer-norm input self.weight.shape self.weight self.bias 1e-5))

(defclass CausalSelfAttention [Module]
  (defn __init__ [self config]
    (super __init__)
    (assert (== (% config.n-embd config.n-head) 0))
    (setv self.c-attn (Linear config.n-embd (* 3 config.n-embd) :bias config.bias)
          self.c-proj (Linear config.n-embd config.n-embd :bias config.bias)
          self.attn-dropout (Dropout config.dropout)
          self.resid-dropout (Dropout config.dropout)
          self.n-head config.n-head
          self.n-embd config.n-embd
          self.dropout config.dropout
          self.flash (if (hasattr torch.nn.functional 'scaled-dot-product-attention') True False))

  (if (not self.flash)
    (print "WARNING: using slow attention. Flash Attention requires PyTorch >= 2.0")
    (setv self.bias
          (-> (torch.tril (torch.ones config.block-size config.block-size))
              (view 1 1 config.block-size config.block-size))))

  (defn forward [self x]
    (setv B T C (.size x))  ; batch size, sequence length, embedding dimensionality (n-embd)

    (setv q k v (.split (.c-attn x) self.n-embd 2)
          k (-> k (.view B T self.n-head (/ C self.n-head)) (.transpose 1 2))
          q (-> q (.view B T self.n-head (/ C self.n-head)) (.transpose 1 2))
          v (-> v (.view B T self.n-head (/ C self.n-head)) (.transpose 1 2))

    (if self.flash
      (setv y (torch.nn.functional.scaled-dot-product-attention q k v :attn-mask None :dropout-p (if (.training self) self.dropout 0) :is-causal True))
      (setv att (-> (matmul q (transpose k -2 -1)) (/ (sqrt (.size k -1))))
            att (-> att (.masked-fill (== self.bias 0) float('-inf')))
            att (softmax att -1))
      (setv y (matmul att v)))

    (setv y (-> y (.transpose 1 2) (.contiguous) (.view B T C))
    (setv y (-> y (.c-proj) (.resid-dropout)))
    y))

(defclass MLP [Module]
  (defn __init__ [self config]
    (super __init__)
    (setv self.c-fc (Linear config.n-embd (* 4 config.n-embd) :bias config.bias)
          self.gelu (nn.GELU)
          self.c-proj (Linear (* 4 config.n-embd) config.n-embd :bias config.bias)
          self.dropout (Dropout config.dropout))

  (defn forward [self x]
    (setv x (-> x (.c-fc) (.gelu) (.c-proj) (.dropout))
    x))

(defclass Block [Module]
  (defn __init__ [self config]
    (super __init__)
    (setv self.ln-1 (LayerNorm config.n-embd :bias config.bias)
          self.attn (CausalSelfAttention config)
          self.ln-2 (LayerNorm config.n-embd :bias config.bias)
          self.mlp (MLP config))

  (defn forward [self x]
    (setv x (+ x (-> (.attn (.ln-1 x)))
          x (+ x (-> (.mlp (.ln-2 x))))
          x)))

(defclass GPTConfig [dataclass]
  :block-size 1024
  :vocab-size 50304
  :n-layer 12
  :n-head 12
  :n-embd 768
  :dropout 0.0
  :bias True)

(defclass GPT [Module]
  (defn __init__ [self config]
    (super __init__)
    (assert (not (none? config.vocab-size))
    (assert (not (none? config.block-size))
    (setv self.config config)
    (setv self.transformer (ModuleDict
                          wte (Embedding config.vocab-size config.n-embd)
                          wpe (Embedding config.block-size config.n-embd)
                          drop (Dropout config.dropout)
                          h (ModuleList (comprehension [_ _] [_ (Block config) (_ range config.n-layer)]))
                          ln-f (LayerNorm config.n-embd :bias config.bias)))
    (setv self.lm-head (Linear config.n-embd config.vocab-size :bias False))
    (setv self.transformer.wte.weight self.lm-head.weight)
    (self _init-weights)
    (setv (setv self._init-weights
                (fn [module]
                  (if (isinstance module nn.Linear)
                    (-> module (.weight torch.nn.init.normal_ 0.0 (/ 0.02 (sqrt (* 2 config.n-layer))))
                    (if (not (none? (.bias module)))
                      (-> (.bias module) torch.nn.init.zeros_))))))))

  (defn _init-weights [self module]
    (if (isinstance module nn.Linear)
      (-> module (.weight torch.nn.init.normal_ 0.0 (/ 0.02)))
      (if (not (none? (.bias module)))
        (-> (.bias module) torch.nn.init.zeros_))))
  
  (defn forward [self idx targets]
    (setv device (.device idx)
    (setv B T (.size idx))
    (assert (<= T self.config.block-size))
    (setv pos (-> (arange 0 T dtype=torch.long device=device))
    (setv tok-emb (-> (.transformer.wte idx))
    pos-emb (-> (.transformer.wpe pos))
    x (-> (.transformer.drop (+ tok-emb pos-emb)))
    (for block (.transformer.h)
      (setv x (-> block x)))
    (setv x (-> (.transformer.ln-f x))
    (if (not (none? targets))
      (setv
