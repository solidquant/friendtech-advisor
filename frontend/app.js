const Koa = require("koa");
const BodyParser = require("koa-bodyparser");
const Logger = require("koa-logger");
const serve = require("koa-static");
const mount = require("koa-mount");
const send = require("koa-send");
const cors = require('koa-cors');

const app = new Koa();

const static_pages = new Koa();
static_pages.use(serve(__dirname + "/build"));
app.use(mount("/", static_pages));
app.use(async (ctx) => {
    if (ctx.status === 404) {
        await send(ctx, "index.html", { root: __dirname + "/build" });
    }
});

const PORT = process.env.PORT || 3333;

app.use(BodyParser());
app.use(Logger());
app.use(cors());

app.listen(PORT, function () {
    console.log("==> 🌎  Listening on port %s. Visit http://localhost:%s/", PORT, PORT);
});