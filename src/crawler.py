Run python src/crawler.py
Traceback (most recent call last):
  File "/opt/hostedtoolcache/Python/3.13.5/x64/lib/python3.13/site-packages/urllib3/connection.py", line 198, in _new_conn
    sock = connection.create_connection(
        (self._dns_host, self.port),
    ...<2 lines>...
        socket_options=self.socket_options,
    )
  File "/opt/hostedtoolcache/Python/3.13.5/x64/lib/python3.13/site-packages/urllib3/util/connection.py", line 60, in create_connection
    for res in socket.getaddrinfo(host, port, family, socket.SOCK_STREAM):
               ~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/opt/hostedtoolcache/Python/3.13.5/x64/lib/python3.13/socket.py", line 977, in getaddrinfo
    for res in _socket.getaddrinfo(host, port, family, type, proto, flags):
               ~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
socket.gaierror: [Errno -3] Temporary failure in name resolution

The above exception was the direct cause of the following exception:

Traceback (most recent call last):
  File "/opt/hostedtoolcache/Python/3.13.5/x64/lib/python3.13/site-packages/urllib3/connectionpool.py", line 787, in urlopen
    response = self._make_request(
        conn,
    ...<10 lines>...
        **response_kw,
    )
  File "/opt/hostedtoolcache/Python/3.13.5/x64/lib/python3.13/site-packages/urllib3/connectionpool.py", line 488, in _make_request
    raise new_e
  File "/opt/hostedtoolcache/Python/3.13.5/x64/lib/python3.13/site-packages/urllib3/connectionpool.py", line 464, in _make_request
    self._validate_conn(conn)
    ~~~~~~~~~~~~~~~~~~~^^^^^^
  File "/opt/hostedtoolcache/Python/3.13.5/x64/lib/python3.13/site-packages/urllib3/connectionpool.py", line 1093, in _validate_conn
    conn.connect()
    ~~~~~~~~~~~~^^
  File "/opt/hostedtoolcache/Python/3.13.5/x64/lib/python3.13/site-packages/urllib3/connection.py", line 753, in connect
    self.sock = sock = self._new_conn()
                       ~~~~~~~~~~~~~~^^
  File "/opt/hostedtoolcache/Python/3.13.5/x64/lib/python3.13/site-packages/urllib3/connection.py", line 205, in _new_conn
    raise NameResolutionError(self.host, self, e) from e
urllib3.exceptions.NameResolutionError: <urllib3.connection.HTTPSConnection object at 0x7f6435b6f0e0>: Failed to resolve 'xn--iwvq54a91czzf' ([Errno -3] Temporary failure in name resolution)

The above exception was the direct cause of the following exception:

Traceback (most recent call last):
  File "/opt/hostedtoolcache/Python/3.13.5/x64/lib/python3.13/site-packages/requests/adapters.py", line 667, in send
    resp = conn.urlopen(
        method=request.method,
    ...<9 lines>...
        chunked=chunked,
    )
  File "/opt/hostedtoolcache/Python/3.13.5/x64/lib/python3.13/site-packages/urllib3/connectionpool.py", line 841, in urlopen
    retries = retries.increment(
        method, url, error=new_e, _pool=self, _stacktrace=sys.exc_info()[2]
    )
  File "/opt/hostedtoolcache/Python/3.13.5/x64/lib/python3.13/site-packages/urllib3/util/retry.py", line 519, in increment
    raise MaxRetryError(_pool, url, reason) from reason  # type: ignore[arg-type]
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
urllib3.exceptions.MaxRetryError: HTTPSConnectionPool(host='xn--iwvq54a91czzf', port=443): Max retries exceeded with url: / (Caused by NameResolutionError("<urllib3.connection.HTTPSConnection object at 0x7f6435b6f0e0>: Failed to resolve 'xn--iwvq54a91czzf' ([Errno -3] Temporary failure in name resolution)"))

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "/home/runner/work/selfview/selfview/src/crawler.py", line 23, in <module>
    response = requests.get('https://目标网站', headers=headers)
               ~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/opt/hostedtoolcache/Python/3.13.5/x64/lib/python3.13/site-packages/requests/api.py", line 73, in get
    return request("get", url, params=params, **kwargs)
  File "/opt/hostedtoolcache/Python/3.13.5/x64/lib/python3.13/site-packages/requests/api.py", line 59, in request
    return session.request(method=method, url=url, **kwargs)
           ~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/opt/hostedtoolcache/Python/3.13.5/x64/lib/python3.13/site-packages/requests/sessions.py", line 589, in request
    resp = self.send(prep, **send_kwargs)
  File "/opt/hostedtoolcache/Python/3.13.5/x64/lib/python3.13/site-packages/requests/sessions.py", line 703, in send
    r = adapter.send(request, **kwargs)
  File "/opt/hostedtoolcache/Python/3.13.5/x64/lib/python3.13/site-packages/requests/adapters.py", line 700, in send
    raise ConnectionError(e, request=request)
requests.exceptions.ConnectionError: HTTPSConnectionPool(host='xn--iwvq54a91czzf', port=443): Max retries exceeded with url: / (Caused by NameResolutionError("<urllib3.connection.HTTPSConnection object at 0x7f6435b6f0e0>: Failed to resolve 'xn--iwvq54a91czzf' ([Errno -3] Temporary failure in name resolution)"))
Error: Process completed with exit code 1.
