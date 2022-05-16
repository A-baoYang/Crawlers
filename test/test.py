from requests_html import HTMLSession

session = HTMLSession()
r = session.get("https://www.moneydj.com/funddj/yp/yp011000.djhtm?a=ACCH38")
