from g4f.gui import run_gui
from g4f.cookies import set_cookies

set_cookies(".bing.com", {
    "_U": "cookie value"
})
set_cookies("chat.openai.com", {
    "access_token": "token value"
})
set_cookies(".google.com", {
    "__Secure-1PSID": "cookie value"
})
run_gui(host="10.10.10.136", port=80)
