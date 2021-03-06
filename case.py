from diy_framework import App, Router 
from diy_framework.http_utils import Response

# GET simple route
async def home(r):
	rsp = Response()
	rsp.set_header('Content-Type','text/html')
	rsp.body  = '<html><body><b>test</b></body></html>'
	return rsp
	
# GET route + params
async  def welcome(r, name):
    return "Welcome {}".format(name)

# POST route + body param
async def parse_form(r):
    if r.method == 'GET':
        return 'form'
    else:
        name = r.body.get('name','')[0]
        password = r.body.get('password','')[0]
        return "{0}:{1}".format(name,password)

# application  = router + http server
router = Router()
router.add_routes({
    r'/welome/{name}':welcome,
    r'/':home,
    r'/login': parse_form,})

app = App(router)
app.start_server()
})
