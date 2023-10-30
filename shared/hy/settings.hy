(import os)

(setv MIN-TEMP                    (float (.get os.environ "MIN_TEMP" 0.5))
      MAX-TEMP                    (float (.get os.environ "MAX_TEMP" 1.2))
      MONGODB-HOST-NAME           (.get os.environ "MONGODB_HOST_NAME" "mongo")
      MONGODB-ADMIN-DATABASE-NAME (.get os.environ "MONGODB_ADMIN_DATABASE_NAME" "database")
      MONGODB-ADMIN-USER_NAME     (.get os.environ "MONGODB_ADMIN_USER_NAME" "root")
      MONGODB-ADMIN-USER-PASSWORD (.get os.environ "MONGODB_ADMIN_USER_PASSWORD" "example")
      DISCORD-TOKEN               (.get os.environ "DISCORD_TOKEN")
      DISCORD-CLIENT-USER-ID      (.get os.environ "DISCORD_CLIENT_USER_ID")
      DISCORD-CLIENT-USER-NAME    (.get os.environ "DISCORD_CLIENT_USER_NAME")
      DEFAULT-CHANNEL             (.get os.environ "DEFAULT_CHANNEL")
      model-path                  "/app/models/duck_gpt.v0.2.0/")
(export
  :objects [MIN-TEMP
            MAX-TEMP
            MONGODB-HOST-NAME
            MONGODB-ADMIN-DATABASE-NAME
            MONGODB-ADMIN-USER_NAME
            MONGODB-ADMIN-USER-PASSWORD
            DISCORD-TOKEN
            DISCORD-CLIENT-USER-ID
            DISCORD-CLIENT-USER-NAME
            DEFAULT-CHANNEL
            model-path])
