from bs4 import BeautifulSoup
import urllib
import random
import asyncio
import aiohttp


_externals = { "running": False }


def _initialise(Handlers, bot=None):
    Handlers.register_user_command(["meme"])
    return []


@asyncio.coroutine
def _retrieve(url, css_selector, attribute):
    print("_retrieve(): getting {}".format(url))
    html_request = yield from aiohttp.request('get', url)
    html = yield from html_request.read()
    soup = BeautifulSoup(str(html, 'utf-8'))
    links = []
    for link in soup.select(css_selector):
        links.append(link.get(attribute))
    return links


def meme(bot, event, *args):
    if _externals["running"]:
        bot.send_html_to_conversation(event.conv_id, "<i>busy, give me a moment...</i>")
        return

    _externals["running"] = True

    try:
        parameters = list(args)
        if len(parameters) == 0:
            parameters.append("robot")

        links = yield from _retrieve("http://memegenerator.net/memes/search?q=" + "+".join(parameters), ".item_medium_small > a", "href")
        links = yield from _retrieve("http://memegenerator.net" + random.choice(links), ".item_medium_small > a", "href")
        links = yield from _retrieve("http://memegenerator.net" + random.choice(links), ".instance_large > img", "src")

        if len(links) > 0:
            jpg_link = links.pop()
            the_request = yield from aiohttp.request('get', jpg_link)
            image_data = yield from the_request.read()

            photoID = yield from bot._client.upload_image(image_data)
            yield from bot._client.sendchatmessage(event.conv.id_, None, imageID=photoID)
        else:
            bot.send_html_to_conversation(event.conv_id, "<i>couldn't find a suitable meme :(</i>")
    except Exception as e:
        bot.send_html_to_conversation(event.conv_id, "<i>oh-uh, something went wrong! try again</i>")
    finally:
        _externals["running"] = False