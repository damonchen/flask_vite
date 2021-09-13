# flask-vite

a flask pulgin for vite(vue3)


# configuration

- VITE_DEV_MODE: boolean, default: False, when True, will proxy request to vite
- VITE_DEV_SERVER_PROTOCOL: str, default: http,
- VITE_DEV_SERVER_HOST: str,default: localhost
- VITE_DEV_SERVER_PORT: int, default: 3000
- VITE_WS_CLIENT_URL: str, default: @vite/client
- VITE_ASSETS_PATH: str, default is None: vite assets path
- VITE_MANIFEST_PATH: str, for 'manifest.json' file position, which exists at dist when vite build, default is static_root or vite_assets_path when in debug mode
