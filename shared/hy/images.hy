(import [PIL.Image [open]] [base64 [b64encode b64decode]])

(defn get-image-bitmap [image-bytes]
  "Get the bitmap from a PNG image."
  (setv image (open image-bytes))
  (.convert image 'RGB))

(defn base-64-encode [image-bytes]
  "Base 64 encode an image."
  (-> image-bytes (b64encode) (.decode 'utf-8)))

(defn base-64-decode [base-64-encoded-image]
  "Base 64 decode an image."
  (b64decode base-64-encoded-image))

(defn base-64-encode-bitmap [bitmap]
  "Base 64 encode a bitmap."
  (-> (.tobytes bitmap) (b64encode) (.decode 'utf-8)))

(defn base-64-decode-bitmap [base-64-encoded-bitmap]
  "Base 64 decode a bitmap."
  (setv image (open (b64decode base-64-encoded-bitmap)))
  (.convert image 'RGB))
