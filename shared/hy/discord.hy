(import discord os settings)

(defn format-message [message]
  (setv channel (. message channel))
  (setv author (. message author))

  (if (hasattr channel "name")
      (setv channel-name (. channel name))
      (setv channel-name (str "DM from " (. channel recipient name))))

  {
   "id" (. message id)
   "recipient" settings.DISCORD_CLIENT_USER_ID
   "recipient_name" settings.DISCORD_CLIENT_USER_NAME
   "created_at" (str (. message created_at))
   "raw_mentions" (. message raw_mentions)
   "author_name" (. author name)
   "guild" (. message guild id)
   "channel_name" channel-name
   "content" (. message content)
   "author" (. author id)
   "channel" (. channel id)
   }
  )
