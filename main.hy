(import discord)
(import asyncio)
(import sys)
(import os)
(import random)
(import json)

(import discord)
(import asyncio)
(with-decorator client.event
  (defn/a on_ready []
    (print "Logged in as")
    (print client.user.name)
    (print client.user.id)))

(import [pathlib [Path]])

(import [textgenrnn [textgenrnn]] )

(setv client (.Client discord))

(setv textgen (textgenrnn "./json_message_model.hdf5"))

;; (.save textgen "./json_message_model.hdf5")
(setv messages (.load json (open "./log.json")))
(setv txt "")
(setv current_message_id 0)

(defn train (d e)
  (.train-on-texts textgen d None 128 e)
  (.save textgen "./json_message_model.hdf5"))

;; (defn save-message (content)
;;   (with (open mess)))

(with-decorator client.event
  (defn/a on_ready []
    (print "Logged in as")
    (print client.user.name)
    (print client.user.id)))

(with-decorator client.event
  (defn/a on_message [message]
    (global txt)
    (global current-message-id)

    (setv channel message.channel)
    (setv author message.author)
    (setv server channel.server)

    (setv i (+ current-message-id 1) )

    (setv currend-message-id i)

    (print (+ author.name ":" message.content))

    (when (eq message.author.id client.user.id)
      (print "not responding to self")
      (return))
    (try (setv message_json (.dumps json m
                                    :sort-keys True
                                    separators (tuple '("," ":"))
                                    )))
    ))

(.run client "NDQ5Mjc5NTcwNDQ1NzI5Nzkz.DeiaGQ.Fd7sBa0WSu_15utvWYDjEFy5HtY")

(print "foobar")
