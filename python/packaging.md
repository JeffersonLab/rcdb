# Packaging instructions (uv)

We use [uv](https://docs.astral.sh/uv/) for building and publishing.

TL;DR:

```bash
uv build && uv publish
```

`uv build` produces the sdist and wheel in `dist/`. `uv publish` uploads them to PyPI.

Authentication for `uv publish` (use a PyPI API token):

```bash
uv publish --token <pypi-token>
# or via environment variables
export UV_PUBLISH_TOKEN=<pypi-token>
uv publish
```

JLAB CERTIFICATE ERROR:

If you hit an SSL certificate error behind the JLab network, point uv at the JLab CA bundle:

```bash
export SSL_CERT_FILE=/home/romanov/JLabCA.crt
uv publish
```

References:

uv build: https://docs.astral.sh/uv/guides/package/

uv publish: https://docs.astral.sh/uv/guides/publish/

A tutorial:
https://packaging.python.org/tutorials/packaging-projects/

edpm pip: https://pypi.org/project/edpm/#history

SO question for JLab certificate validation
https://stackoverflow.com/questions/10667960/python-requests-throwing-sslerror/10668173
