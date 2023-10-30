(import shared.nano_gpt.trainer [train_gpt_model setup_model]
        shared.nano_gpt.generator [generate_text_from_gpt_model]
        shared.training_data [get_messages_for_in_order_training]
        shared.settings [*]
        random [randint]
        os [path exists listdir]
        json [dumps]
        time [sleep])

(print "start building model" *model_path)
(setv [model model_args iter_num best_val_loss checkpoint scaler optimizer]
      (setup_model :out_dir *model_path
                   :learning_rate 6e-3
                   :device "cuda"
                   :init_from (if (and (exists *model_path) (> (len (listdir *model_path)) 0)) "resume" "gpt2-medium")))
(print "building model complete")

(while True
  (setv messages (get_messages_for_in_order_training (randint 20 100) (randint 10 100)))
  (print "training on messages " messages)

  (if messages
    (setv [model model_args iter_num best_val_loss checkpoint scaler optimizer]
          (train_gpt_model model iter_num best_val_loss checkpoint scaler optimizer model_args
                           :always_save_checkpoint True
                           :learning_rate 6e-5
                           :min_lr 6e-9
                           :out_dir *model_path
                           :input_data messages
                           :warmup_iters 2
                           :grad_clip 1
                           :max_iters 10))
    (print "no messages to train on")
    (continue)))
