# -*- coding: utf-8 -*-

from logging import getLogger, StreamHandler, DEBUG, INFO
import json
import config
from requests_oauthlib import OAuth1Session

logger = getLogger(__name__)
handler = StreamHandler()
handler.setLevel(INFO)
logger.setLevel(INFO)
logger.addHandler(handler)
logger.propagate = False

screen_name = None
# screen_name = 'hie_dazs'


def main():

    twitter = OAuth1Session(config.CONSUMER_KEY, config.CONSUMER_SECRET,
                            config.ACCESS_TOKEN, config.ACCESS_TOKEN_SECRET)

    time_line_url = 'https://api.twitter.com/1.1/statuses/user_timeline.json'
    update_url = 'https://api.twitter.com/1.1/statuses/update.json'

    if screen_name is None:
        params = {'count': 100}
    else:
        params = {'count': 100, 'screen_name': screen_name}

    req = twitter.get(time_line_url, params=params)

    if req.status_code == 200:
        time_line = json.loads(req.text)
        for tweet in time_line:
            logger.debug('tweet: ' + tweet['text'])
            logger.debug('created at ' + tweet['created_at'])

            target = tweet['text']

            with open('keywords', 'r', encoding='utf-8') as f:
                for keyword in f:

                    keyword = keyword.replace('\r', '').replace('\n', '')

                    if not exists_keyword(keyword, target):
                        continue

                    result = mark_keyword(keyword, target)
                    result += ' // find_kani found kani【' + keyword + '】'
                    logger.info(result)

                    if screen_name is None:
                        tweet_text = '@' + tweet['user']['screen_name'] + ' ' + result
                    else:
                        tweet_text = '@' + screen_name + ' ' + result

                    while True:
                        print(tweet_text)
                        input_word = input('投稿しますか？（y/n） > ')

                        if input_word in {'y', 'Y'}:

                            params = {'status': tweet_text, 'in_reply_to_status_id': tweet['id']}
                            req = twitter.post(update_url, params=params)

                            if req.status_code == 200:
                                logger.info('succeed to post')
                            else:
                                print('POSTに失敗しました - エラーコード: %d' % req.status_code)
                                logger.warning('failed to post: %d' % req.status_code)

                            break

                        elif input_word in {'n', 'N'}:
                            print('キャンセルしました')
                            logger.info('canceled')
                            break

                        else:
                            continue

                    break

    else:
        print('タイムラインの取得に失敗しました - エラーコード: %d' % req.status_code)
        logger.warning('failed to get user time line: %d' % req.status_code)


def exists_keyword(keyword, target):

    offset = 0

    for char in keyword:
        offset = target.find(char, offset + 1)
        if offset < 0:
            return False

    return True


def mark_keyword(keyword, target):

    offset = 0

    for char in keyword:
        if offset == 0:
            cont = -1
        else:
            cont = target.find(char, offset + 1, offset + 2)

        if cont < 0:
            offset = target.find(char, offset + 1)
            target = target[0:offset] + '【' + target[offset:offset + 1] + '】' + target[offset + 1:]
            offset += 2
        else:
            target = target[0:cont - 1] + target[cont:cont + 1] + target[cont - 1:cont] + target[cont + 1:]
            offset = cont

    return target


if __name__ == '__main__':
    main()
