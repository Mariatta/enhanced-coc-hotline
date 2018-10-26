import os
from aiohttp import web


routes = web.RouteTableDef()


@routes.get("/")
async def main(request):
    return web.Response(text="The Hotline.")


if __name__ == "__main__":
    app = web.Application()
    app.router.add_routes(routes)

    port = os.environ.get("PORT")

    if port is not None:
        port = int(port)

    web.run_app(app, port=port)
