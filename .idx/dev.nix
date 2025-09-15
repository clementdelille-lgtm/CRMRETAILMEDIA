# To learn more about how to use Nix to configure your environment
# see: https://firebase.google.com/docs/studio/customize-workspace
{ pkgs, ... }: {
  # Which nixpkgs channel to use.
  channel = "stable-24.05"; # or "unstable"

  # Use https://search.nixos.org/packages to find packages
  packages = [
    pkgs.python311
    pkgs.google-cloud-sdk
    pkgs.python311Packages.pylint # Ajout de pylint
    pkgs.python311Packages.streamlit
    pkgs.python311Packages.pandas
    pkgs.python311Packages.sqlalchemy
    pkgs.python311Packages.psycopg2
    pkgs.python311Packages.google-generativeai
    pkgs.python311Packages.altair
    pkgs.python311Packages.openpyxl
    pkgs.python311Packages.plotly
    pkgs.python311Packages.aiobotocore
    pkgs.python311Packages.aiohttp
    pkgs.python311Packages.aioitertools
    pkgs.python311Packages.aiosignal
    pkgs.python311Packages.alabaster
    pkgs.python311Packages.annotated-types
    pkgs.python311Packages.attrs
    pkgs.python311Packages.babel
    pkgs.python311Packages.blinker
    pkgs.python311Packages.botocore
    pkgs.python311Packages.cachetools
    pkgs.python311Packages.certifi
    pkgs.python311Packages.charset-normalizer
    pkgs.python311Packages.click
    pkgs.python311Packages.colorama
    pkgs.python311Packages.docutils
    pkgs.python311Packages.frozenlist
    pkgs.python311Packages.fsspec
    pkgs.python311Packages.gitdb
    pkgs.python311Packages.gitpython
    pkgs.python311Packages.google-api-core
    pkgs.python311Packages.google-api-python-client
    pkgs.python311Packages.google-auth
    pkgs.python311Packages.google-auth-httplib2
    pkgs.python311Packages.googleapis-common-protos
    pkgs.python311Packages.greenlet
    pkgs.python311Packages.grpcio
    pkgs.python311Packages.grpcio-status
    pkgs.python311Packages.httplib2
    pkgs.python311Packages.idna
    pkgs.python311Packages.imagesize
    pkgs.python311Packages.jinja2
    pkgs.python311Packages.jmespath
    pkgs.python311Packages.jsonschema
    pkgs.python311Packages.markupsafe
    pkgs.python311Packages.multidict
    pkgs.python311Packages.numpy
    pkgs.python311Packages.packaging
    pkgs.python311Packages.pillow
    pkgs.python311Packages.proto-plus
    pkgs.python311Packages.protobuf
    pkgs.python311Packages.pyarrow
    pkgs.python311Packages.pyasn1
    pkgs.python311Packages.pyasn1-modules
    pkgs.python311Packages.pydantic
    pkgs.python311Packages.pydantic-core
    pkgs.python311Packages.pydeck
    pkgs.python311Packages.pygments
    pkgs.python311Packages.pyparsing
    pkgs.python311Packages.python-dateutil
    pkgs.python311Packages.pytz
    pkgs.python311Packages.referencing
    pkgs.python311Packages.requests
    pkgs.python311Packages.rpds-py
    pkgs.python311Packages.rsa
    pkgs.python311Packages.s3fs
    pkgs.python311Packages.setuptools
    pkgs.python311Packages.six
    pkgs.python311Packages.smmap
    pkgs.python311Packages.snowballstemmer
    pkgs.python311Packages.sphinx
    pkgs.python311Packages.sphinxcontrib-applehelp
    pkgs.python311Packages.sphinxcontrib-devhelp
    pkgs.python311Packages.sphinxcontrib-htmlhelp
    pkgs.python311Packages.sphinxcontrib-jsmath
    pkgs.python311Packages.sphinxcontrib-qthelp
    pkgs.python311Packages.sphinxcontrib-serializinghtml
    pkgs.python311Packages.tenacity
    pkgs.python311Packages.toml
    pkgs.python311Packages.tornado
    pkgs.python311Packages.tqdm
    pkgs.python311Packages.typing-extensions
    pkgs.python311Packages.tzdata
    pkgs.python311Packages.uritemplate
    pkgs.python311Packages.urllib3
    pkgs.python311Packages.watchdog
    pkgs.python311Packages.wrapt
    pkgs.python311Packages.yarl
  ];

  # Sets environment variables in the workspace
  env = {};
  idx = {
    # Search for the extensions you want on https://open-vsx.org/ and use "publisher.id"
    extensions = [
      # "vscodevim.vim"
      "ms-python.debugpy"
      "ms-python.python"
    ];
    previews = {
      enable = true;
      previews = {
        Web = {
          manager = "web";
          command = [ "streamlit" "run" "page_01_accueil.py" "--server.port" "$PORT" "--server.headless" "true" ];
        };
      };
    };
  };
}
