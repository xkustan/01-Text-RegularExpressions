import aiohttp
from aiohttp import web
import asyncio
import sys

DEFAULT_TIMEOUT = 1


def validate_url(raw_url=None):
    if not raw_url:
        raw_url = sys.argv[2]

    if "http://" not in raw_url:
        raw_url = "http://" + raw_url

    if "localhost" in raw_url:
        raw_url = "http://localhost:" + sys.argv[1]

    return raw_url


def validate_headers(raw_headers):
    new_headers = {
        "Accept": "*/*"
    }
    new_headers.update(raw_headers)
    if "Host" in new_headers.keys():
        del new_headers["Host"]

    return new_headers


async def get_handler(request):
    url_to_fwd = validate_url()
    headers_to_fwd = validate_headers(request.headers.copy())

    res = await forward_request(url_to_fwd, headers_to_fwd, "GET")
    return web.json_response(res)


async def post_handler(request):
    # check if request data is valid json
    try:
        data = await request.json()
        if "url" not in data:
            raise Exception("url missing!")
        if data.get("type", "GET") == "POST":
            if "content" not in data:
                raise Exception("content missing for POST request!")
    except:
        return web.json_response({"code": "invalid json"})

    url_to_fwd = validate_url(data["url"])
    headers_to_fwd = validate_headers(data.get("headers", {}))
    type_for_fwd = data.get("type", "GET")
    content_to_fwd = data.get("content", {})
    timeout_for_fwd = data.get("timeout", DEFAULT_TIMEOUT)

    res = await forward_request(url_to_fwd, headers_to_fwd, type_for_fwd, content_to_fwd, timeout_for_fwd)
    return web.json_response(res)


async def compose_fwd_response(response):
    client_res = {
        "code": response.status,
        "headers": {x: y for x, y in response.headers.items()}
    }

    try:
        client_res["json"] = await response.json()
    except:
        client_res["content"] = await response.text(encoding="utf-8")

    return client_res


async def forward_request(fwd_url, fwd_headers, fwd_type, fwd_content=None, fwd_timeout=DEFAULT_TIMEOUT):

    client_timeout = aiohttp.ClientTimeout(total=fwd_timeout)

    try:
        async with aiohttp.ClientSession(timeout=client_timeout, headers=fwd_headers) as session:
            if fwd_type == "GET":
                async with session.get(url=fwd_url) as response:
                    return await compose_fwd_response(response)
            elif fwd_type == "POST":
                async with session.post(url=fwd_url, data=fwd_content) as response:
                    return await compose_fwd_response(response)
            else:
                raise Exception("unknown request type")
    except asyncio.TimeoutError:
        return {"code": "timeout"}


def run_app(port):
    app = web.Application()
    app.add_routes([web.get('/{tail:.*}', get_handler),
                    web.post('/{tail:.*}', post_handler)])
    web.run_app(app, host='localhost', port=port)


if __name__ == '__main__':
    if len(sys.argv) != 3:
        sys.exit("First argument is port, second is upstream address")

    my_port = sys.argv[1]
    if int(my_port) < 9001:
        sys.exit("Por must be 9001 above")

    run_app(my_port)
