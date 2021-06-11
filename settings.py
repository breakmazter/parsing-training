########################
# CONFIGS FOR RABBITMQ #
########################

RABBITMQ_HOST = '34.145.90.213'
RABBITMQ_PORT = 5672
RABBITMQ_VHOST = '/'
RABBITMQ_LOGIN = 'user'
RABBITMQ_PASSWORD = '12JqEf2T5Fn6QZCF'

RABBITMQ_URL = f'''amqp://{RABBITMQ_LOGIN}:{RABBITMQ_PASSWORD}@{RABBITMQ_HOST}:{RABBITMQ_PORT}'''

#####################
# CONFIGS FOR REDIS #
#####################

REDIS_HOST = '34.83.238.11'
REDIS_PORT = 6379
REDIS_USERNAME = 'user'
REDIS_PASSWORD = 'LYWxyNDJSg7h'

########################
# CONFIGS FOR POSTGRES #
########################

POSTGRES_HOST = '127.0.0.1'
POSTGRES_PORT = 5432
POSTGRESS_DB = 'devby_db'
POSTGRES_LOGIN = 'postgres'
POSTGRES_PASSWORD = 'HsLcpxodIfPCo9rH'
POSTGRES_URL = f'postgresql://{POSTGRES_LOGIN}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRESS_DB}'

#######################
# CONFIGS FOR PARSING #
#######################

HEADERS = {
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.101 "
                  "Safari/537.36",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,"
              "application/signed-exchange;v=b3;q=0.9",
}
MAIN_PAGE = "https://companies.dev.by/"
