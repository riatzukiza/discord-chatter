(import  shared.mongodb [discord-message-collection  duck-gpt]
         shared.settings  :as settings
         pymongo os json re)

(import os.path [ exists])
(discord-message-collection.create-index [#("id" pymongo.ASCENDING)])

(defn serialize-message [message]
  {"channel" (get message "channel")
   "channel_name" (get message "channel_name")
   "author_name" (get message "author_name") 
   "content" (get message "content")})

(defn collect-random-samples [[size 100]]
  (.aggregate discord-message-collection
              [{ "$match" { "recipient" settings.DISCORD_CLIENT_USER_ID 
                            "author"  {"$nin" [settings.DISCORD_CLIENT_USER_ID]}} }
               {"$sample" {"size" size}}]))

(defn collect-messages-from-pointer []
  (discord-message-collection.aggregate
    [{ "$match" {  "recipient" settings.DISCORD_CLIENT_USER_ID
                   "id" {"$gte" current-message-id }
                 "channel_name" {"$not" { "$regex" (re.compile "hemp|bot|spam|playground|brain|training|twitter")}}
                   "author_name" {"$nin" [ settings.DISCORD_CLIENT_USER_NAME
                                          "mr thing"
                                          "Jim"
                                          "Hivemind"
                                          "Timmy"]}}}
     { "$sort" { "id" pymongo.ASCENDING }}
     { "$limit" size }]))

(defn collect-samples-from-pointer [[size 100]  [current-message-id 0]]
  (discord-message-collection.aggregate
    [{"$match"{"recipient" settings.DISCORD_CLIENT_USER_ID
                 "id" { "$gte" current-message-id }
                 "channel_name" {"$not" {"$regex" (re.compile "hemp|bot|spam|playground|brain|training|twitter" )}}
                 "author_name" {"$nin"
                                [settings.DISCORD_CLIENT_USER_NAME
                                 "mr thing"
                                 "Jim"
                                 "Hivemind"
                                 "Timmy"]}}}
     {"$sort" {"id" pymongo.ASCENDING}}
     {"$limit" size}]))

(defn get-most-recent-messages [count]
  (discord-message-collection.aggregate
    [{"$sort" {"id" pymongo.DESCENDING}}
     { "$match"  { "recipient" settings.DISCORD_CLIENT_USER_ID 
                  "author_name" {"$nin" [
                                         settings.DISCORD_CLIENT_USER_NAME
                                         "mr thing"
                                         "Jim"
                                         "Hivemind"
                                         "Timmy"
                                         ]}
                  "channel_name" {"$not" {"$regex" (re.compile "hemp")}}} }
     {"$limit" count}
     {"$sort" {"id" pymongo.ASCENDING}}]))


(defn get-messages-for-inference [count]
  (list (map encode-sample
             (get-most-recent-messages count))))

(defn get-messages-for-training [&optional [frames 1000  ][size 100]] 
  (map (fn [n] (list (map serialize-message (get-random-messages size))))
       (range frames)))

(defn get_messages_for_in_order_training [frames size &optional [training_pointer_file "training_pointer.json"]]
  (setv current_message_id (if (exists training_pointer_file) (load (open training_pointer_file)) {"id" 0}))
  (setv training_data [])
  (dotimes [_ frames]
           (setv docs (collect_samples_from_pointer size :current_message_id current_message_id))
           (setv current_message (if (len docs) (last docs) latest_message))
           (setv current_message_id (.get current_message "id" current_message_id))
           (setv messages (list (map encode_sample docs)))
           (with [message-pointer (open "training_pointer.json" "w")]
             (.write message-pointer (json.dumps {"current_id" current_message_id})))
           (setv training_data (append training_data (list (json.dumps (list (map encode_sample messages)))))))
  training_data)
