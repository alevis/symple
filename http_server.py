class HTTPConnection(object):
    def init(self, http_server, reader, writer):
        self.router = http_server.router
        self.http_parser = http_server.http_parser
        slef.loop = http_server.loop

        self._reader = reader
        self._writer = writer
        self._buffer = bytearray()
        self._conn_timeout = None
        self.request = Request()
    async def handle_request(self):
        try:
            while not self.request.finished and not self._reader.at_eof():
                data = await self._reader.read(1024)
                if data:
                    self._reset_conn_timeout()
                    await self.process_data(data)
            if self.request.finished:
                await self.reply()
            elif self._reader.at_eof():
                raise BadRequestException()
        except (NotFoundException, BadRequestException) as e:
            self.error_reply(e.code, body=Response.reason_phrase_phrases[e.code])
        except Exception as e:
            self.error_reply(500, body=Response.reason_phrases[500])
        
        self.close_connection()

    async def process_data(self, data):
        self._buffer.extend(data)
        self._buffer = self.http_parser.parse_into(
        self.request, self._buffer)
    async def reply(self):
        request = self.request
        handler = self.router.get_handler(request.path)
        response = await handler.handle(request)

        if not isinstance(response, Response):
            response = Response(code=200, body=response)
        self._writer.write(response.to_bytes())
        await self._writer.drain()
    def close_connection(self):
        self._cancel_conn_timeout()
        self._writer.close()
    def _conn_timeout_close(self):
        self.error_reply(500, 'timeout')
        self.close_connection()
    def _cancel_conn_timeout(self):
        if self._conn_timeout:
            self._conn_timeout.cancel()
    def _reset_conn_timeout(self,timeout=TIMEOUT):
        self._cancel_conn_timeout()
        self._conn_timeout = self.loop.call_later(
            timeout, self._conn_timeout_close)
    def start_server(self):
        if not self._server:
            self.loop = asyncio.get_event_loop()
            self._server = HTTPServer(self.router, self.http_parser, self.loop)
            self._connection_handler = asyncio.start_server(
                self._server.handle_connection,
                host=self.host,
                port=self.port,
                reuse_address=True,
                reuse_port=True,
                loop=self.loop)

            logger.info('Starting server on {0}:{1}'.format(
                self.host,self.port))
            self.loop.run_until_complete(self._connection_handler)
            try:
                self.loop.run_forever()
                except KeyboardInterrupt:
                    logger.info('Got signal, killing server')
                except DiyFrameworkException as e:
                    logger.error('Critical framework failure:')
                    logger.error(e.traceback)
                finally:
                    self.loop.close()
            else:
                logger.info('Server already started - {0}'.format(self))
