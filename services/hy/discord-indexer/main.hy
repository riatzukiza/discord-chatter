(import asyncio [sleep]
        typing [List]
        discord [Intents Client TextChannel Message]
        shared.discord [format-message]
        shared.mongodb [discord-message-collection discord-channel-collection])

(import traceback shared.settings)

(def intents (discord.Intents.default))
(def client (discord.Client :intents intents))

(defn setup-channel [channel-id]
  "Setup a channel for indexing."
  (print (f"Setting up channel {channel-id}"))
  (discord-channel-collection.insert-one {"id" channel-id "cursor" None}))

(defn update-cursor [message]
  "Update the cursor for a channel."
  (print (f"Updating cursor for channel {(.channel message).id} to {(.id message)}"))
  (discord-channel-collection.update-one {"id" (.channel message).id} {"$set" {"cursor" (.id message)}}))

(defn index-message [message]
  "Index a message only if it has not already been added to mongo."
  (let [message-record (discord-message-collection.find-one {"id" (.id message)})]
    (if (none? message-record)
      (do
        (print (f"Indexing message {(.id message)} {(.content message)}"))
        (discord-message-collection.insert-one (format-message message)))
      (do
        (print (f"Message {(.id message)} already indexed"))
        (print message-record)))))

(defn find-channel-record [channel-id]
  "Find the record for a channel."
  (print (f"Finding channel record for {channel-id}"))
  (let [record (discord-channel-collection.find-one {"id" channel-id})]
    (if (none? record)
      (do
        (print (f"No record found for {channel-id}"))
        (setup-channel channel-id)
        (setv record (discord-channel-collection.find-one {"id" channel-id})))
      (do
        (print (f"Found channel record for {channel-id}"))
        (print (f"Channel record: {record}"))))
    record))

(defn/a next-messages [channel]
  "Get the next batch of messages in a channel."
  (let [channel-record (find-channel-record (.id channel))]
    (print (f"Cursor: {(:cursor channel-record)}"))
    (print (f"Getting history for {channel-record}"))
    (if (not (:is_valid channel-record true))
      (do
        (print (f"Channel {(:id channel-record)} is not valid"))
        [])
      (if (none? (:cursor channel-record))
        (do
          (print (f"No cursor found for {(:id channel-record)}"))
          (try
            [(await message) for message in (.history channel :limit 200 :oldest_first True)]
            (except Exception [e]
              (print (f"Error getting history for {(:id channel-record)}"))
              (print e)
              (discord-channel-collection.update-one {"id" (:id channel-record)} {"$set" {"is_valid" False}})
              []))
          (else
            (print (f"Cursor found for {channel} {(:cursor channel-record)}"))
            (try
              [(await message) for message in
               (.history channel :limit 200 :oldest_first True :after (.get_partial_message channel (:cursor channel-record)))]
              (except AttributeError [e]
                (print (f"Attribute error for {(.id channel)}"))
                []))))))))

(defn/a index-channel [channel]
  "Index all messages in a channel."
  (setv newest-message None)
  (print (f"Indexing channel {channel}"))
  (for [message (await (next-messages channel))]
    (await (sleep 0.1))
    (setv newest-message message)
    (index-message message))
  (if (not (none? newest-message))
    (update-cursor newest-message))
  (print (f"Newest message: {newest-message}")))

(defn shuffle-array [array]
  "Shuffle an array."
  (import random)
  (random.shuffle array)
  array)

(defn on-ready []
  (while True
    (for [channel (shuffle-array (list (client.get-all-channels)))]
      (if (isinstance channel discord.TextChannel)
        (do
          (print (f"Indexing channel {channel}"))
          (await (sleep 1))
          (await (index-channel channel)))))))

(.run client settings.DISCORD_TOKEN)
