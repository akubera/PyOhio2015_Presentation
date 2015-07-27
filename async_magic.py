#
# async_magic.py
#
"""
Run cell in a thread.
"""

import IPython.core.magic as ipym
import threading
import asyncio
import growler
import sys

@ipym.magics_class
class AsyncMagics(ipym.Magics):

    @ipym.cell_magic
    def run_async(self, line, cell=None):
        """
        Called when a %%run_async is found at top of ipython cell
        """
        # get an auto-timeout
        time_len = float(line) if line else 10.0
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        g = {'growler': growler, 'asyncio': asyncio, 'loop': loop}
        exec(cell, g)
        loop.close()

    @ipym.cell_magic
    def async_srv(self, line, cell=None):
        """
        Called when a %%async_thread is found at top of ipython cell
        """
        # get an auto-timeout
        time_len = float(line) if line else 10.0
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        srv = self.load_server(cell, loop)
        loop.call_later(time_len, srv.close)
        loop.call_later(time_len, loop.stop)
        loop.run_forever()
        loop.close()

    @ipym.cell_magic
    def async_thread(self, line, cell=None):
        """
        Called when a %%async_thread is found at top of ipython cell
        """
        # get an auto-timeout
        time_len = float(line) if line else 10.0

        def exec_cell():
            """
            This is within a newly created thread. Create and set a new event
            loop
            """
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            srv = self.load_server(cell, loop)
            loop.call_later(time_len, srv.close)
            loop.call_later(time_len, loop.stop)
            loop.run_forever()
            loop.close()

        thread = threading.Thread(target=exec_cell)
        thread.start()

    @staticmethod
    def load_server(code, loop):
        g = {'growler': growler, 'asyncio': asyncio, 'loop': loop}
        exec(code, g)
        try:
            srv = loop.run_until_complete(g['srv'])
        except KeyError:
            print("Cell did not create a server with name 'srv'",
                  file=sys.stderr)
            srv = None
        return srv

    @staticmethod
    def run_server_in_new_loop(code, loop):
        g = {'growler': growler, 'asyncio': asyncio, 'loop': loop}
        exec(code, g)
        try:
            srv = loop.run_until_complete(g['srv'])
        except KeyError:
            print("Cell did not create a server with name 'srv'",
                  file=sys.stderr)
            srv = None
        return srv


def load_ipython_extension(ipython):
    ipython.register_magics(AsyncMagics)
