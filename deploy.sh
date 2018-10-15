touch configs.json
echo "{
  "SECRET_KEY": "ThisIsARandomStringWithLength=50!-----------------",
  "DEBUG": true,
  "IGNORE_WECHAT_SIGNATURE": false,
  "WECHAT_TOKEN": "ThisIsAWeChatTokenWhichCanBeARandomString",
  "WECHAT_APPID": "PleaseCopyFromWebsite",
  "WECHAT_SECRET": "PleaseCopyFromWebsite",
  "DB_NAME": "wechat_ticket",
  "DB_USER": "root",
  "DB_PASS": "$DB_PWD",
  "DB_HOST": "127.0.0.1",
  "DB_PORT": "3306",
  "SITE_DOMAIN": "http://your.domain"
}" > configs.json