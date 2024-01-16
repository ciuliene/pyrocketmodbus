# Useful info

## Build and Upload

To build the package:

```sh
npm run build
```

To upload the package:

```sh
npm run upload-test
```

When you are requested to enter the credentials, use the following:

```sh
Username: __token__
Password: <PyPI API TOKEN> # including 'pypi-' prefix
```

# Use the package

To install the package (it's not uploaded to the official PyPI yet, so you need to use the test PyPI.):

```sh
pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple pyrocketmodbus
```

Where:
- `--index-url` is used to install the package from the test PyPI.
- `--extra-index-url` is used to install the dependencies from the official PyPI.