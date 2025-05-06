import asyncio
import httpx
import time

API_KEY = "1ce42240deeab8e84bb50b73fb2c77c9"

async def resolver_captcha(sitekey, url):

    # 1. Enviar captcha a 2Captcha
    payload = {
        'key': API_KEY,
        'method': 'userrecaptcha',
        'googlekey': sitekey,
        'pageurl': url,
        'json': 1
    }

    async with httpx.AsyncClient() as client:
        r = await client.post('http://2captcha.com/in.php', data=payload)
        request_result = r.json()

    if request_result['status'] != 1:
        raise Exception("Error enviando captcha a 2Captcha")

    captcha_id = request_result['request']

    # 2. Esperar y consultar el resultado
    for _ in range(20):
        await asyncio.sleep(5)

        params = {
            'key': API_KEY,
            'action': 'get',
            'id': captcha_id,
            'json': 1
        }

        async with httpx.AsyncClient() as client:
            res = await client.get('http://2captcha.com/res.php', params=params)
            result = res.json()

        if result['status'] == 1:
            return result['request']

    raise Exception("Captcha no resuelto a tiempo")
