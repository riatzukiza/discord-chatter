(import os
        pymongo [MongoClient]
        shared.settings [MONGODB-HOST-NAME MONGODB-ADMIN-DATABASE-NAME])

(setv CONNECTION-STRING (str (+ "mongodb://" MONGODB-HOST-NAME "/" MONGODB-ADMIN-DATABASE-NAME)))

(defn get-database []
  (setv client (MongoClient CONNECTION-STRING))
  (get client MONGODB-ADMIN-DATABASE-NAME))

(when (= __name__ "__main__") (setv dbname (get-database)))

(setv db (get-database))
(setv discord-message-collection (get db "discord_messages"))
(setv generated-message-collection (get db "generated_messages"))
(setv discord-channel-collection (get db "discord_channels"))
(setv discord-user-collection (get db "discord_users"))
(setv discord-server-collection (get db "discord_servers"))
(setv duck-gpt (get db "duck_gpt"))
